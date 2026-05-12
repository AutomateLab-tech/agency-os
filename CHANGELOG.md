# Changelog

All notable changes to this project will be documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

### Changed
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
