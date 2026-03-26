# Minimal Example

This is the smallest ClawJection example in this repository.

## What the agent should do

1. Read `clawjection.yaml`.
2. Resolve the entrypoint as `run.sh`.
3. Run the entrypoint with the `apply` action.
4. By default, let the entrypoint discover OpenClaw config from `~/.openclaw/openclaw.json`.
5. If needed, pass `--openclaw-config-path <path>` to override the default config path.
6. Read the result JSON from `CLAWJECTION_RESULT_PATH`.

## Example invocation

```bash
bash run.sh apply
```

With explicit config override:

```bash
bash run.sh apply --openclaw-config-path /path/to/openclaw.json
```

## What this example demonstrates

- minimal manifest shape
- basic entrypoint invocation
- default OpenClaw config discovery
- writing a result payload
