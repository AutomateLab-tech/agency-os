# Structuring work — parent vs subtask vs log entry

The hardest part of using this board well is deciding **what shape** a piece of work takes. Three rules:

**1. A task is a coherent unit with a clear "done" state.** It can be shipped, merged, published, decided. "Set up X integration" is a task. "Think about X" is not — it has no done state.

**2. A subtask is a child task that can be completed independently and is bounded by a deliverable, not by a step.** "Write the onboarding blurb" is a subtask of "Onboarding flow rewrite" because the blurb is a separable artifact with its own done. "Click submit on the form" is **not** a subtask — that's a step, log it in the discussion or done note instead.

Rule of thumb: if you'd naturally hand it to a different agent on a different day, it's a subtask. If you'd do it inline while working the parent, it's a step.

**3. A log entry is a decision, clarification, or update on existing scope.** "Decided to launch Tue not Wed" is a log entry on an existing launch task, not a new subtask. "Operator handles the review thread" is a log entry, not a subtask.

## Depth

- Top-level: standalone work or a top-level container.
- Subtask (depth 1): the normal case. Most subtasks live here.
- Nested subtask (depth 2): legitimate when a parent has multiple major deliverables, each with its own breakdown. Example: `Product launch` → `directory submissions` (container) → each individual directory.
- Depth 3+: the skill warns. Almost always means the hierarchy should be flattened or split into separate top-level tasks.

## Parent discipline — never dump in root

A flat list of unrelated top-level tasks is a smell. **Before creating ANY new row, the orchestrator MUST run the structure preflight.** This is non-negotiable for batch creation and required even for single rows when the work is clearly part of a broader initiative.

### Structure preflight protocol

The fastest path: read `state/task-tree.json` (written by every `sync`, `tree`, or `suggest`). This file gives a full tree snapshot with no MCP round-trip. If it's absent, run `/agency-os tree` once to generate it — this is cheap and should be a first step whenever starting a new session or about to do batch work.

```
step 1 — read state/task-tree.json (or run /agency-os tree if absent)
step 2 — scan top-level In Progress + To-Do rows for an umbrella match
step 3 — if found: propose --parent=<id> in chat and wait for user confirmation
          if batch (3+ rows): also propose the container row before any work items
          if none found: proceed with top-level suggest
```

The orchestrator MUST **show the planned tree in chat** before any mutation flies. One-liner format:

```
Planned tree:
  OS-12 "Umbrella initiative" [existing]
    → NEW "Container: <theme>" [new container]
      → NEW "<work item 1>"
      → NEW "<work item 2>"
      → NEW "<work item 3>"
```

User sees the shape, can redirect, then the orchestrator dispatches each `suggest` call in order.

**Check 1: Does this belong under an existing parent?** Match against In Progress and To-Do rows. If the new work is a sub-deliverable, follow-up, related artifact, or supporting piece of one of those initiatives, parent it there with `--parent=<id>`. Don't create siblings of an umbrella you can attach to.

**Check 2: Is this a batch of 3+ related rows?** Create a container row first, then add each work item as a child. A container is a task — title like "Landing page content series", "Onboarding flow rewrite", "API v2 migration" — with a coherent "all subtasks shipped" done state. It is NOT a folder. The container itself goes under the umbrella parent from Check 1 when one exists.

**Decision matrix:**

| Situation | Action |
|---|---|
| 1 task, unrelated to anything active | `suggest --force-top-level` |
| 1 task, clearly part of an active initiative | `suggest --parent=<active-initiative-id>` |
| 2 tasks sharing a clear theme | container helps even at N=2; use judgment |
| 3+ related tasks at once | container subtask first, then `--parent=<container-id>` for each |
| 3+ flat top-level rows that share a theme | **the failure mode — never do this** |
| unsure whether a parent exists | read `state/task-tree.json` first, always |

**Ownership: the orchestrator, not the subagent, makes the structure call.** Before any `suggest` batch dispatches, the orchestrator must (a) read the tree snapshot, (b) check for an existing umbrella, (c) decide whether a container is needed, (d) print the planned tree in chat so the user can correct it. The subagent executes the orchestrator's plan verbatim — it does not invent or reassign parents mid-batch. The `suggest` structure preflight is a safety net for single-row calls, not a replacement for the orchestrator's upfront planning on batches.

**Reparenting existing rows.** When the user asks to "reorganize", "restructure", "group under <parent>", or "move <task> under <other-task>" — that's `update --parent=<id>` (one row at a time) or, for bulk reorganization, the orchestrator plans the new tree (show it in chat), creates any new container rows via `suggest --parent`, then reparents the existing rows via `update --parent`.

## The "move this chat to Notion" workflow

When the user says "save this to Notion", "make this a task", "track this in Notion", "capture this conversation" mid-chat, read the conversation as a **tree, not a transcript**:

1. **Identify the parent task.** What's the central thing being discussed? Usually one coherent goal. Phrase as an imperative ≤80 chars. → `/agency-os suggest "<title>" --corpus=<inferred>`.
2. **Open it for discussion immediately** — the chat already contains clarification. → `/agency-os discuss <id>`.
3. **Log the rationale and major decisions** as one or two distilled entries. Don't dump the whole chat verbatim — extract: "decided X over Y because Z", "agreed scope is A not B". → `/agency-os log <id> "<distilled>"`.
4. **Carve out subtasks** for each separable deliverable the chat surfaced. One subtask per concrete artifact / hand-offable chunk. → `/agency-os add-subtask <id> "<title>"` per item.
5. **Stop and ask before approving.** Moving a chat to Notion is a capture step, not a commitment. End with: `Captured to <url> in Discussion. Approve when you're ready to schedule.`

What **not** to do:

- Don't paste the raw chat as the Description. Description = acceptance criteria + context, not a transcript.
- Don't create a subtask for every message. Most exchanges are clarifications and belong in the discussion log.
- Don't create a separate top-level task per subtopic if they share a parent goal. Use subtasks; that's what they're for.
- Don't auto-approve.

## Worked example

Chat: user and agent discuss launching a new product on a directory site. The exchange touches: which date, who writes the blurb, what assets are needed (logo, GIF, copy), who handles the comments thread, a follow-up social post.

**Wrong shape:** one task "Directory launch" with a Description that's the whole chat dumped in.

**Right shape:**

- Parent task: `Directory launch` (corpus=General, Status=Discussion)
  - Description: `Launch on directory site Tue morning. Goal: top-5 of the day. Operator runs the comment thread.`
  - Discussion log entry: `decided Tue morning; operator runs comments; social follow-up included in scope.`
  - Subtask: `Write launch blurb (60 + 260 char)`
  - Subtask: `Produce launch GIF + logo asset`
  - Subtask: `Draft social launch thread`
  - (The comment-thread duty is a single-person low-effort step → mentioned in discussion log, not a subtask.)
