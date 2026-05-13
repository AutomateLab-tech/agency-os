# Quickstart

Get agency-os running in under 10 minutes. For the full story of how agency-os works and why it matters, [read the launch post](https://automatelab.tech/agency-os-launch/).

---

## Prerequisites

- **Claude Code** installed and authenticated (`claude --version` should return a version).
- A **Notion workspace** where you have admin rights (or at least permission to create pages and databases).
- A **Notion internal integration token** - create one at https://www.notion.so/my-integrations. Share the integration with the page subtree you want agency-os to manage (or the workspace root for maximum reach).

---

## 5-step setup

**Step 1 - Install the plugin.**

```
/plugin install https://github.com/your-org/agency-os
```

Once installed, `/agency-os` commands are available in the current Claude Code project.

**Step 2 - Set your Notion token.**

Create or edit `.env` in your project root:

```
NOTION_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

The token must have access to the workspace or the Hub page. Never commit `.env` - it should already be in `.gitignore`.

**Step 3 - Scaffold the workspace.**

```
/agency-os scaffold
```

This creates the Hub page, Tasks database, General Guidance page, default corpus pages (General, Recurring), and all linked views inside Notion. It's idempotent - safe to run again if anything was missed.

After scaffolding, Notion prints the Hub URL. Open it and:
- Enable "Full width" on the Hub, Guidance, Resources, and corpus pages (the Notion MCP can't do this for you - use the ... menu on each page).
- Enable Sub-items on the Tasks database and wire it to the `Parent Task` / `Subtasks` relation (see the scaffold output for exact steps).

**Step 4 - Define your corpora.**

A corpus is a domain of work (e.g. "Backlinks", "Community", "Infrastructure"). The scaffold creates `General` and `Recurring` by default. Add your own:

```
/agency-os add-corpus "Content" --goal "Publish 2 posts per week on automatelab.tech"
/agency-os add-corpus "Outreach" --goal "Build backlinks through directory submissions"
```

Each corpus gets a Notion page with a Goal section, a Local guidance section, and a linked view of its tasks.

**Step 5 - File your first suggestion.**

```
/agency-os suggest "Write a quickstart guide for agency-os" --corpus="Content" --effort=M
```

The task lands in the Suggestions Inbox in Notion with `Status=Suggestion`.

---

## End-to-end example

This is the full lifecycle of a task from idea to done.

```
# Suggest
/agency-os suggest "Submit to BetaList" --corpus="Outreach" --effort=S

# Opens the task for clarification (flips to Discussion)
/agency-os discuss <id>

# Log decisions mid-discussion
/agency-os log <id> "Decided to use the short-form description, 300 chars max"

# Carve off a subtask for a separable deliverable
/agency-os add-subtask <id> "Write 300-char product description for BetaList"

# Approve - moves task and subtask to To-Do
/agency-os approve <id>

# Start the subtask first (loads its brief, flips to In Progress)
/agency-os start <subtask-id>

# ... agent executes the subtask ...

# Close the subtask
/agency-os done <subtask-id> --note "Written, 287 chars"

# All subtasks done - close the parent
/agency-os done <id> --result-link "https://www.betalist.com/startups/agency-os"
```

At each step, the task page in Notion reflects the current state. The operator can follow along without opening Claude Code.

---

## Running the queue

### The Exec gate

By default, tasks have `Exec=none` - they don't enter the agent queue automatically. To let an agent pick up a task:

1. Open the task row in Notion.
2. Set `Exec = Agent`.

Only do this for tasks you're confident can complete end-to-end without operator input: no captchas, no personal account logins, no "click publish" steps that require a human.

### Refresh - inspect the queue

```
/agency-os refresh
```

Fetches all `Status=To-Do` AND `Exec=Agent` rows from Notion and writes them to `state/todo-ids.json`. Use this to inspect the queue before dispatching.

### Dry run - preview the plan

```
/agency-os run
```

Without `--go`, this is a dry run. It shows:
- Which tasks would be dispatched, and at what model (Haiku/Sonnet/Opus)
- Which stage each task belongs to (based on dependencies)
- Which tasks are blocked because their dependencies haven't reached Done yet

Review the plan before pulling the trigger.

### Dispatch

```
/agency-os run --go
```

Stages execute sequentially. Within each stage, tasks fan out in parallel (cap: 5 at a time). Each execution agent loads the kickoff brief via `/agency-os start`, does the work, and calls `/agency-os done` when finished. If a task can't complete end-to-end (operator login required, etc.), it closes with `blocked-operator` and the row stays In Progress so you see it.

After `run --go` finishes, a summary shows counts by outcome: done, needs-operator, needs-clarification, blocked-deps, failed.
