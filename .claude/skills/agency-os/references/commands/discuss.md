# Command: `discuss <id>`

Begin clarification on a Suggestion. Flips status to Discussion and prepares the agent to ask clarifying questions.

1. Sync preflight.
2. Resolve `<id>` (UUID, URL, or unique Title substring against `Suggestion` rows).
3. `notion-update-page` Status -> Discussion.
4. **Print the discussion brief**: row properties + Description section. End with: `Ready to clarify. Ask your questions or paste new requirements; the skill will log them with /agency-os log <id> and create subtasks with /agency-os add-subtask <id>. [Open task](<task-url>)`
5. The agent in this conversation now drives the clarification: it asks questions, accepts user answers, calls `log` for each round, calls `add-subtask` whenever the user's responses imply concrete new work.

`discuss` does not require status to be `Suggestion` — calling it on an already-Discussion row is fine and reloads the brief.
