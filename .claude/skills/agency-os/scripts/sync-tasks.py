#!/usr/bin/env python3
"""
Incremental delta sync between the Notion Tasks DB and the local mirror
at state/tasks.json. The mirror is the brief-ready primary read source for
every al-notion command; live notion-fetch is only used as an escape hatch.

Strategy:
  1. Load existing mirror if present; read its synced_at timestamp.
  2. Query the Notion data source with a last_edited_time > synced_at filter
     (full bootstrap when no prior mirror exists or --full is passed).
  3. For each changed page, fetch block children once and parse the three
     toggleable H2 sections (Description, Discussion log, Done log) into
     compact brief-ready fields.
  4. Upsert rows into the mirror; drop rows whose status moved to a state
     the mirror no longer tracks (none today — we keep terminal rows too,
     since `done`/`list done` reads them).
  5. Bump synced_at to the most recent last_edited_time seen.

Reads NOTION_KEY from .env (same precedent as query-tasks.py). No external
deps; urllib only.

Usage:
  python .claude/skills/al-notion/scripts/sync-tasks.py            # delta
  python .claude/skills/al-notion/scripts/sync-tasks.py --full     # rebuild
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

NOTION_API_VERSION = "2025-09-03"
REPO_ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = Path(__file__).resolve().parents[1]
POINTERS = SKILL_DIR / "references" / "notion-pointers.json"
MIRROR = SKILL_DIR / "state" / "tasks.json"
ENV_FILE = REPO_ROOT / ".env"


def load_env_var(name: str) -> str:
    val = os.environ.get(name)
    if val:
        return val
    if not ENV_FILE.exists():
        sys.exit(f"error: {name} not in environment and {ENV_FILE} not found")
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == name:
            return v.strip().strip('"').strip("'")
    sys.exit(f"error: {name} not found in {ENV_FILE}")


def notion_request(method: str, path: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    last_err: str | None = None
    for attempt in range(5):
        req = urllib.request.Request(
            f"https://api.notion.com{path}",
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": NOTION_API_VERSION,
                "Content-Type": "application/json",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            last_err = f"HTTP {e.code} on {method} {path}\n{body_text}"
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(1.5 * (attempt + 1))
                continue
            sys.exit(f"error: Notion API {last_err}")
        except urllib.error.URLError as e:
            last_err = f"URLError on {method} {path}: {e.reason}"
            time.sleep(1.5 * (attempt + 1))
            continue
    sys.exit(f"error: Notion API {last_err} (after retries)")


def prop_select(props: dict, name: str) -> str | None:
    p = props.get(name) or {}
    sel = p.get("select") or {}
    return sel.get("name")


def prop_status(props: dict, name: str) -> str | None:
    p = props.get(name) or {}
    st = p.get("status") or {}
    return st.get("name")


def prop_title(props: dict, name: str) -> str:
    p = props.get(name) or {}
    title = p.get("title") or []
    return "".join(t.get("plain_text", "") for t in title).strip()


def prop_date(props: dict, name: str) -> str | None:
    p = props.get(name) or {}
    d = p.get("date") or {}
    return d.get("start")


def prop_url(props: dict, name: str) -> str | None:
    p = props.get(name) or {}
    return p.get("url")


def prop_relation_ids(props: dict, name: str) -> list[str]:
    p = props.get(name) or {}
    rel = p.get("relation") or []
    return [r.get("id") for r in rel if r.get("id")]


def prop_multi_select(props: dict, name: str) -> list[str]:
    p = props.get(name) or {}
    ms = p.get("multi_select") or []
    return [m.get("name") for m in ms if m.get("name")]


def prop_rich_text(props: dict, name: str) -> str:
    p = props.get(name) or {}
    rt = p.get("rich_text") or []
    return "".join(r.get("plain_text", "") for r in rt).strip()


def prop_unique_id(props: dict, name: str) -> str | None:
    p = props.get(name) or {}
    uid = p.get("unique_id") or {}
    prefix = uid.get("prefix")
    number = uid.get("number")
    if number is None:
        return None
    return f"{prefix}-{number}" if prefix else str(number)


def block_text(blk: dict) -> str:
    t = blk.get("type")
    if not t:
        return ""
    inner = blk.get(t, {}) or {}
    rt = inner.get("rich_text") or []
    return "".join(r.get("plain_text", "") for r in rt)


def fetch_block_children(page_id: str, token: str) -> list[dict]:
    blocks: list[dict] = []
    cursor: str | None = None
    while True:
        path = f"/v1/blocks/{page_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        data = notion_request("GET", path, token)
        blocks.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return blocks


def parse_sections(blocks: list[dict]) -> dict:
    """Split block children into the three toggleable H2 sections we care about.
    Returns: {description, latest_discussion_entry, last_done_log_entry}.
    Discussion / Done logs use h3 entry headings (e.g. '### 2026-05-12 — ...');
    we grab the most recent one (last in document order)."""
    section: str | None = None
    sections: dict[str, list[str]] = {"description": [], "discussion": [], "done": []}
    for blk in blocks:
        t = blk.get("type")
        if t == "heading_2":
            text = block_text(blk).strip().lower()
            if text.startswith("description"):
                section = "description"
                continue
            if text.startswith("discussion"):
                section = "discussion"
                continue
            if text.startswith("done log"):
                section = "done"
                continue
            section = None
            continue
        if section is None:
            continue
        text = block_text(blk).strip()
        if text:
            sections[section].append(text)

    def last_entry(lines: list[str]) -> str:
        """Take the last '###'-prefixed chunk; otherwise the tail."""
        if not lines:
            return ""
        last_idx = 0
        for i, ln in enumerate(lines):
            if ln.startswith("### "):
                last_idx = i
        chunk = " ".join(lines[last_idx:])
        return chunk[:600]

    return {
        "description": " ".join(sections["description"])[:600],
        "latest_discussion_entry": last_entry(sections["discussion"]),
        "last_done_log_entry": last_entry(sections["done"]),
    }


def serialize_row(row: dict, token: str) -> dict:
    props = row.get("properties", {})
    page_id = row["id"]
    body = parse_sections(fetch_block_children(page_id, token))
    return {
        "notion_id": page_id,
        "task_id": prop_unique_id(props, "Task ID"),
        "url": row.get("url"),
        "title": prop_title(props, "Title"),
        "status": prop_status(props, "Status") or prop_select(props, "Status"),
        "type": prop_select(props, "Type"),
        "cadence": prop_select(props, "Cadence"),
        "corpus": prop_select(props, "Corpus"),
        "priority": prop_select(props, "Priority"),
        "impact": prop_select(props, "Impact"),
        "effort": prop_select(props, "Effort"),
        "exec": prop_select(props, "Exec"),
        "tags": prop_multi_select(props, "Tags"),
        "parent_task_id": (prop_relation_ids(props, "Parent Task") or [None])[0],
        "dependency_ids": prop_relation_ids(props, "Dependencies"),
        "last_done": prop_date(props, "Last Done"),
        "done_at": prop_date(props, "Done At"),
        "result_link": prop_url(props, "Result Link"),
        "created_time": row.get("created_time"),
        "last_edited_time": row.get("last_edited_time"),
        "description": body["description"],
        "latest_discussion_entry": body["latest_discussion_entry"],
        "last_done_log_entry": body["last_done_log_entry"],
    }


def query_changed(data_source_id: str, token: str, since: str | None) -> list[dict]:
    body: dict = {"page_size": 100}
    if since:
        body["filter"] = {
            "timestamp": "last_edited_time",
            "last_edited_time": {"on_or_after": since},
        }
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        if cursor:
            body["start_cursor"] = cursor
        page = notion_request(
            "POST", f"/v1/data_sources/{data_source_id}/query", token, body
        )
        rows.extend(page.get("results", []))
        if not page.get("has_more"):
            break
        cursor = page.get("next_cursor")
    return rows


def main() -> int:
    full = "--full" in sys.argv[1:]
    token = load_env_var("NOTION_KEY")
    pointers = json.loads(POINTERS.read_text(encoding="utf-8"))
    data_source_id = pointers["tasks_database"]["data_source_id"]

    existing: dict = {}
    since: str | None = None
    if MIRROR.exists() and not full:
        existing = json.loads(MIRROR.read_text(encoding="utf-8"))
        since = existing.get("synced_at")

    rows = query_changed(data_source_id, token, since)
    by_id: dict[str, dict] = {t["notion_id"]: t for t in existing.get("tasks", [])}

    new_synced_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )
    changed = 0
    for r in rows:
        # Skip rows that weren't actually edited after `since` — Notion's
        # on_or_after is inclusive and can re-return the boundary row.
        if since and r.get("last_edited_time") and r["last_edited_time"] < since:
            continue
        by_id[r["id"]] = serialize_row(r, token)
        changed += 1

    payload = {
        "synced_at": new_synced_at,
        "previous_synced_at": existing.get("synced_at"),
        "tasks": list(by_id.values()),
    }
    MIRROR.parent.mkdir(parents=True, exist_ok=True)
    MIRROR.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    total = len(payload["tasks"])
    mode = "full bootstrap" if full or not since else f"delta since {since}"
    print(f"sync: {mode} -> {changed} changed, {total} total -> state/tasks.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
