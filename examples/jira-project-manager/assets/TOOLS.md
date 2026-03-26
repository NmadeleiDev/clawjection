<!-- CLAWJECTION_JIRA_PM_TOOLS -->
## Jira Project Manager Tooling

### Jira

- Jira base URL comes from `JIRA_SITE`
- Jira account email comes from `JIRA_EMAIL`
- Jira API token comes from `JIRA_API_TOKEN`
- Never persist raw Jira tokens in workspace files
- Ask your human to add those values to your environment variables. JIRA_API_TOKEN can be generated at https://id.atlassian.com/manage-profile/security/api-tokens.

### ACLI

- Installed command wrapper: `{{acli_command}}`
- Verify auth with `{{acli_command}} jira auth status`
- If needed, authenticate with stdin token:

```bash
printf "%s" "$JIRA_API_TOKEN" | {{acli_command}} jira auth login \
  --site "$JIRA_SITE" \
  --email "$JIRA_EMAIL" \
  --token
```

- Documentation for ACLI: https://developer.atlassian.com/cloud/acli/guides/how-to-get-started/

### gogcli

- Installed command wrapper: `{{gog_command}}`
- Before account auth, set up Google OAuth client credentials and store them with:

```bash
{{gog_command}} auth credentials /path/to/client_secret.json
```

- In Google Cloud, enable the main APIs needed for this workflow before creating or using the client:
  - Google Calendar API
  - Gmail API
  - Google Drive API
  - People API
- The credentials file should be a Google Cloud Desktop OAuth client JSON
- Preferred UX: ask the user to send you the JSON file directly or provide its contents via environment-backed secret input, then write it locally and run `gog auth credentials ...` yourself
- Manual auth flow for this role:

```bash
{{gog_command}} auth add <jira-email> --services user --manual
```

- Send the printed auth URL to the user
- Ask the user to return the full redirect URL
- Finish the auth flow with the returned redirect URL
- Documentation for gogcli: https://github.com/steipete/gogcli
