# Changelog

All notable changes to this project will be documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

## [0.1.6] - 2026-05-12

### Changed
- **Status discipline enforced on every run outcome.** Execution agents must now leave each row in a terminal-for-this-run state before returning: `Done` on full completion, `Discussion` on any other outcome (partial, blocked-operator, needs-clarification, failed). The old pattern of leaving blocked-operator rows at `In Progress` is forbidden — it lied about live state and cluttered the dashboard. A matching discussion-log entry explaining the outcome is required.
- **`start` is mandatory as the first call** in the execution-agent contract, flipping `To-Do` -> `In Progress` before any work begins.
- **Run output uses CommonMark markdown links** (`[title](url)`) instead of HTML `<a>` tags. Claude Code renders markdown but not HTML, so the old format showed up as literal text.

### Changed (prior unreleased)
- **Sync always reads from Notion live.** All commands now call `notion-fetch` directly on every invocation; there is no local snapshot or fallback. If Notion is unreachable, the command aborts rather than continuing against stale data. `notion-cache.json` is no longer written or read by any command.
- **Subagents always report back.** Execution agents are required to emit a result block on every exit path — success, failure, or mid-execution crash. The orchestrator must relay that result to the operator; if an agent returns empty output, the orchestrator surfaces `subagent returned no output` rather than staying silent. Applies to both single-command dispatch and batch `run`.

### Added
- Community health files: SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG
- `.github/` issue templates and PR template

---

## [0.1.0] - 2025-05-12

### Added
- Initial release: agency-os Claude Code plugin
- Notion task board integration via the `agency-os` skill
- Claude Code skills for AI-driven task planning and execution
- `.claude-plugin/` manifest for Claude Code plugin distribution
