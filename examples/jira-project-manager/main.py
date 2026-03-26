#!/usr/bin/env python3
"""Reference ClawJection entrypoint for the Jira project manager example."""

from __future__ import annotations

import argparse
import shutil
import json
import os
import sys
from pathlib import Path

AGENTS_MARKER = "<!-- CLAWJECTION_JIRA_PROJECT_MANAGER -->"
MEMORY_MARKER = "<!-- CLAWJECTION_JIRA_MEMORY -->"


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

    changes = apply_workspace_changes(runtime["workspace_path"])
    skill_target = install_bundled_skill(runtime["workspace_path"])

    payload = {
        "status": "needs_user_action",
        "summary": "Configured Jira project manager example, updated workspace files, and installed the bundled Jira skill.",
        "changed_files": [
            to_relative_label(path, runtime["workspace_path"])
            for path in [*changes, skill_target]
        ],
        "installed_packages": [
            "gogcli",
            "atlassian-cli",
        ],
        "installed_skills": [
            to_relative_label(skill_target, runtime["workspace_path"]),
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


def apply_workspace_changes(workspace_path: Path) -> list[Path]:
    workspace_path.mkdir(parents=True, exist_ok=True)

    identity_path = workspace_path / "IDENTITY.md"
    identity_content = (
        "# Identity\n\n"
        "You are a project manager focused on Jira-based planning, execution, tracking, and follow-up.\n"
    )
    identity_path.write_text(identity_content, encoding="utf-8")

    agents_path = workspace_path / "AGENTS.md"
    agents_block = (
        f"{AGENTS_MARKER}\n"
        "## Jira Project Manager Mode\n\n"
        "- Prefer Jira as the source of truth for work tracking.\n"
        "- Use the bundled Jira ACLI skill for Jira operations.\n"
        "- Use the ClawHub `gog` skill for Google account and auth workflows.\n"
        "- Ask the user for missing credentials instead of guessing them.\n"
    )
    append_once(agents_path, agents_block, AGENTS_MARKER)

    memory_path = workspace_path / "memory.md"
    memory_block = (
        f"{MEMORY_MARKER}\n"
        "- This agent was configured by the Jira Project Manager ClawJection.\n"
        "- Default posture: gather Jira context first, then plan, then execute.\n"
    )
    append_once(memory_path, memory_block, MEMORY_MARKER)

    return [identity_path, agents_path, memory_path]


def install_bundled_skill(workspace_path: Path) -> Path:
    source_skill = Path(__file__).resolve().parent / "skills" / "jira-acli" / "SKILL.md"
    target_skill = workspace_path / "skills" / "jira-acli" / "SKILL.md"
    target_skill.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_skill, target_skill)
    return target_skill


def append_once(path: Path, block: str, marker: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in existing:
        return

    prefix = existing.rstrip()
    rendered = block.rstrip() + "\n"
    if prefix:
        path.write_text(prefix + "\n\n" + rendered, encoding="utf-8")
    else:
        path.write_text(rendered, encoding="utf-8")


def to_relative_label(path: Path, workspace_path: Path) -> str:
    try:
        relative = path.relative_to(workspace_path)
    except ValueError:
        return str(path)
    return f"{workspace_path.name}/{relative.as_posix()}"


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
