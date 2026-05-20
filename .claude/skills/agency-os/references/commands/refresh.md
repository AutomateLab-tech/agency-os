# Command: `refresh`

Auto-enumerate the agent-runnable To-Do set and write it to `state/todo-ids.json`. **No arguments.** The operator's only job upstream is to mark rows in Notion with `Exec=Agent`; `refresh` then fetches them via the Notion REST API and the sidecar is the enumeration substrate for `run`.

The currently installed Notion MCP does not expose property-filtered enumeration of a data source, so this command shells out to `scripts/query-tasks.py`, which posts to `POST /v1/data_sources/{id}/query` with a server-side `Status="To-Do" AND Exec="Agent"` filter (Notion API version `2025-09-03`). The integration token (`NOTION_KEY` in `.env`) must be shared with the Tasks database.

Run:

```
python .claude/skills/agency-os/scripts/query-tasks.py
```

The script:

1. Loads `NOTION_KEY` from `.env` and `tasks_database.data_source_id` from `references/notion-pointers.json`.
2. Queries the data source with the two-gate filter, paginating through `has_more`/`next_cursor`.
3. For each result, fetches the page's block children once to extract a `description_preview` (the text between the `Description` H2 and the next H2; first 200 chars).
4. Writes `.claude/skills/agency-os/state/todo-ids.json`:
   ```json
   {
     "refreshed_at": "<iso>",
     "tasks": [
       {
         "id": "<uuid>",
         "url": "https://www.notion.so/...",
         "title": "...",
         "corpus": "General",
         "priority": "3",
         "effort": "M",
         "type": "one-time",
         "cadence": null,
         "last_done": null,
         "exec": "Agent",
         "parent_task_id": null,
         "has_todo_subtasks": false,
         "description_preview": "<first 200 chars of Description>",
         "dependencies": [
           { "id": "<uuid>", "status": "Done" },
           { "id": "<uuid>", "status": "To-Do" }
         ]
       }
     ]
   }
   ```
5. Prints a summary: `refreshed: <N> agent-runnable To-Do tasks -> state/todo-ids.json` followed by one line per task.

**Failure modes.** The script aborts with a non-zero exit and an explanatory message if `NOTION_KEY` is missing, the integration is not shared with the database, or the API returns an error. The existing sidecar is overwritten only after the query succeeds end-to-end.
