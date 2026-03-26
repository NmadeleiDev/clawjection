# ClawJection

ClawJection is a lightweight bundle standard for turning an OpenClaw instance into a role-specific operator.

A ClawJection bundle has one standardized file, `clawjection.yaml`, plus an entrypoint declared by that manifest. Everything else in the bundle is arbitrary and pack-defined.

The core flow is:

1. A user gives an OpenClaw agent a ClawJection source.
2. The agent reads `clawjection.yaml`.
3. The agent runs the declared entrypoint.
4. The entrypoint modifies the local OpenClaw runtime.
5. The entrypoint returns structured results, including what the agent should ask the user to do next.

## Status

This repository currently contains a draft v1 standard, JSON schemas, and example bundles. The standard is intentionally small so it can be implemented quickly by agents and hosts.

## Repository Layout

- `standard/`
  - human-readable standard drafts
- `schemas/`
  - machine-readable JSON Schemas for manifests and result files
- `examples/`
  - reference example bundles

## What Is Standardized

- `clawjection.yaml`
- bundle root detection rules
- manifest fields
- entrypoint execution contract
- default OpenClaw config discovery via `~/.openclaw/openclaw.json`
- result JSON contract
- structured post-install handoff via ordered `followups`

## What Is Not Standardized

- internal bundle directory names
- interpreter selection
- uninstall and rollback
- registry APIs
- signature verification
- host-specific security enforcement

## Why The Result Contract Matters

ClawJection is not only about file mutation. Many real bundles need a human handoff after install.

Example:
- install `gogcli`
- install the ClawHub `gog` skill
- install a Jira ACLI skill from bundled text
- then tell the agent to ask the user to complete the first step of `gog auth add`, open the printed auth URL locally, and send back the returned auth value
- then tell the agent to ask for a Jira API token

That is why the v1 result schema includes:
- `followups`

## Quick Start

Read the standard:
- [`standard/v1.md`](standard/v1.md)

By default, bundles should discover the target runtime from `~/.openclaw/openclaw.json`. When needed, entrypoints may also support `--openclaw-config-path`.

Validate manifests/results against the schemas:
- [`schemas/clawjection.schema.json`](schemas/clawjection.schema.json)
- [`schemas/result.schema.json`](schemas/result.schema.json)

Inspect examples:
- [`examples/minimal`](examples/minimal)
- [`examples/jira-project-manager`](examples/jira-project-manager)

## Example Bundles

`examples/minimal`
- smallest possible bundle

`examples/jira-project-manager`
- non-trivial example
- installs local tooling
- installs a bundled Jira skill
- installs `https://clawhub.ai/steipete/gog`
- returns ordered follow-up instructions for credential collection and auth

## Design Principles

- Only standardize what agents actually need.
- Keep bundle internals flexible.
- Make post-install handoff first-class.
- Let hosts apply stricter policy without redefining the format.

## Open Questions

- Whether lifecycle verbs beyond `apply` should become mandatory
- Whether provenance/signatures should be required in a later version

## License

MIT
