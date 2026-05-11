# agency-os on any MCP-capable agent

If your harness can (a) load a long system prompt or instruction file and (b) call an MCP server, you can run agency-os.

## What you need

- An agent that can read `.claude/skills/agency-os/SKILL.md` as instructions (or have it pasted into a system prompt).
- The Notion MCP server, configured with your integration token.
- A working directory where the agent can read/write `references/notion-pointers.json` and `references/notion-cache.json`.

## Wiring it up

1. Vendor `.claude/skills/agency-os/` into your project.

2. Add this to your agent's system prompt (or custom instructions):

   ```
   You have access to the agency-os skill. The full spec is in
   .claude/skills/agency-os/SKILL.md. When the user types
   /agency-os <command> or describes the same intent in natural
   language, follow SKILL.md exactly.

   Execution:
   - Sync preflight on every command (notion-cache.json).
   - Resolve <id> against the cache; mutate via Notion MCP.
   - Return the exact output format SKILL.md specifies.
   - Ignore the "delegate to Haiku" section; run mutations inline.
   ```

3. Wire the Notion MCP. The skill calls tools named `notion-fetch`, `notion-create-pages`, `notion-update-page`, `notion-search`, `notion-update-data-source`. The exact tool prefix varies by harness; the spec resolves them dynamically as `mcp__*__notion-*`.

4. First run: ask the agent `/agency-os scaffold`. If your harness has no `.env` mechanism, set `NOTION_KEY` in your shell environment so the MCP server can pick it up.

## What you lose

- **Slash command UI.** Most generic agents don't render `/agency-os ...` as a real command; you type it as plain text. The parser still works.
- **Subagent delegation.** The Claude Code wrapper offloads mutations to a cheaper model; on a generic harness, everything runs on whatever model is in the chat. The work is mechanical, so even a small model handles it fine.

## What you keep

The full skill: status flow, dependencies, recurring tasks, subtasks, batch `run`, all of it. The contract is in SKILL.md, not in the wrapper.
