# Command: `scaffold [--parent=<id-or-url>] [--corpora="<n1>,<n2>,..."]`

**The single-shot setup command.** Builds the entire Notion workspace from scratch — Hub page, Tasks database with the full schema below, General Guidance page, Resources page, default corpus pages (`General`, `Recurring`), and every linked DB view. There is no public Notion template to duplicate; this command IS the setup. The integration only needs to be shared with the parent (workspace root or `--parent` page) before running.

Idempotent: if `notion-pointers.json` exists and every ID resolves via `notion-fetch`, prints `scaffold: already in place` and exits. Otherwise creates only what's missing.

1. **Locate or create the Hub**. If `--parent=<page-id-or-url>` is passed, create the Hub as a child of that page (use this when the integration is shared with a specific page rather than the workspace root). Otherwise: search by title at workspace root; create there if absent. If the create fails because the integration lacks workspace-root access, abort with `scaffold: integration must be shared with the workspace root, or pass --parent=<page-id>`.
2. **Create the Tasks database** as a child of the Hub, with the schema in SKILL.md. Capture both `database_id` and `data_source_id`. The `Dependencies` property is a self-relation on Tasks (separate from `Parent Task` — that's the hierarchy relation; `Dependencies` is the gating relation used only by `run`).
3. **Create the General Guidance page** under the Hub; seed body from `references/general-guidance.md`.
4. **Create each Corpus page** under the Hub. Default set: `General`, `Recurring` (user can customise via `--corpora` flag or add later with `add-corpus`). Seed each from `references/corpus-template.md`.
5. **Create the Resources page** under the Hub; seed from `references/resources.md` if present.
6. **Add linked DB views** to the Hub for Suggestions Inbox, In Discussion, To-Do, Recurring, In Progress, Recently Done. Add a per-corpus filtered view to each Corpus page. Every view's SHOW clause must include `Task ID` as the leftmost column so subtask IDs are reachable at a glance.
7. **Wire interlinks** (Hub <-> Guidance <-> Corpora <-> Resources).
8. **Write `notion-pointers.json`**.
9. **Full-width pages — manual one-time toggle.** The Notion MCP doesn't expose `page_full_width`, so Hub / Guidance / Resources / each Corpus page / new task pages need the ... menu -> "Full width" toggle flipped on by the operator after creation. Surface this in scaffold's final output so the operator knows to do it.
10. **Sub-items — manual one-time toggle.** The Notion MCP doesn't expose the Sub-items setting either. On the Tasks DB, the operator must enable Sub-items and wire it to the existing `Parent Task` (parent) / `Subtasks` (children) relation. Path varies by Notion version: typically `...` menu -> "Sub-items" -> pick `Parent Task`. Once wired, every view in the Hub gets a chevron on rows with children.
11. **Print** the Hub URL.

`add-corpus "<name>"` extends the General Plan post-scaffold: appends a `Corpus` select option, creates the page, adds the filtered view, updates pointers. Print: `+ Corpus: [<name>](<url>)`.
