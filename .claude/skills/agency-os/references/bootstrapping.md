# Bootstrapping

Fresh workspace — no template duplication required, the command creates everything:

```
/agency-os scaffold
```

If your Notion integration is shared with a specific page rather than the workspace root, pass that page:

```
/agency-os scaffold --parent=<page-id-or-url>
```

You can pass `--corpora "Name1,Name2,Name3"` to scaffold with custom corpus names instead of the defaults (`General`, `Recurring`). You can always add more later with `/agency-os add-corpus "<name>"`.

Migrating from an existing Notion setup:

```
/agency-os scaffold
# then read existing pages, parse content, and:
#   - bulk /agency-os suggest each parsed item with --corpus inferred from heading
#   - copy resource pages to the new Resources page
#   - archive the old structure
# this is a one-shot manual migration; the skill does not provide a generic import command,
# because the source format varies and parsing requires per-source judgment.
```

On non-Claude-Code harnesses, run `/agency-os init` after scaffold to store your preferred models in `config.json` (used by `run`).
