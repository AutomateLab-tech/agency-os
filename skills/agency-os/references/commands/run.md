# Command: `run [--go]`

Batch-execute every task in `state/todo-ids.json` (which only contains rows with `Status == "To-Do"` AND `Exec == "Agent"`).

**Claude Code:** The Haiku subagent builds the plan from the sidecar; the orchestrator picks a model per task at runtime and spawns execution agents.

**Non-Claude harnesses:** The skill reads `config.json` to determine available models. If `config.json` doesn't exist, run `/agency-os init` first.

**Auto-refresh.** `run` always calls `refresh` as its first step. If `refresh` fails, `run` aborts.

## Plan phase (Haiku subagent)

1. **Execute `scripts/query-tasks.py` via Bash** — this is mandatory and must happen before reading anything. Run `python .claude/skills/agency-os/scripts/query-tasks.py` and verify it exits 0. Only then read the freshly written `state/todo-ids.json`. Never read the sidecar without running the script first; the file on disk is always stale.
2. **Dedup containers.** For each row with `has_todo_subtasks: true`, skip the parent — its work IS its subtasks.
3. **Resolve dependencies.** Each sidecar row carries `dependencies: [{id, status}]`. For every dep:
   - `status == "Done"` -> satisfied, ignore.
   - dep `id` is in the current in-batch set -> record as an **intra-batch** edge.
   - otherwise -> **external blocker**: drop from dispatch plan, collect into `blocked_deps[]`.
4. **Topological stage assignment.** Build a DAG from intra-batch edges; assign each task a stage = `1 + max(stage of its in-batch deps)` (stage 1 = no in-batch deps). If a cycle is detected, abort.
5. Sort within each stage: Priority asc, then overdue-recurring first, then Effort asc.
6. Return the plan to the orchestrator as `stages: [[(id, title, corpus, effort, parent_id, description_preview), ...], ...]` plus `blocked_deps`.

## Dispatch phase (orchestrator)

**Before spawning any execution agent**, the orchestrator prints the plan outline (see `### Output` below) so the user sees which tasks are about to fire, in which stages, with which model per task. Then `dispatching stage 1...` and dispatch begins.

Stages run **sequentially**: every task in stage N must finish before stage N+1 starts. Within a stage, tasks fan out in parallel.

If any task in stage N closes as not Done, stage N+1 tasks that depend on it are dropped; added to the run summary's `blocked-deps`. Stage N+1 tasks whose deps all closed Done still run.

**Claude Code:** The orchestrator picks a model and spawns an execution agent per task.

**Non-Claude harnesses:** The skill reads `config.json` to determine which models are available, then suggests a complexity level (easy/med/hard) for each task based on the same heuristic.

Picker heuristic (same on all harnesses):

- **Haiku (easy)** — mechanical, template-driven, single-skill: form filings, recurring routines, log-and-close mutations, anything that's "fill a form / file a PR / post a comment from a known template."
- **Sonnet (medium, default)** — substantive content/comms work, judgment-bearing audits, multi-step drafting, anything that needs a draft + revision pass.
- **Opus (hard)** — strategic design, multi-skill orchestration, hard reasoning. Rare.

Cap concurrency at **5** parallel execution agents **per stage**.

## Execution-agent contract

**Status discipline is non-negotiable.** Every spawned agent MUST leave the row in a terminal-for-this-run state before returning. No exceptions, no "leave it at In Progress for the operator to see":

| Outcome | Final Status | Closer command |
|---|---|---|
| Full completion | `Done` (one-time) / `To-Do` w/ Last Done bumped (recurring) | `/agency-os done <id> --result-link <url> --note "..."` |
| Partial completion | `Discussion` | `/agency-os move <id> --to discussion` + `/agency-os log <id> "partial: <what's left>"` |
| Blocked on operator action | `Discussion` | `/agency-os move <id> --to discussion` + `/agency-os log <id> "blocked-operator: <what operator must do>"` |
| Needs clarification | `Discussion` | `/agency-os move <id> --to discussion` + `/agency-os log <id> "needs-clarification: <question>"` |
| Failed (crash, tool error, dead-end) | `Discussion` | `/agency-os move <id> --to discussion` + `/agency-os log <id> "failed: <what broke>"` |

Rationale: leaving a row at `In Progress` after the agent has stopped working is a lie about live state. The dashboard ends up cluttered with rows nothing is actually working on, and the next `run` can't tell whether to retry. `Discussion` is the correct holding pen for "an agent looked at this and could not close it" — the operator sees a real queue of things needing attention, and a follow-up `/agency-os approve <id>` is the explicit "try again" signal.

Every spawned agent:

1. Calls `/agency-os start <id>` to load the kickoff brief AND flip the row To-Do -> In Progress. This MUST be the first call; if the row is already In Progress (re-dispatch), `start` is idempotent and re-emits the brief.
2. **Runnability check:** can this task plausibly be completed end-to-end by an agent, or does it require operator action (logging into a personal account, solving a captcha, clicking publish in a UI without API access)?
   - If operator-only: call `/agency-os log <id> "blocked-operator: <one-line what the operator must do>"`, then `/agency-os move <id> --to discussion`, then emit the result report (step 6) with `status: blocked-operator`. Do not skip the status flip.
3. Otherwise: execute the brief end-to-end.
4. **Self-assessment.** Before closing: did I complete 100% of the acceptance criteria? Partial completions are **not** Done.
5. **Auto-close — required, every outcome.** Pick the closer command from the table above and run it BEFORE emitting the result report. Verify the closer returned success. If the closer itself errors (e.g. Notion API hiccup), retry once; if it still fails, surface that in the result report's `summary` line as `status: failed` with the closer error appended — but still emit the report.
6. **Result report — required, every run, no exceptions.** The agent's final chat output MUST be a single block in this exact format. Returning nothing is not allowed — not on success, not on failure, not on a crash mid-execution. If the agent hit an unrecoverable error before it could do anything meaningful, it still emits the block with `status: failed` and describes what happened. The `status:` line in the report must agree with the final Notion status: `done` <-> Done, every other status <-> Discussion.

   ```
   ### <task-id> — [<title>](<notion-url>)
   status:       done | blocked-operator | needs-clarification | failed
   model:        haiku | sonnet | opus
   result-link:  <url or ->
   summary:      <1-2 sentences: what was done, or what blocked it>
   next-step:    <only if status != done; what operator should do next>

   #### Full output
   <verbatim full output of the agent's execution — every step taken, every tool result summary, every decision made. Do not truncate. If the agent produced no meaningful output beyond the header fields above, write "(no output)" here.>
   ```

**Orchestrator accountability.** After each stage, the orchestrator must confirm it received a result block from every agent it spawned. If an agent returned empty output or no output:
- Treat it as `status: failed`, `summary: agent returned no output`, `full output: (agent returned no output)`.
- Include it in the run summary under failed with that note.
- Never omit a task from the summary because its agent was silent.

## Parent-cascade rule

When a **subtask** transitions To-Do -> In Progress (via `start`), the skill also flips its parent To-Do -> In Progress, if the parent is currently `To-Do`. The parent stays In Progress until the operator (or a deliberate later `/agency-os done <parent-id>`) closes it.

## Output

**The plan outline is ALWAYS printed first** — both in dry-run (without `--go`) and in real dispatch (with `--go`). The user must see what's about to fire before any agent spawns. In `--go` mode, after printing the outline, immediately proceed to dispatch — do not pause for confirmation (the `--go` flag already is the confirmation).

Emit the outline as plain markdown (no fenced code block, so the links are clickable):

**plan (`<N>` tasks, `<S>` stages):**

- **stage 1** (`<K>` tasks, parallel):
  - `[haiku]` [title](url)
  - `[sonnet]` [title](url)
  - ...
- **stage 2** (`<L>` tasks, parallel, after stage 1):
  - `[haiku]` [title](url) — deps: [dep-title](dep-url)
  - ...

If any tasks were dropped for external blockers, follow with:

**blocked-deps (`<B>` tasks, not dispatched):**
- [title](url) — missing: [dep-title](dep-url) (or raw dep-id if unknown)

If `blocked-deps` is non-empty, also print: `note: <B> task(s) have dependencies outside this batch. Approve the missing deps or run them first, then /agency-os run again.`

In dry-run mode, the outline IS the entire output — stop here, fire nothing.

In `--go` mode, after the outline, print a one-line marker — `dispatching stage 1...` — then begin dispatch. After completion, the orchestrator emits two more sections:

**1. Per-task detail** — one block per task executed, in stage order, verbatim from each execution agent's result report:

```
---
### <task-id> — [<title>](<notion-url>)
status:       done | blocked-operator | needs-clarification | failed
model:        haiku | sonnet | opus
result-link:  <url or ->
summary:      <...>
next-step:    <...>

#### Full output
<verbatim agent output>
---
```

**2. Run summary** — after all per-task blocks. **Do NOT wrap the summary in a fenced code block** (```), because markdown links inside code fences render as literal text in Claude Code. Emit the summary as plain markdown so `[title](url)` links are clickable:

**run summary (T queued, S stages):**
- done (`<N>`): [title](url), [title](url), ...
- needs operator (`<M>`): [title](url), ...
- needs clarification (`<P>`): [title](url), ...
- blocked-deps (`<B>`): [title](url) (dep: [dep-title](dep-url)), ...
- failed (`<Q>`): [title](url), ...

Omit any row whose count is 0.

`blocked-deps` entries also surface which dep blocked them. The orchestrator must emit both sections — the per-task detail AND the summary — every time `--go` is used.
