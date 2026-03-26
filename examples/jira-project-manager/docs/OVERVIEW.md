# Jira Project Manager Example

This example demonstrates a non-trivial ClawJection bundle.

It shows how a bundle can:
- install local tooling
- install a bundled Jira skill
- install a remote ClawHub skill
- discover the OpenClaw workspace from `~/.openclaw/openclaw.json` or `--openclaw-config-path`
- seed OpenClaw workspace files such as `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `TOOLS.md`, `MEMORY.md`, and `memory/YYYY-MM-DD.md`
- return structured `followups`
- instruct the agent how to continue after the user replies

This example performs real local file mutations. It treats `IDENTITY.md` as part of the role change itself, so the bundled identity file replaces the existing one. The project-manager operating posture is then reinforced through `AGENTS.md`, `SOUL.md`, `MEMORY.md`, and the daily memory log.
