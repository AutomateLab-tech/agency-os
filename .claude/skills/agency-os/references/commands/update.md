# Command: `update <id> ...`

Mutate properties without changing status. All flags optional. Print: `Updated: [<title>](<url>)`.

`--notes "..."` replaces the Description toggle body. To **append** without replacing, use `log` instead.

`--deps=<id1>,<id2>,...` replaces the Dependencies relation (each id resolved live via Notion; refuse if any is unknown). `--deps=none` clears it. Self-reference and cycles are refused.

`--parent=<id>` reparents the task under `<id>` (resolved live; refuse if unknown, Done, or Killed; refuse self-reference and cycles). `--parent=none` removes the parent and promotes the row to top-level. Use cases: regrouping flat tasks under a newly created container, demoting a misplaced subtask back to root, swapping a task between umbrella initiatives.
