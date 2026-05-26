# Command: `suggest "<title>" ...`

Add a row in `Suggestion` status. **Structure check runs inside `suggest`** — the subagent enforces it, not just the orchestrator. The orchestrator decides the shape (which parent, whether a container is needed); `suggest` verifies that decision was made rather than silently creating a root-level row.

1. **Structure preflight (skip only when `--parent` is provided or `--force-top-level` is passed).**
   - Read `state/task-tree.json` for the active task tree. If the file is absent, it will be built as a side-effect of the sync preflight in step 2 — proceed.
   - Scan In-Progress and To-Do **top-level** rows for an obvious umbrella. "Obvious" = the candidate's title or corpus clearly covers the work being suggested (confidence >= 80%).
   - If one candidate: `Candidate parent: [<title>](<url>) — attach as subtask? Reply with --parent=<id> to confirm, or --force-top-level to create at root.` **Stop and wait** for the orchestrator to relay the answer. Do not create the row until confirmed.
   - If multiple candidates: list all, wait.
   - If no candidate: proceed silently.
2. Sync preflight.
3. Validate: `--corpus` is in pointers (else list and refuse); if `--type=recurring`, `--cadence` is required. If `--parent=<id>` is provided, resolve it live and refuse if unknown, Done, or Killed; refuse self-reference and cycles.
4. **Dedup check**: refuse if Title-Jaccard >= 0.8 against any row with status in `{Suggestion, Discussion, To-Do, In Progress}`.
5. `notion-create-pages` with parent = Tasks data source. Properties: Title, Status=Suggestion, Corpus, Type, Cadence (if recurring), Effort. If `--parent=<id>` provided, also set Parent Task to that id and inherit Corpus from the parent unless `--corpus` was explicitly passed. Page body = `task-page-template.md` rendered.
6. If `--notes` provided, write into the Description section.
7. **Update tree snapshot**: append the new row to `state/task-tree.json` so the snapshot stays current without a full re-fetch.
8. Print: `+ Suggestion: [<title>](<url>){  parent=<parent-title>}`.

`--parent` makes `suggest` the canonical way to create a row under any existing task. `add-subtask` remains a convenience for the in-discussion flow (it inherits parent's status; `suggest --parent` always lands in Suggestion). `--force-top-level` is the explicit override when a root-level task is genuinely unrelated to any active initiative — it skips the structure preflight without a prompt.

See `references/structuring-work.md` for the parent-vs-subtask-vs-log decision rules and the structure preflight protocol.
