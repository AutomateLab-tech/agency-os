# agency-os on Cline / Continue

Both harnesses support custom instructions plus MCP servers, which is everything agency-os needs.

## Install

1. Vendor the skill into your project: copy `skills/agency-os/` from this repo to `.claude/skills/agency-os/` in your project.
2. Add a custom-instructions block (Cline: settings -> custom instructions; Continue: `.continue/config.json` or workspace settings) pointing the agent at the spec:

   ```
   You have access to the agency-os skill. The full spec is in
   .claude/skills/agency-os/SKILL.md. When the user invokes
   /agency-os <command> or describes the same intent in natural
   language, follow SKILL.md exactly: sync, resolve IDs against the
   cache, mutate Notion via the Notion MCP, return the spec's output.
   
   For model selection (read SKILL.md's "Execution model" section):
   - You are on Cline/Continue (non-Claude harness), so skip the "delegate to Haiku" part.
   - Run mutations inline on this agent.
   - For batch execution (/agency-os run), read config.json (created by /agency-os init)
     to see which models are configured for easy/med/hard tasks.
   ```

3. Add the Notion MCP server with your integration token.

4. In a fresh chat, ask the agent to run `/agency-os init`. This stores your model preferences for task execution.

5. Then scaffold the board with `/agency-os scaffold`.

## Triggers

Slash form (`/agency-os ...`) and natural language both work because the custom instructions teach the agent to interpret them.

## Notes

- No `.env` is needed if your harness's MCP config holds the Notion token.
- **Model selection:** Cline/Continue don't spawn subagents, so the skill uses `config.json` (created by `/agency-os init`) to guide task complexity choices. If your harness has Anthropic SDK integration, it can use different models per task.
- The full feature surface (status flow, dependencies, recurring tasks, batch run) is available.
