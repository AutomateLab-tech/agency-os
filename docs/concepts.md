# Concepts

How agency-os thinks about work, state, and the boundary between repo and Notion.

---

## Hybrid contract: what lives where

agency-os splits state across two places. Getting this wrong costs tokens and causes drift.

**In the repo (source of truth):**
- All skill specs under `.claude/skills/` - the executable logic
- All docs under `docs/` - the human-readable map
- `references/notion-pointers.json` - the IDs that bind the repo to the Notion workspace
- `references/general-guidance.md` - the canonical General Guidance text (Notion's page is a one-way mirror of this file)

Agents read these off disk - fast, free, greppable, diffable. Git history makes them auditable.

**In Notion (source of truth):**
- Task rows: Title, Status, Corpus, Priority, Impact, Effort, Type, Cadence, Parent Task, Dependencies, Tags
- Discussion logs (per task page)
- Done logs (per task page)
- Corpus pages: Goal + local guidance authored by the operator
- The Hub and its linked DB views

Anything the operator wants to review in-place, anything that changes frequently, anything that doesn't benefit from `git log`.

**One-way mirror only.**

`references/general-guidance.md` -> Notion General Guidance page. Edit the local file, then push to Notion (via `scaffold` or a manual `notion-update-page` call). Never edit the Notion page and try to pull it back; drift will follow.

The task cache (`references/notion-cache.json`) is gitignored - it's a throwaway snapshot regenerated on every sync. The pointer file (`notion-pointers.json`) is the only Notion binding that gets committed.

---

## Status flow

```
Suggestion --discuss--> Discussion --approve--> To-Do --start--> In Progress --done--> Done
                                                                               |
any --kill--> Killed (terminal)                                                |
                                                                               |
                     Recurring: done logs an occurrence and loops to To-Do ---+
```

| Status | Meaning | Set by |
|---|---|---|
| Suggestion | Idea in the inbox, not yet discussed | `suggest`, or manual Notion add |
| Discussion | Under clarification; subtasks may be emerging | `discuss` |
| To-Do | Approved scope; scheduled to execute | `approve`, or recurring loop on `done` |
| In Progress | An agent (or operator) is actively working it | `start` |
| Done | Closed (one-time tasks only) | `done` when Type=one-time |
| Killed | Intentionally dropped, archival | `kill` |

**Dedup gate on suggest.** Before creating a new task, `suggest` checks for Title-Jaccard similarity >= 0.8 against any non-terminal row (Suggestion, Discussion, To-Do, In Progress). A near-duplicate refuses loudly - the operator either approves the similar existing task or kills it before filing a variant.

**Stale In Progress.** If `start` crashes mid-execution, the row sits at In Progress. Manual recovery: `/agency-os move <id> --to todo`, then restart. The `status` command flags rows that have been In Progress for more than 7 days.

---

## Subtasks vs steps vs log entries

The hardest call in using this board well is deciding what shape a piece of work takes.

**A task** has a clear "done" state. It can be shipped, merged, published, decided. "Set up Yandex Webmaster" is a task. "Think about SEO" is not - it has no done state.

**A subtask** is a child task that can be completed independently and is bounded by a deliverable. "Write the Capterra blurb" is a subtask of "Capterra directory submission" because the blurb is a separable artifact with its own done. "Click submit on the form" is not a subtask - do it inline and mention it in the done note.

Rule of thumb: if you'd hand it to a different agent on a different day, it's a subtask. If you'd do it in the same session, it's a step.

**A log entry** is a decision, clarification, or update on existing scope. "Decided to use 300-char description" is a log entry. "Operator handles the comments thread" is a log entry, not a subtask.

### Depth guide

| Depth | When to use |
|---|---|
| Top-level | Standalone work, or a container for a multi-deliverable project |
| Subtask (depth 1) | Normal case - most subtasks live here |
| Nested subtask (depth 2) | Parent has multiple major deliverables each with their own breakdown |
| Depth 3+ | Warning raised. Almost always a sign the hierarchy should be flattened |

### Containers

A top-level task with subtasks is a container. Containers are skipped by `run` - their work IS their subtasks. The container flips to In Progress automatically when its first subtask starts (parent-cascade rule). It stays In Progress until the operator explicitly closes it with `done`.

---

## Dependencies and waves

Tasks can depend on other tasks. The `Dependencies` relation on a task row holds a list of task IDs that must reach `Done` before this task is dispatchable.

`run` resolves dependencies into a staged execution plan:

1. Tasks with no unmet dependencies are stage 1.
2. Tasks whose only unmet dependencies are in stage 1 are stage 2.
3. And so on (topological sort).

Within each stage, tasks run in parallel. The next stage starts only when all tasks in the current stage reach a terminal state (Done, blocked-operator, needs-clarification, or failed).

If a dependency isn't in the current run batch and isn't already Done, the dependent task is classified as `blocked-deps` and reported but not dispatched.

Dependencies are invisible to `start`, `next`, and `list` - they only matter to `run`. An operator can always `start` a task manually regardless of its dependencies.

---

## Exec gate and model picker

`Exec` is a three-value field set by the operator on each task row:

| Value | Meaning |
|---|---|
| `none` (default) | Not yet decided - stays out of the agent queue |
| `Agent` | Safe for autonomous execution - enters `run` queue |
| `Human` | Requires a person - flagged in the board, never dispatched |

Only rows with `Exec=Agent` AND `Status=To-Do` appear in the `run` queue. This is the operator's primary control surface.

The model picker runs at dispatch time (not pre-tagged on the row):

- **Haiku** - mechanical, template-driven, single-skill. Form filings, directory submissions, recurring log-and-close tasks, anything that's "fill a template and submit."
- **Sonnet** (default) - substantive content, judgment-bearing audits, multi-step drafts, anything that needs a draft + revision pass.
- **Opus** - strategic design, multi-skill orchestration, hard reasoning. Rare; reserve for tasks that genuinely need it.

Token spend scales with task complexity, not workflow size.

---

## Corpora and the Hub

The Hub is the top-level Notion page. It contains:
- An intro block
- The General Guidance page (linked)
- A General Plan table listing corpora
- Linked DB views: Suggestions Inbox, In Discussion, To-Do, Recurring, In Progress, Recently Done
- The Resources page (linked)

Each **corpus page** scopes a domain of work. It has a Goal section, a Local guidance section (authored by the operator - conventions, links, contacts), and a linked DB view filtered to tasks in that corpus.

When a task brief is assembled by `start`, it pulls corpus Goal + Local guidance directly into the brief so the executing agent has context without needing to navigate Notion manually.

Corpora are created at scaffold time (`General` and `Recurring` by default) or added later with `/agency-os add-corpus`. They're cheap to add and there's no overhead to having many.
