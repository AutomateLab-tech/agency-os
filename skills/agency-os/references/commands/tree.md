# Command: `tree [--depth N] [--corpus=<s>] [--status=<s>]`

Emit a compact indented view of the active task hierarchy and refresh `state/task-tree.json`. This is the primary tool for understanding the board's shape before adding new work.

Default scope: all non-terminal rows (Suggestion, Discussion, To-Do, In Progress). `--status` filters to a specific status. `--corpus` narrows to one corpus. `--depth N` truncates at N levels (default: unlimited).

1. Sync preflight (this also writes `task-tree.json` as a side-effect — see Sync section in SKILL.md).
2. Build the tree from the live result: group rows by `Parent Task`, render depth-indented.
3. Output as plain markdown (links clickable, not a fenced block):

   ```
   [OS-12](url) "Top-level initiative"  [In Progress · General · L]
     [OS-13](url) "Container subtask"  [To-Do · M]
       [OS-14](url) "Leaf work item"  [To-Do · S]
     [OS-15](url) "Another subtask"  [Suggestion · M]
   [OS-16](url) "Unrelated top-level"  [To-Do · Recurring · M]
   ```

4. After the tree, print a one-line summary: `<N> tasks across <K> top-level roots  (snapshot written to state/task-tree.json)`.

**When to call `tree`:**
- At the start of any session where you'll be adding or reorganizing tasks.
- Before any batch `suggest` operation, if `state/task-tree.json` is absent or you're unsure of the current shape.
- Whenever the user asks "what's the structure", "show me the hierarchy", "how is this organized".

`tree` is a read-only command — it never mutates Notion, only refreshes the local snapshot.
