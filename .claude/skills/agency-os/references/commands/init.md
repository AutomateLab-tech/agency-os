# Command: `init [--harness=...] [--haiku=...] [--sonnet=...] [--opus=...]`

**Non-Claude harnesses only.** Configure which models to use for task execution. Claude Code harnesses ignore this; they have built-in model selectors.

**Why it matters:** Cursor, Cline, Continue, and generic MCP harnesses can't spawn subagents with different models on the fly. Instead, store your preferred models upfront in `.claude/skills/agency-os/config.json`, then the skill uses them during batch execution.

**Interactive mode** (recommended):
```
/agency-os init
```

Prompts:
1. Which harness are you using? (or auto-detect from environment)
2. For *easy* mechanical tasks (form fills, recurring routines), which model? (default: haiku-4-5)
3. For *medium* substantive work (drafting, audits, revisions), which model? (default: sonnet-4-6)
4. For *hard* strategic work (design, multi-skill reasoning), which model? (default: opus-4-7)

Stores in `.claude/skills/agency-os/config.json` and prints `config: created -> <path>`.

**Non-interactive mode:**
```
/agency-os init --harness cursor --haiku claude-haiku-4-5 --sonnet claude-sonnet-4-6 --opus claude-opus-4-7
```

If a harness doesn't support a model (e.g., Cursor is configured for only Sonnet), pass the model it does support for all three tiers; the skill will use it for everything.

If `config.json` already exists, re-running `init` overwrites it. To reset: `/agency-os init` interactively.
