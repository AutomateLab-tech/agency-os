# agency-os

> A visual workflow board for working with AI. Structure ideas into tasks, stay in control of what ships.

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## What it is

agency-os turns Notion into the dashboard of your own AI agency. You talk through ideas with the agent. It pushes back, clarifies scope, breaks the work into tasks and subtasks with the right hierarchy and dependencies, and writes it all into Notion. You approve. Agents then pick up the work and ship it - jobs, submissions, drafts, reports - with result links back on the row.

It's for founders, makers, solo operators, and teams who want their AI tools to actually ship things, not just talk about them.

[Read the launch post with examples and illustrations](https://automatelab.tech/agency-os-launch/)

---

## What you get

- **Structure over noise.** AI ideas land as Suggestions, not commands. Discuss, scope, and approve before anything runs. The board is the source of truth; work has shape and status.
- **One visual board for everything.** Ideas, tasks, decisions, finished work - all in a single Notion view with a clear status flow. No chasing TODOs across Slack, docs, and twelve open tabs.
- **You stay in control of execution.** Nothing dispatches autonomously. Every run is operator-gated. Agents only touch rows you've explicitly marked `Exec=Agent`; the board is honest about what's queued, what's blocked, and why.
- **The agent plans with you, not at you.** Talk through an idea in plain English. The agent asks clarifying questions, carves it into tasks and subtasks, sets dependencies. You stop being the project manager.
- **The board stays organised.** Before adding any task, the skill checks whether it belongs under an active initiative and surfaces the match. `/agency-os tree` shows the full hierarchy at a glance. Accidental flat lists of unrelated top-level rows are caught before they land.
- **Agents do the mechanical parts.** Once a task is approved with `Exec=Agent`, an AI handles it end-to-end: form fills, draft posts, directory submissions, log-and-close work. Result links come back on the row.
- **Dependencies just work.** Tasks that block other tasks run in order. The queue won't fire something whose prereq isn't done.
- **Right model for the job** *(side benefit, not the point).* Mechanical work runs on fast, cheap models; heavy thinking goes to bigger ones. You don't pay flagship rates for clerical tasks.

---

## How it works (30 seconds)

1. **Suggest** an idea. The skill checks whether it belongs under an existing initiative before creating anything — no accidental root-level clutter.
2. **Discuss** with the agent. It asks clarifying questions, then writes out subtasks and dependencies on the row.
3. **Approve** when you're ready. The task and its subtasks move to To-Do.
4. **Run.** Agents pick up `Exec=Agent` rows, work in parallel (respecting dependencies), and close them with result links.

Use `/agency-os tree` any time to see the full hierarchy at a glance.

That's the whole loop. The board is the source of truth; the agent is just an executor.

---

## 1-minute setup

1. Install agency-os in your harness (see the table below).
2. Create a Notion integration at https://www.notion.so/my-integrations and share it with your workspace (or a specific parent page).
3. Drop the token in `.env`: `NOTION_KEY=secret_...` (or configure in your harness's MCP settings).
4. **If using Cursor, Cline, Continue, or a generic agent:** run `/agency-os init` to configure which models to use for easy/med/hard tasks. (Claude Code handles this automatically.)
5. Run `/agency-os scaffold` (or `/agency-os scaffold --parent=<page-id>` if the integration is scoped to a specific page).

That's it. Scaffold builds the Hub, Tasks database, corpus pages, and all linked views in Notion. No template to duplicate.

---

## Install

agency-os ships as a Claude Code plugin and as a portable skill spec for every other harness. The core contract (`skills/agency-os/SKILL.md`) is the same everywhere; only the wrapper changes.

| Harness | Format | Setup |
|---|---|---|
| **Claude Code** | Plugin | `/plugin install https://github.com/ratamaha-git/agency-os` |
| **Cursor** | Skill / rules | [docs/harnesses/cursor.md](docs/harnesses/cursor.md) |
| **Cline / Continue** | Custom instructions | [docs/harnesses/cline.md](docs/harnesses/cline.md) |
| **Any MCP-capable agent** | Generic spec | [docs/harnesses/generic.md](docs/harnesses/generic.md) |

All variants talk to Notion through the same MCP server, so your data and commands stay portable. Model selection (which models run which tasks) is configured via `/agency-os init` on non-Claude harnesses; Claude Code handles it automatically.

---

## Docs

- [docs/quickstart.md](docs/quickstart.md) - 5-step setup with a worked example
- [docs/concepts.md](docs/concepts.md) - status flow, dependencies, what lives where
- [docs/extending.md](docs/extending.md) - custom corpora, new commands, integrations

---

## License

MIT - see [LICENSE](LICENSE).

---

Built by [AutomateLab](https://automatelab.tech).
