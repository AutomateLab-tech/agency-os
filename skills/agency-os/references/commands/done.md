# Command: `done <id>`

Close a task. Branches on `Type`.

1. Sync preflight.
2. Resolve `<id>` against rows in `In Progress` (preferred) or `To-Do` (allowed).
3. **If `Type == "one-time"`:**
   - Status -> Done; Done At -> today; Result Link -> `--result-link` if given.
   - Append `### <date>: done — <note or "(no note)">` to the Done log.
   - For subtasks: if **all** siblings are now `Done`, surface a nudge: `note: all subtasks of <parent> are done — consider /agency-os done <parent>`.
4. **If `Type == "recurring"`:**
   - Status -> To-Do (loops back).
   - Last Done -> today.
   - Append `### <date>: done — <note>` to the Done log.
5. Print: `Done: [<title>](<result-link>)` (if no result-link, omit the link and print title as plain text).
