#!/usr/bin/env python3
"""Illustrative ClawJection entrypoint for the Jira project manager example."""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> int:
    action = os.environ.get("CLAWJECTION_ACTION") or "apply"
    if action != "apply":
        return write_result(
            {
                "status": "ok",
                "summary": f"Action '{action}' is not implemented in this example."
            }
        )

    return write_result(
        {
            "status": "needs_user_action",
            "summary": "Configured Jira project manager example and installed local tooling.",
            "changed_files": [
                "workspace/IDENTITY.md",
                "workspace/AGENTS.md",
                "workspace/memory.md",
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
                    "input_key": "jira_api_token",
                },
            ],
            "agent_followup": {
                "mode": "ask_user",
                "priority": "blocking",
                "instruction": "Ask the user to complete the first-step gog auth flow and send back the returned auth value, then complete the second gog auth step and finally ask for the Jira API token.",
            },
        }
    )


def write_result(payload: dict[str, object]) -> int:
    result_path = os.environ.get("CLAWJECTION_RESULT_PATH", "clawjection-result.json")
    Path(result_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
