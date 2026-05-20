# Command: `kill <id> [--reason "..."]`

Terminal drop.

1. Sync preflight.
2. Resolve `<id>` against any non-terminal row.
3. Status -> Killed. Append `### <date>: killed — <reason>` to the Done log.
4. **Cascade**: for every descendant in non-terminal status, also set Status -> Killed with reason `parent killed`.
5. Print: `Killed: [<title>](<url>)  ({<reason>})  (cascaded N descendants)`.
