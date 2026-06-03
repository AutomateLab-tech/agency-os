# agency-os on Claude Code

Native plugin. Slash commands work out of the box, and per-command Notion mutations dispatch to a Haiku subagent so the orchestrator stays free for conversation.

## Install

```
/plugin install ratamaha-git/agency-os
```

The plugin registers `skills/agency-os/SKILL.md` as a skill and exposes every `/agency-os <command>` as a slash command in your current project.

## Configure

1. Create a Notion integration at https://www.notion.so/my-integrations.
2. Share it with the page where agency-os should live (or the workspace root).
3. Drop the token in `.env` at your project root:

   ```
   NOTION_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

4. Run `/agency-os scaffold`. It builds the Hub, Tasks DB, corpus pages, and linked views, then prints the Hub URL.

## How commands run

- The orchestrator (your current Claude Code model) handles conversation and parses natural language into `/agency-os <command> <args>`.
- Each Notion mutation dispatches to a Haiku subagent that reads SKILL.md, performs the MCP call, and returns the result verbatim.
- Batch execution (`/agency-os run`) spawns one agent per task, picking the model (Haiku/Sonnet/Opus) by task complexity.
- Why: mechanical work runs on a cheaper, faster model; the orchestrator stays focused on the thread.

## Model selection

Claude Code handles model selection automatically — no configuration needed. The `/agency-os init` command and `config.json` are for **non-Claude harnesses only**; Claude Code ignores them.

## Triggers

Both forms work:

- Slash: `/agency-os suggest "Write quickstart" --corpus="Content"`
- Natural language: "add a suggestion to write the quickstart in Content corpus"

The parser is in SKILL.md - see the command list there.
