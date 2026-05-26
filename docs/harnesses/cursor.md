# agency-os on Cursor

Cursor doesn't have a native plugin system, so agency-os loads as a project rule plus a Notion MCP connection.

## Install

1. Clone or copy the agency-os repo into your project (or vendor `skills/agency-os/` from this repo to `.claude/skills/agency-os/` in your workspace).
2. Add a Cursor rule that points at the skill spec. Create `.cursor/rules/agency-os.mdc`:

   ```mdc
   ---
   description: agency-os - Notion-as-source-of-truth dispatch board
   alwaysApply: true
   ---
   You have access to the agency-os skill. The full spec is in
   `.claude/skills/agency-os/SKILL.md`. When the user invokes
   `/agency-os <command>` or describes the same intent in natural
   language ("add a suggestion ...", "discuss the X task", "approve
   that"), follow SKILL.md exactly: sync, resolve IDs against the
   cache, mutate Notion via the Notion MCP, return the spec's output.
   
   For model selection (read SKILL.md's "Execution model" section):
   - You are on Cursor (non-Claude harness), so skip the "delegate to Haiku" part.
   - Run mutations inline on this agent.
   - For batch execution (/agency-os run), read config.json (created by /agency-os init)
     to see which models are configured for easy/med/hard tasks.
   ```

3. Configure the Notion MCP server. In Cursor settings -> MCP, add a server with your Notion integration token (the same one you'd put in `.env` as `NOTION_KEY`).

4. Restart Cursor. Open your project and ask the agent to run `/agency-os init`. This stores your model preferences for task execution.

5. Then scaffold the board with `/agency-os scaffold`.

## Triggers

Cursor doesn't register the slash command natively, but typing it into chat works because the rule teaches the agent to interpret it. Natural language works the same way.

## Notes

- The skill's `.env` / `NOTION_KEY` fallback isn't used in Cursor; the MCP server holds the credential.
- **Model selection:** Cursor doesn't spawn subagents, so the skill uses `config.json` (created by `/agency-os init`) to guide task complexity choices. You don't need an API integration unless you want to actually execute tasks against different models; for planning and discussion, one model is fine.
- All other SKILL.md behavior (status flow, schema, dependencies) applies unchanged.
