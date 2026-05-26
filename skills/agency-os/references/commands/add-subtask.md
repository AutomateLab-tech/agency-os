# Command: `add-subtask <parent-id> "<title>" ...`

Create a subtask row.

1. Sync preflight.
2. Resolve `<parent-id>`. Refuse if parent's status is `Done` or `Killed`.
3. `notion-create-pages` with parent = Tasks data source. Properties: Title, Status = parent's status (`Discussion` or `To-Do` typically), Corpus = parent's corpus, Parent Task = parent, Type = `one-time`, Effort from flag or default, Dependencies from `--deps` if provided (each id resolved live via Notion; refuse if any id is unknown).
4. Append a line to the parent's Discussion log section: `### <date> — subtask added: [<title>](<url>)`.
5. Print: `+ Subtask of <parent-title>: [<title>](<url>){  deps=N}`.

Subtasks can have their own subtasks (nesting allowed; the skill doesn't enforce a depth limit but warns at depth >= 3).

See `references/structuring-work.md` for parent-vs-subtask-vs-log decision rules.
