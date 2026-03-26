#!/usr/bin/env python3
"""Reference ClawJection entrypoint for the Jira project manager example."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

IDENTITY_MARKER = "<!-- CLAWJECTION_JIRA_PM_IDENTITY -->"
SOUL_MARKER = "<!-- CLAWJECTION_JIRA_PM_SOUL -->"
AGENTS_MARKER = "<!-- CLAWJECTION_JIRA_PM_AGENTS -->"
TOOLS_MARKER = "<!-- CLAWJECTION_JIRA_PM_TOOLS -->"
MEMORY_MARKER = "<!-- CLAWJECTION_JIRA_PM_MEMORY -->"
DAILY_MEMORY_MARKER = "<!-- CLAWJECTION_JIRA_PM_DAILY_MEMORY -->"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
DEFAULT_ACLI_URL = "https://acli.atlassian.com/linux/latest/acli_linux_amd64/acli"


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

    cli_targets = install_clis(runtime["workspace_path"])
    changes = apply_workspace_changes(runtime["workspace_path"], cli_targets)
    skill_target = install_bundled_skill(runtime["workspace_path"])
    install_clawhub_skill(runtime["workspace_path"], "gog")

    payload = {
        "status": "needs_user_action",
        "summary": "Configured the workspace for Jira-based project management, installed the bundled Jira skill plus the ClawHub gog skill, and seeded agent operating files.",
        "changed_files": [
            to_relative_label(path, runtime["workspace_path"])
            for path in [*changes, skill_target, *cli_targets.values()]
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
                "instruction": "Ask the user for Jira base URL, Jira account email, and Jira API token. Store them as JIRA_SITE, JIRA_EMAIL, and JIRA_API_TOKEN without writing the raw token into workspace files.",
                "blocking": True,
                "notes": "Use the exact user-provided Jira site and email. Do not guess or substitute placeholders.",
            },
            {
                "id": "install-gog-oauth-credentials",
                "instruction": "Ask the user to create a Google Cloud Desktop OAuth client, enable the main Google APIs needed for this workflow, and either send you the client JSON file directly or provide its contents through an environment-backed secret that you can read. Then write that JSON locally on the host and run `gog auth credentials <path-to-client-secret.json>` yourself.",
                "blocking": True,
                "notes": "This step must happen before any `gog auth add ...` flow. Without stored OAuth client credentials, gog account auth will fail. The user should not need to run gog commands manually. At minimum, ask them to enable Google Calendar API, Gmail API, Google Drive API, and People API if contact/profile access will be needed.",
            },
            {
                "id": "complete-gog-auth",
                "instruction": "After you have the Jira email and have installed the gog OAuth client credentials, run `gog auth add <jira-email> --services user --manual`, send the printed auth URL to the user, ask the user to return the full redirect URL after authenticating, then finish the gog auth flow with that redirect URL.",
                "blocking": True,
                "notes": "Pause until the user replies with the redirect URL. Do not continue with placeholder auth data.",
            },
        ],
        "artifacts": [
            str(runtime["config_path"]),
            str(runtime["workspace_path"]),
            *(str(path) for path in cli_targets.values()),
        ],
    }
    print("FOLLOWUPS:", file=sys.stdout)
    for idx, followup in enumerate(payload["followups"], start=1):
        print(f"{idx}. {followup['instruction']}", file=sys.stdout)
        notes = followup.get("notes")
        if isinstance(notes, str) and notes:
            print(f"   notes: {notes}", file=sys.stdout)
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


def apply_workspace_changes(
    workspace_path: Path, cli_targets: dict[str, Path]
) -> list[Path]:
    workspace_path.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    changed: list[Path] = []

    identity_path = workspace_path / "IDENTITY.md"
    write_identity(identity_path)
    changed.append(identity_path)

    soul_path = workspace_path / "SOUL.md"
    soul_block = read_asset("SOUL.md")
    upsert_managed_section(soul_path, "# Soul", soul_block, SOUL_MARKER)
    changed.append(soul_path)

    agents_path = workspace_path / "AGENTS.md"
    agents_block = read_asset("AGENTS.md")
    upsert_managed_section(agents_path, "# Agents", agents_block, AGENTS_MARKER)
    changed.append(agents_path)

    tools_path = workspace_path / "TOOLS.md"
    tools_block = read_asset(
        "TOOLS.md",
        {
            "acli_command": str(cli_targets["acli"]),
            "gog_command": str(cli_targets["gog"]),
        },
    )
    upsert_managed_section(tools_path, "# Tools", tools_block, TOOLS_MARKER)
    changed.append(tools_path)

    memory_path = workspace_path / "MEMORY.md"
    memory_block = read_asset("MEMORY.md")
    upsert_managed_section(memory_path, "# Memory", memory_block, MEMORY_MARKER)
    changed.append(memory_path)

    daily_memory_path = workspace_path / "memory" / f"{today}.md"
    daily_memory_block = read_asset("daily-memory.md", {"today": today})
    upsert_managed_section(daily_memory_path, f"# {today}", daily_memory_block, DAILY_MEMORY_MARKER)
    changed.append(daily_memory_path)

    return changed


def install_bundled_skill(workspace_path: Path) -> Path:
    source_skill = Path(__file__).resolve().parent / "skills" / "jira-acli" / "SKILL.md"
    target_skill = workspace_path / "skills" / "jira-acli" / "SKILL.md"
    target_skill.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_skill, target_skill)
    return target_skill


def install_clis(workspace_path: Path) -> dict[str, Path]:
    bin_dir = workspace_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    acli_target = bin_dir / "acli"
    install_acli(acli_target)

    gog_target = bin_dir / "gog"
    install_gog(gog_target)

    return {
        "acli": acli_target,
        "gog": gog_target,
    }


def install_acli(target: Path) -> None:
    acli_url = os.environ.get("CLAWJECTION_ACLI_URL", DEFAULT_ACLI_URL)
    subprocess.run(
        ["curl", "-fsSL", acli_url, "-o", str(target)],
        check=True,
    )
    target.chmod(0o755)


def install_gog(target: Path) -> None:
    brew_bin = resolve_brew_bin()
    subprocess.run([brew_bin, "install", "gogcli"], check=True)
    brew_prefix = subprocess.run(
        [brew_bin, "--prefix"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    brewed_gog = Path(brew_prefix) / "bin" / "gog"
    if not brewed_gog.exists():
        raise FileNotFoundError(f"Expected gog binary at {brewed_gog}")

    if target.exists() or target.is_symlink():
        target.unlink()
    target.symlink_to(brewed_gog)


def resolve_brew_bin() -> str:
    configured = os.environ.get("CLAWJECTION_BREW_BIN")
    candidates = [
        configured,
        "/home/node/linuxbrew/bin/brew",
        shutil.which("brew"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise FileNotFoundError("Could not find Homebrew binary for gogcli installation")


def install_clawhub_skill(workspace_path: Path, skill_name: str) -> None:
    clawhub_bin = os.environ.get("CLAWJECTION_CLAWHUB_BIN", "clawhub")
    subprocess.run(
        [clawhub_bin, "install", skill_name],
        cwd=workspace_path,
        check=True,
    )


def read_asset(name: str, replacements: dict[str, str] | None = None) -> str:
    content = (ASSETS_DIR / name).read_text(encoding="utf-8")
    for key, value in (replacements or {}).items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def write_identity(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(read_asset("IDENTITY.md").rstrip() + "\n", encoding="utf-8")


def upsert_managed_section(path: Path, title: str, block: str, marker: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    path.parent.mkdir(parents=True, exist_ok=True)

    if marker in existing:
        path.write_text(replace_section(existing, block, marker), encoding="utf-8")
        return

    rendered = block.rstrip() + "\n"
    if existing.strip():
        path.write_text(existing.rstrip() + "\n\n" + rendered, encoding="utf-8")
    else:
        path.write_text(title.rstrip() + "\n\n" + rendered, encoding="utf-8")


def replace_section(existing: str, block: str, marker: str) -> str:
    rendered = block.rstrip()
    before, current = existing.split(marker, 1)
    after = ""

    marker_index = current.find("<!-- ", 1)
    if marker_index != -1:
        after = current[marker_index:].lstrip()

    updated = before.rstrip()
    if updated:
        updated += "\n\n"
    updated += rendered
    if after:
        updated += "\n\n" + after.rstrip()
    return updated.rstrip() + "\n"


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
            if isinstance(candidate, list):
                for item in candidate:
                    if isinstance(item, dict):
                        workspace = item.get("workspace")
                        if isinstance(workspace, str) and workspace.strip():
                            return Path(workspace).expanduser()

    return fallback


def write_result(payload: dict[str, object]) -> int:
    result_path = os.environ.get("CLAWJECTION_RESULT_PATH", "clawjection-result.json")
    Path(result_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
