# Jira Project Manager Example

This example demonstrates a non-trivial ClawJection bundle.

It shows how a bundle can:
- install local tooling
- install a bundled Jira skill
- install a remote ClawHub skill
- discover the OpenClaw workspace from `~/.openclaw/openclaw.json` or `--openclaw-config-path`
- modify OpenClaw workspace files such as `IDENTITY.md`, `AGENTS.md`, and `memory.md`
- return structured `followups`
- instruct the agent how to continue after the user replies

This example performs real local file mutations, but it is still only a reference bundle, not a production-ready integration.
