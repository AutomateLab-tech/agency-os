# Extending agency-os

How to go beyond the defaults: add corpora, add commands, plug in other skills, and swap out the task-enumeration backend.

---

## Adding corpora

A corpus is a domain page in Notion scoped to a type of work. The default set is `General` and `Recurring`, but the right corpora depend on what you're operating.

To add one after scaffold:

```
/agency-os add-corpus "Backlinks" --goal "Build 50 quality backlinks to the homepage by Q3"
```

This does four things:
1. Appends `Backlinks` as a new option in the Tasks DB `Corpus` select field.
2. Creates a new corpus page under the Hub with the Goal you provided and an empty Local guidance section.
3. Adds a filtered linked DB view on that page (Corpus = Backlinks, grouped by Status).
4. Updates `notion-pointers.json` with the new corpus ID.

After creation, open the corpus page in Notion and fill in the **Local guidance** section. This is where you put conventions specific to this corpus - contact names, style rules, relevant external docs, recurring constraints. When an agent works a task in this corpus, the Local guidance is embedded directly in the kickoff brief.

You can add as many corpora as you need. They're cheap to create and useful for grouping work that has distinct conventions.

---

## Adding new commands

The skill spec at `skills/agency-os/SKILL.md` is the executable spec. Every command definition lives in that file. Adding a new command means editing SKILL.md.

A command entry needs:

1. A name and signature in the command index (the fenced block near the top of SKILL.md).
2. A `## Command: <name>` section with:
   - Numbered steps the subagent follows
   - The exact output format (what it prints on success/failure)
   - Failure behavior (what to print, whether to abort or continue)

Guidelines:
- Keep commands single-purpose. A command that does two unrelated things is two commands.
- Every mutating command needs a sync preflight: run `python .claude/skills/agency-os/scripts/sync-tasks.py` to refresh `state/tasks.json`, then read state from that file. Abort the mutation if the sync call fails. Read-only commands may proceed against the stale mirror with a warning.
- Every mutating command must also write-through patch the local mirror row in `state/tasks.json` using the MCP response payload, so the next command sees current state without another sync round-trip.
- Every command that touches Notion must go through the MCP tools (`notion-update-page`, `notion-create-pages`, etc.) - never write Notion API calls inline in a prompt.
- Output format matters: the orchestrator and the run summary parser both rely on the exact output lines. Don't change existing output formats without updating callers.

The subagent dispatched by `/agency-os <cmd>` always reads SKILL.md first before executing. So edits take effect immediately - no build step, no publish step.

---

## Plugging other skills into the brief

When `start` assembles a kickoff brief, it pulls:
- Task row properties (title, corpus, effort, etc.)
- The Description section from the task page
- The latest discussion log entry
- Corpus Goal + Local guidance
- The full General Guidance page body

The General Guidance page is seeded from `references/general-guidance.md`. If you want an executing agent to know about another skill - say, a writing skill or a deployment skill - the right place to reference it is in the General Guidance file.

Example addition to `references/general-guidance.md`:

```markdown
## Available skills

- my-publish-skill: research, draft, audit, and publish content. Spec at `.claude/skills/my-publish-skill/SKILL.md`.
- my-deploy-skill: stage, commit, and push the repo. Spec at `.claude/skills/my-deploy-skill/SKILL.md`.
```

After editing the local file, push it to Notion:

```
/agency-os scaffold
```

Scaffold is idempotent - it won't recreate existing structure, but it will re-seed the General Guidance page from the local file when the content has changed.

Alternatively, you can also link to another skill from within a task's Description section. The executing agent can then read that skill's SKILL.md directly.

You can also link into `.claude/skills/<your-skill>/` from the Corpus Local guidance section, scoping the skill reference to tasks in that corpus only.

---

## Swapping the task-enumeration backend

`refresh` shells out to `scripts/query-tasks.py` to enumerate To-Do + Agent rows. The script exists because the Notion MCP (as of the initial release) does not expose property-filtered enumeration of a data source. The script posts directly to the Notion REST API:

```
POST /v1/data_sources/{id}/query
Filter: Status = "To-Do" AND Exec = "Agent"
```

If the Notion MCP gains property-filtered data source queries in a future release, the script becomes redundant. To swap it out:

1. Edit the `## Command: refresh` section in `SKILL.md`.
2. Replace the "shells out to `scripts/query-tasks.py`" step with the equivalent MCP call.
3. Keep the output contract identical: `state/todo-ids.json` with the same schema, and the same printed summary line.

The rest of the system (`run`, the execution agents, the planner) reads `state/todo-ids.json` and doesn't care how it was produced.

If you want to filter on different criteria - say, only tasks in a specific corpus, or only tasks below a certain effort level - you can fork `scripts/query-tasks.py` or replace it entirely. The only contract is the output file schema.

---

## Plugin marketplace registration

agency-os is a Claude Code plugin. To list it on the Claude Code plugin marketplace:

1. Ensure the repo has a valid `plugin.json` (or equivalent manifest, per the current Claude Code plugin spec at https://docs.claude.com/en/docs/claude-code/plugins).
2. The skill entry point must be in `skills/agency-os/SKILL.md`. The plugin manifest points to this file.
3. Register at the Claude Code plugin registry. <!-- TODO: link to the registry submission page once published -->
4. Once listed, operators can install with `/plugin install agency-os` (short name) rather than the full repo URL.

Share it via the `owner/repo` shorthand:

```
/plugin install ratamaha-git/agency-os
```
