#!/usr/bin/env python3
"""Illustrative ClawJection entrypoint for the Jira project manager example."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> int:
    args = parse_args()
    action = os.environ.get("CLAWJECTION_ACTION") or args.action or "apply"
    runtime = resolve_openclaw_runtime(args.openclaw_config_path)

    if action != "apply":
        return write_result(
            {
                "status": "ok",
                "summary": f"Action '{action}' is not implemented in this example.",
                "artifacts": [str(runtime["config_path"])],
            }
        )

    return write_result(
        {
            "status": "needs_user_action",
            "summary": "Configured Jira project manager example and installed local tooling.",
            "changed_files": [
                f"{runtime['workspace_label']}/IDENTITY.md",
                f"{runtime['workspace_label']}/AGENTS.md",
                f"{runtime['workspace_label']}/memory.md",
            ],
            "installed_packages": [
                "gogcli",
                "atlassian-cli",
            ],
            "installed_skills": [
                "bundle://skills/jira-acli",
                "clawhub.ai/steipete/gog",
            ],
            "user_actions": [
                {
                    "id": "gog-manual-auth",
                    "title": "Start gog remote auth",
                    "instruction": "Tell the user to run the first-step `gog auth add` command in remote/manual mode, open the printed auth URL, finish auth in the browser, and then send back the returned auth value needed for the second step.",
                    "kind": "manual_step",
                    "required": True,
                    "notes": "After the user sends the returned auth value, continue the second-step gog auth flow."
                },
                {
                    "id": "jira-api-token",
                    "title": "Provide Jira API token",
                    "instruction": "Ask the user for a Jira API token and use the runtime's preferred secret flow.",
                    "kind": "provide_input",
                    "required": True,
                    "secret": True,
                },
            ],
            "agent_followup": {
                "mode": "ask_user",
                "priority": "blocking",
                "instruction": "Ask the user to complete the first-step gog auth flow and send back the returned auth value, then complete the second gog auth step and finally ask for the Jira API token.",
            },
            "artifacts": [
                str(runtime["config_path"]),
                str(runtime["workspace_path"]),
            ],
        }
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", default="apply")
    parser.add_argument("--openclaw-config-path")
    return parser.parse_args()


def resolve_openclaw_runtime(cli_config_path: str | None) -> dict[str, Path | str]:
    config_path = Path(
        cli_config_path
        or os.environ.get("CLAWJECTION_OPENCLAW_CONFIG_PATH")
        or Path.home() / ".openclaw" / "openclaw.json"
    ).expanduser()

    workspace_path = Path.home() / ".openclaw" / "workspace"
    if config_path.exists():
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        workspace_path = discover_workspace(payload, workspace_path)

    return {
        "config_path": config_path,
        "workspace_path": workspace_path,
        "workspace_label": workspace_path.name or str(workspace_path),
    }


def discover_workspace(payload: object, fallback: Path) -> Path:
    if not isinstance(payload, dict):
        return fallback

    direct_workspace = payload.get("workspace")
    if isinstance(direct_workspace, str) and direct_workspace.strip():
        return Path(direct_workspace).expanduser()

    agents = payload.get("agents")
    if isinstance(agents, dict):
        for candidate_name in ("main", "default"):
            candidate = agents.get(candidate_name)
            if isinstance(candidate, dict):
                workspace = candidate.get("workspace")
                if isinstance(workspace, str) and workspace.strip():
                    return Path(workspace).expanduser()
        for candidate in agents.values():
            if isinstance(candidate, dict):
                workspace = candidate.get("workspace")
                if isinstance(workspace, str) and workspace.strip():
                    return Path(workspace).expanduser()

    return fallback


def write_result(payload: dict[str, object]) -> int:
    result_path = os.environ.get("CLAWJECTION_RESULT_PATH", "clawjection-result.json")
    Path(result_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
