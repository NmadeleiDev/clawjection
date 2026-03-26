# Jira Project Manager Example

This example demonstrates a non-trivial ClawJection bundle for configuring an OpenClaw instance as a Jira-focused project manager.

## What the agent should do

1. Read `clawjection.yaml`.
2. Resolve the entrypoint as `main.py`.
3. Run the entrypoint with the `apply` action.
4. By default, let the entrypoint discover OpenClaw config from `~/.openclaw/openclaw.json`.
5. If needed, pass `--openclaw-config-path <path>` to override the default config path.
6. Read stdout as agent-readable execution hints.
7. Read the result JSON from `CLAWJECTION_RESULT_PATH`.
8. Execute the returned ordered `followups`.

## Example invocation

```bash
python3 main.py apply
```

With explicit config override:

```bash
python3 main.py apply --openclaw-config-path /path/to/openclaw.json
```

## Expected behavior

When run successfully, this example:
- discovers the OpenClaw workspace from `openclaw.json`
- writes `IDENTITY.md`
- appends a Jira project-manager block to `AGENTS.md`
- appends a seed block to `memory.md`
- installs the bundled Jira ACLI skill into `skills/jira-acli/SKILL.md`
- reports installation of the ClawHub `gog` skill
- returns ordered `followups` telling the agent to:
  - ask the user for Jira email, Jira base URL, and Jira API token
  - run the first step of `gog` auth, send the auth URL to the user, receive the redirect URL, and finish auth

## Files of interest

- `clawjection.yaml`
- `main.py`
- `skills/jira-acli/SKILL.md`
- `docs/OVERVIEW.md`
