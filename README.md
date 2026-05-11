# agency-os

agency-os: Notion-as-source-of-truth dispatch board for agencies and operators running AI workflows.

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
<!-- TODO: add marketplace badge once listed -->

---

## Why

Operators running AI workflows drown in TODOs spread across chat threads, docs, and spreadsheets. Nothing has a clear owner, a clear status, or a clear "done." Work gets lost or re-discovered instead of executed.

Notion is the one tool that's already open, already organized, and already trusted as the source of truth in most agencies. agency-os puts a structured work board inside Notion - a Tasks database with a defined status flow, corpus pages for grouping work by domain, and a General Guidance page for project-wide rules. The board doesn't replace how you think; it just makes the queue inspectable and executable.

Agents pick up tasks gated by `Exec=Agent`. That gate is operator-set, not automatic - the operator marks rows when they're confident the task can run end-to-end without human intervention. This keeps the queue honest: no surprise autonomous execution, no tasks that silently stall.

Model choice happens per task at dispatch time. Haiku for mechanical work (form filings, template-driven posts, log-and-close mutations), Sonnet for substantive drafting and judgment calls, Opus rarely and only when the reasoning is genuinely hard. Token spend scales with task complexity, not workflow size.

---

## Quick start

```bash
# 1. Install the plugin
/plugin install https://github.com/your-org/agency-os  # TODO: update URL when repo is public

# 2. Set your Notion integration token
echo "NOTION_KEY=secret_..." >> .env

# 3. Scaffold the workspace (idempotent)
/agency-os scaffold

# 4. Define your first corpus and suggest a task
/agency-os add-corpus "My Work" --goal "Ship X"
/agency-os suggest "My first task" --corpus="My Work"

# 5. Run the full flow
/agency-os discuss <id>    # clarify
/agency-os approve <id>    # schedule
/agency-os start <id>      # load brief + begin
```

See [docs/quickstart.md](docs/quickstart.md) for a step-by-step walkthrough with a worked example.

---

## Concepts at a glance

- **Tasks DB** - one Notion database; one row per task, including subtasks. Every task has Title, Status, Corpus, Priority, Effort, Exec, Type, and optionally Parent Task + Dependencies.
- **Corpora** - domain pages (e.g. "Backlinks", "Community", "Infrastructure"). Each corpus has a Goal, local guidance, and a linked view of its tasks.
- **Status flow** - `Suggestion -> Discussion -> To-Do -> In Progress -> Done` (or `Killed`). The gate from To-Do to execution is explicit: `start` loads the brief and flips status.
- **Subtasks** - child rows that inherit Corpus and Status from their parent. Subtasks are separable deliverables, not steps. Steps go in the discussion log.
- **Dependencies** - tasks can block other tasks. `run` resolves the DAG into stages; blocked tasks are reported, not silently skipped.
- **Exec gate** - only rows marked `Exec=Agent` enter the agent queue. The operator sets this field. `Exec=Human` means "this task needs a person." `Exec=none` is the default - not yet decided.
- **`run` stages** - `run` (dry-run) shows the plan; `run --go` dispatches. Stages run sequentially; tasks within a stage run in parallel (cap: 5). Each execution agent loads the brief via `start`, executes, and closes with `done`.

---

## Install

agency-os is a Claude Code plugin. Install it in any Claude Code project:

```
/plugin install https://github.com/your-org/agency-os
```

<!-- TODO: replace URL above with the published plugin URL once the repo is public -->

Once installed, all `/agency-os` commands are available in that project. The plugin reads `.env` for `NOTION_KEY` and writes `notion-pointers.json` to `.claude/skills/agency-os/references/` on first scaffold.

### Requirements

- Claude Code (any recent version)
- A Notion workspace
- A Notion internal integration token with access to the workspace (or at minimum the Hub page subtree)

---

## Public Notion template

Duplicate the ready-made template to get the Tasks database, Hub page, corpus pages, and linked views pre-wired:

<!-- TODO: add public template URL once published. Check .claude/skills/agency-os/references/public-template-url.md -->

> Template link coming soon. Once the repo is public, run `/agency-os scaffold` against your own workspace - it builds everything from scratch and is equally fast.

---

## Docs

- [docs/quickstart.md](docs/quickstart.md) - prereqs, 5-step setup, end-to-end example
- [docs/concepts.md](docs/concepts.md) - hybrid contract, status flow, structuring work, dependencies
- [docs/extending.md](docs/extending.md) - adding corpora, custom commands, plugging in other skills

---

## License

MIT - see [LICENSE](LICENSE).

<!-- TODO: link to launch blog post once published -->
