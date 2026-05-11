# agency-os

> Run your work like a small AI agency, from a single Notion board.

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## What it is

agency-os turns Notion into the dashboard of your own AI agency. You drop ideas in. They get clarified, scheduled, and executed by AI agents. Finished work lands back in Notion with links to whatever shipped - posts, submissions, drafts, reports.

It's for founders, makers, solo operators, and small teams who already think in Notion and want their AI tools to actually ship things, not just talk about them.

---

## What you get

- **One place for everything.** Ideas, tasks, decisions, and finished work all live in one board. No more chasing TODOs across Slack, docs, and twelve open tabs.
- **Agents do the boring parts.** Flip a task to `Exec=Agent` and an AI handles it end-to-end: form fills, post drafts, directory submissions, log-and-close work.
- **Right model for the job.** Mechanical work runs on fast, cheap models. Heavy thinking goes to bigger ones. You don't pay flagship rates for clerical tasks.
- **Dependencies just work.** Tasks that block other tasks run in order. The queue won't fire something whose prereq isn't done.
- **You stay in control.** Nothing dispatches autonomously. Every run is operator-gated; the board is honest about what's queued and why.

---

## How it works (30 seconds)

1. **Suggest** an idea. It lands in the Notion inbox.
2. **Discuss** to clarify scope and break it into subtasks if needed.
3. **Approve** when you're ready. The task moves to To-Do.
4. **Run.** Agents pick up `Exec=Agent` rows, work in parallel, and close them with result links.

That's the whole loop. The board is the source of truth; the agent is just an executor.

---

## 1-minute setup

1. Install agency-os in your harness (see the table below).
2. Duplicate the [public Notion template](https://www.notion.so/35dd01a02a8081dea01cd8d42617f0c8) into your workspace.
3. Create a Notion integration at https://www.notion.so/my-integrations and share it with the duplicated page.
4. Drop the token in `.env`: `NOTION_KEY=secret_...`
5. Run `/agency-os scaffold` (or the natural-language equivalent in your harness).

The board is wired and ready for suggestions.

---

## Install

agency-os ships as a Claude Code plugin and as a portable skill spec for every other harness. The core contract (`.claude/skills/agency-os/SKILL.md`) is the same everywhere; only the wrapper changes.

| Harness | Format | Setup |
|---|---|---|
| **Claude Code** | Plugin | `/plugin install https://github.com/ratamaha-git/agency-os` |
| **Cursor** | Skill / rules | [docs/harnesses/cursor.md](docs/harnesses/cursor.md) |
| **Cline / Continue** | Custom instructions | [docs/harnesses/cline.md](docs/harnesses/cline.md) |
| **Any MCP-capable agent** | Generic spec | [docs/harnesses/generic.md](docs/harnesses/generic.md) |

All variants talk to Notion through the same MCP server, so your data and commands stay portable.

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
