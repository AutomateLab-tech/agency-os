# agency-os on Cline / Continue

Both harnesses support custom instructions plus MCP servers, which is everything agency-os needs.

## Install

1. Vendor `.claude/skills/agency-os/` into your project (copy it from this repo).
2. Add a custom-instructions block (Cline: settings -> custom instructions; Continue: `.continue/config.json` or workspace settings) pointing the agent at the spec:

   ```
   You have access to the agency-os skill. The full spec is in
   .claude/skills/agency-os/SKILL.md. When the user invokes
   /agency-os <command> or describes the same intent in natural
   language, follow SKILL.md exactly: sync, resolve IDs against the
   cache, mutate Notion via the Notion MCP, return the spec's output.
   Treat the "Execution model — delegate to Haiku" section as
   Claude-Code-only and run mutations inline.
   ```

3. Add the Notion MCP server with your integration token.

4. In a fresh chat, ask the agent to run `/agency-os scaffold`.

## Triggers

Slash form (`/agency-os ...`) and natural language both work because the custom instructions teach the agent to interpret them.

## Notes

- No `.env` is needed if your harness's MCP config holds the Notion token.
- The full feature surface (status flow, dependencies, recurring tasks, batch run) is available.
