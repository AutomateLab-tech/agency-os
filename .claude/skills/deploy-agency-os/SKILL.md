---
name: deploy-agency-os
description: "End-to-end deploy for the agency-os git repo (https://github.com/ratamaha-git/agency-os). Single command: drains Claude worktrees, stages + commits + pushes any local changes to origin/main. User does NOT commit or push manually — this skill owns the whole pipeline. Re-runnable and idempotent. Trigger when the user says: 'deploy agency-os', 'push agency-os', 'sync agency-os to GitHub', 'ship changes', or after any local change to repo files."
type: workflow
---

# deploy-agency-os — sync local → GitHub

End-to-end push of `C:\Work\agency-os` to `https://github.com/ratamaha-git/agency-os`. Drains any open Claude worktrees, commits everything on `main`, and pushes. No server-side steps — this is a pure GitHub repo.

**Single source of truth:** `origin/main` on GitHub. Every deploy is `git push`. The only files not in git are ephemeral session state (`.claude/worktrees/`, `tmp/`).

---

## Execution model — delegate to Haiku

This skill is mechanical: git commands, status checks. **Run it on Haiku via a subagent.**

When `/deploy-agency-os` is invoked, the orchestrator's only job is to dispatch:

```
Agent({
  description: "Deploy agency-os to GitHub",
  subagent_type: "general-purpose",
  model: "haiku",
  prompt: "Run the deploy-agency-os skill end-to-end. Read C:\\Work\\agency-os\\.claude\\skills\\deploy-agency-os\\SKILL.md and follow Steps 1 → 3. Execute every git command exactly as written from C:\\Work\\agency-os; verify after each step; if a verification fails, stop and report. Final response: git SHA pushed, commit message used, and anything that needed user attention."
})
```

After the subagent returns, the orchestrator passes the report through verbatim. Do **not** re-run any step yourself.

The remainder of this document is written for the Haiku subagent.

---

## Step 1 — Preflight

Verify HEAD is `main`. If it is not, **stop and report** — deploying from a feature branch would push the wrong commits.

```bash
cd /c/Work/agency-os
git rev-parse --abbrev-ref HEAD   # must print: main
git status
```

---

## Step 2 — Drain worktrees, merge, commit, push

Single-person workflow. Whatever exists locally at deploy time is what ships. In-flight Claude Code worktrees are the most common source of drift — this step commits and merges them before pushing.

```bash
cd /c/Work/agency-os
MAIN=/c/Work/agency-os

# 2a — Drain every worktree under .claude/worktrees/
git -C "$MAIN" worktree list --porcelain | awk '/^worktree / {print $2}' | while IFS= read -r WT; do
  case "$WT" in
    "$MAIN") continue ;;
    "$MAIN/.claude/worktrees/"*) ;;
    *) continue ;;
  esac
  if ! git -C "$WT" diff --quiet \
     || ! git -C "$WT" diff --cached --quiet \
     || [ -n "$(git -C "$WT" ls-files --others --exclude-standard)" ]; then
    WT_NAME=$(basename "$WT")
    echo "[drain] committing wip in $WT_NAME"
    git -C "$WT" add -A || { echo "[drain] add failed in $WT_NAME — skipping"; continue; }
    git -C "$WT" commit -m "wip($WT_NAME): drain by /deploy-agency-os" \
      || echo "[drain] commit failed in $WT_NAME — skipping"
  fi
done

# 2b — Merge every claude/* branch into main. Abort on first conflict.
for BR in $(git -C "$MAIN" for-each-ref --format='%(refname:short)' refs/heads/claude/); do
  if git -C "$MAIN" merge-base --is-ancestor "$BR" HEAD; then
    continue
  fi
  echo "[merge] $BR -> main"
  if ! git -C "$MAIN" merge --no-edit -m "merge $BR into main for deploy" "$BR"; then
    git -C "$MAIN" merge --abort
    echo "STOP: conflict merging $BR into main." >&2
    echo "Resolve the conflict, drop $BR if obsolete, then re-run /deploy-agency-os." >&2
    exit 1
  fi
done

# 2c — Stage anything dirty in main, commit, push.
git add -A
if ! git diff --cached --quiet; then
  git commit -m "deploy: sync local changes"
fi
git push
```

Notes:
- Auto-commit messages are generic on purpose. For a meaningful message, commit manually before invoking `/deploy-agency-os`.
- File-lock drain failures are common on Windows when an old session still holds a worktree. The loop continues so deploy isn't blocked, but that worktree's WIP won't merge until the lock is released.
- If `git push` fails (auth, non-fast-forward, network), **stop and report**.

---

## Step 3 — Report

Final response:

- Git SHA pushed (`git rev-parse --short HEAD`).
- Commit message used (or "nothing to commit — already up to date").
- Anything that needed user attention (merge conflicts, drain failures, push failures).

---

## Failure modes

| Symptom | Fix |
|---|---|
| HEAD is not `main` | Checkout main, resolve, re-run. |
| Merge conflict on a `claude/*` branch | Resolve the conflict manually, drop the branch if obsolete, re-run. |
| `git push` fails with non-fast-forward | Someone pushed to `origin/main` separately. Pull first (`git pull --rebase`), then re-run. |
| `git push` fails with auth error | Check SSH key or HTTPS credential; re-run after fixing. |
