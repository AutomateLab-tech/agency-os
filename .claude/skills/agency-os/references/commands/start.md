# Command: `start <id>` (alias: `launch`)

Move To-Do -> In Progress and emit the kickoff brief.

1. Sync preflight.
2. Resolve `<id>` (UUID, URL, or substring against To-Do rows).
3. Verify status is `To-Do`. If `Suggestion` -> refuse with `discuss it first`. If `Discussion` -> refuse with `approve it first`. If `In Progress` -> soft-allow (re-emits brief).
4. `notion-update-page` Status -> In Progress.
5. **Assemble the kickoff brief, in this exact order:**

   ```
   ## Task
   [<title>](<notion-url>)  [<corpus> / <priority> / type=<type>{ cadence=<cadence>}{ last_done=<date>} / effort=<effort>]

   ## Description
   <Description toggle body>

   ## Subtasks (N)
   - [Status]  <subtask title>  ->  /agency-os start <subtask-id>
   - ...

   ## Latest discussion entry  (of <K> total)
   <most-recent entry verbatim>
   (For older entries: /agency-os show <id> --section discussion --entry <date>)

   ## Corpus: <name>
   <Goal + Local guidance from the corpus page>

   ## General guidance
   <full general guidance page body>
   ```

6. End with: `Brief loaded. Proceed.`

**Overfeed protection.** The brief never embeds:
- Older discussion entries (only the latest; the rest are referenced by date)
- Sibling tasks
- Subtask bodies (only their titles + status)
- The Done log
