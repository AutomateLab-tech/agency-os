# Command: `approve <id>`

Promote a task from Discussion -> To-Do, cascading active children. **Requires explicit user authorization for the specific row or batch** (see "Authorization gates" in SKILL.md) — `approve` is a Gate-1 transition, never run it on the orchestrator's initiative.

1. Sync preflight.
2. Resolve `<id>`. Verify status is `Discussion` (or `Suggestion` — fast-track allowed). Refuse otherwise.
3. **Cascade**: collect every descendant with status in `{Suggestion, Discussion}`. For each, set Status -> To-Do.
4. Set the parent's Status -> To-Do. If `--priority` provided, set on the parent only.
5. Append a `### <date> — approved` entry to the parent's Discussion log.
6. Print: `-> To-Do: [<title>](<url>)  (cascaded N subtasks)`.
