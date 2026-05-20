# Command: `log <id> "<entry>"`

Append a discussion entry to the task page.

1. Sync preflight.
2. Resolve `<id>`.
3. Find or create the `Discussion log` toggle on the page. Append a new dated entry:
   ```
   ### <YYYY-MM-DD> — <auto-summary first 6 words of entry>
   <entry>
   ```
4. Print: `+ Logged: [<title>](<url>)`.
5. If the entry contains lines starting with `+` they're treated as proposed subtasks and surfaced in the output: `note: detected N proposed subtasks; create with /agency-os add-subtask <id> "<title>"`.

The agent should call `log` multiple times during a discussion — once per Q/A round, or once per cohesive thought — rather than dumping a single megalogue at the end. This keeps the log queryable by date.
