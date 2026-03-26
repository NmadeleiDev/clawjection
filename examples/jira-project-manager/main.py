#!/usr/bin/env python3
"""Illustrative ClawJection entrypoint for the Jira project manager example."""

from __future__ import annotations

import argparse
import json
import os
import sys
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

    payload = {
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
        "followups": [
            {
                "id": "collect-jira-credentials",
                "instruction": "Ask the user for Jira email, Jira base URL, and Jira API token.",
                "blocking": True,
            },
            {
                "id": "complete-gog-auth",
                "instruction": "Run the first step of gog auth, send the user the auth URL, get the redirect URL back from the user, and finish auth.",
                "blocking": True,
                "notes": "Use the collected Jira email when constructing the gog auth command.",
            },
        ],
        "artifacts": [
            str(runtime["config_path"]),
            str(runtime["workspace_path"]),
        ],
    }
    print("FOLLOWUPS:", file=sys.stdout)
    for idx, followup in enumerate(payload["followups"], start=1):
        print(f"{idx}. {followup['instruction']}", file=sys.stdout)
    return write_result(payload)


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
