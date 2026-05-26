# Command: `show <id> [--section ...] [--entry <date>]`

Read a task's content without mutating state. Always include a `[<title>](<url>)` link at the top of the output before showing the requested content.

- Default: row properties + Description + subtask titles.
- `--section description`: Description only.
- `--section discussion [--entry <date>]`: discussion log; one specific entry if `--entry` given.
- `--section donelog`: done log entries.
- `--section all`: everything (full page body + subtask titles).
