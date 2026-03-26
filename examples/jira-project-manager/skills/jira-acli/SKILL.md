---
name: jira-acli
description: Use ACLI for Jira issues, projects, work items, JQL searches, transitions, and Atlassian CLI auth. Trigger when working with Jira operations or ACLI authentication/setup.
---

# Jira ACLI

Use this skill for Jira work via ACLI.

## Local environment

- Jira site: from `JIRA_SITE` environment variable
- Account email: from `JIRA_EMAIL` environment variable
- API token source: environment variable `JIRA_API_TOKEN`
- ACLI command: `acli`

Do not write raw API tokens into files. Read from `JIRA_API_TOKEN` only. If `JIRA_API_TOKEN` is not set, ask the user to get it at https://id.atlassian.com/manage-profile/security/api-tokens and add it to the environment variable.

## CLI shape

Use ACLI in this general form:

```bash
acli <product> <entity> <action> [flags]
```

For Jira, common patterns are:

```bash
acli jira auth <login|status|logout|switch>
acli jira workitem <create|edit|transition>
```

## Recommended workflow

1. Check required env vars exist: `JIRA_SITE`, `JIRA_EMAIL`, and `JIRA_API_TOKEN`.
2. Verify auth first:

```bash
acli jira auth status
```

3. If not authenticated, log in with stdin token:

```bash
printf "%s" "$JIRA_API_TOKEN" | acli jira auth login \
  --site "$JIRA_SITE" \
  --email "$JIRA_EMAIL" \
  --token
```

4. Use `--help` on target commands before guessing flags:

```bash
acli jira --help
acli jira workitem --help
acli jira workitem create --help
```

## Getting started reference

- API token auth can be piped on stdin.
- OAuth login may be available via `acli jira auth login --web` depending on ACLI version.
- Work-item operations are typically centered on `acli jira workitem ...`.
- Prefer built-in `--help` because ACLI syntax can change across versions.

## Common examples

Create a work item:

```bash
acli jira workitem create --summary "New Task" --project "TEAM" --type "Task"
```

Edit work items by key:

```bash
acli jira workitem edit --key "KEY-1,KEY-2" --summary "New Summary"
```

Transition work items:

```bash
acli jira workitem transition --key "KEY-1,KEY-2" --status "Done"
```

## Safety notes

- Never persist raw API tokens in workspace files.
- Prefer env vars or stdin redirection for secrets.
- Confirm destructive or bulk-edit operations before running them.
