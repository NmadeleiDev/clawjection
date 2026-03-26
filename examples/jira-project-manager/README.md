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
- overwrites `IDENTITY.md` with a filled Jira project-manager identity
- writes `SOUL.md`
- appends or updates a managed Jira tooling block in `TOOLS.md`
- writes `MEMORY.md`
- appends or updates a Jira project-manager block in `AGENTS.md`
- seeds the daily memory log in `memory/YYYY-MM-DD.md`
- installs CLI wrappers in `bin/acli` and `bin/gog`
- installs the bundled Jira ACLI skill into `skills/jira-acli/SKILL.md`
- runs `clawhub install gog` to install the ClawHub `gog` skill
- returns ordered `followups` telling the agent to:
  - ask the user for Jira base URL, Jira email, and Jira API token
  - ask the user to enable the main Google APIs, send Google OAuth client credentials or provide them through environment-backed secret input, then run `gog auth credentials <path-to-client-secret.json>` on the host
  - run `gog auth add <jira-email> --services user --manual`, send the auth URL to the user, receive the redirect URL, and finish auth

This example treats `IDENTITY.md` as part of the role switch. Running it replaces the existing identity file with the bundled Jira project-manager identity.

## Files of interest

- `clawjection.yaml`
- `main.py`
- `assets/`
- `skills/jira-acli/SKILL.md`
- `docs/OVERVIEW.md`
