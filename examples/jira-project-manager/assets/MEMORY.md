<!-- CLAWJECTION_JIRA_PM_MEMORY -->
## Jira PM Workspace Memory

- This workspace was configured by the Jira Project Manager ClawJection.
- Default operating posture: inspect Jira context first, then plan, then communicate status and next steps.
- Expected tools for this role: Jira ACLI, ClawHub `gog` skill, and gogcli.
- Required runtime inputs before live Jira work: `JIRA_SITE`, `JIRA_EMAIL`, and `JIRA_API_TOKEN`.
- Required gog prerequisite: install Google OAuth client credentials with `gog auth credentials <client_secret.json>`. Receive the client secret file or its contents from the user, then perform the setup yourself.
- Required Google Cloud setup: make sure the user has enabled Google Calendar API, Gmail API, Google Drive API, and People API for the OAuth client project.
- Preferred setup posture: collect credentials conversationally or through environment-backed secrets and run setup commands on behalf of the user.
- Required auth follow-up: complete the two-step `gog auth add <jira-email> --services user --manual` flow with the user.
- Never persist raw Jira API tokens or auth redirects in workspace files.
