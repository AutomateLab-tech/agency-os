# Command: `next [N] [--corpus=<s>]`

Show top N (default 3) To-Do tasks. **Does not execute.**

1. Sync preflight.
2. Filter: `Status == "To-Do"` and (if `--corpus` given) matching corpus and **`Parent Task IS NULL`** (only top-level).
3. Sort by Priority (1 first; unset last), then Type (recurring with overdue Last Done first), then Created ascending.
4. Print N rows: `<idx>. [<priority>][<corpus>][<type>{<cadence>}][<effort>]  [<title>](<url>)  (/agency-os start <id>)`.

For recurring tasks, "overdue" = `now - Last Done` exceeds the cadence interval (daily=1d, weekly=7d, biweekly=14d, monthly=30d, quarterly=90d, yearly=365d).
