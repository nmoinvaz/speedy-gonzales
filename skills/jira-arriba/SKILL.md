---
name: jira-arriba
description: Jira operations with the jira-arriba CLI, for issues, JQL search, transitions, attachments, and comments or descriptions written in Markdown
allowed-tools: Bash(jira-arriba --version), Bash(jira-arriba auth status)
---

# jira-arriba Quick Reference

[jira-arriba](https://github.com/nmoinvaz/jira-arriba) is the CLI this project's Jira workflows use.
It takes Markdown wherever Jira wants rich text and converts it to ADF, so comments and descriptions
are never written as JSON by hand.

## Prerequisites

Installed version and login:

!`jira-arriba --version 2>&1 || echo "jira-arriba is not installed"`

!`jira-arriba auth status 2>&1 || true`

If it is not installed, tell the user to download it from the
[releases](https://github.com/nmoinvaz/jira-arriba/releases) and put it on the `PATH`, or run
`cargo install --git https://github.com/nmoinvaz/jira-arriba`, and stop.

If there is no login, tell the user to run `jira-arriba auth login`, which signs in through acli in
the browser and offers to install acli when it is missing, and stop. `JIRA_API_TOKEN`, `JIRA_EMAIL`,
and `JIRA_SITE` in the environment work without acli.

## Conventions

- Every `KEY` argument also accepts the issue's URL, so pass `https://x.atlassian.net/browse/PROJ-123` as is.
- Add `--json` to any command whose output you need to parse.
- `comment delete` and `attachment delete` ask before acting, `--yes` skips the prompt.
- Pass `--site mysite.atlassian.net` when acli holds logins for several sites.

## View an Issue

Summary, status, people, dates, labels, description, comments, and attachments, with rich text as
Markdown:

```bash
jira-arriba issue view PROJ-123
jira-arriba issue view PROJ-123 --json
jira-arriba issue view PROJ-123 --fields summary,status,priority,components
jira-arriba issue view PROJ-123 --all      # every field, custom ones included
```

## Search with JQL

```bash
jira-arriba issue search --jql 'text ~ "search terms" AND key != PROJ-123' --json
jira-arriba issue search --jql 'component = "my-component" AND status != Closed' --fields key,summary,status --limit 20
jira-arriba issue search --jql 'project = PROJ AND resolved >= -30d' --all
```

Jira tokenizes hyphenated IDs such as CVEs badly in the `text` field, so search those with
`summary ~ "CVE-2024-1234"`.

## Comments

Bodies are Markdown, from the argument, a file, or stdin. Headings, lists, task lists, tables, code
blocks, links, and `> [!NOTE]` style alerts all convert to ADF.

```bash
jira-arriba issue comment list PROJ-123
jira-arriba issue comment add PROJ-123 "Fixed in commit abc123, see the PR for details."
jira-arriba issue comment add PROJ-123 --file comment.md
jira-arriba issue comment add PROJ-123 <<'MD'
## Root cause

The cache was keyed by path, so a renamed file kept its stale entry.

- Fixed in `src/cache.rs`
- Covered by `cache_follows_renames`
MD
jira-arriba issue comment edit PROJ-123 10001 --file comment.md
jira-arriba issue comment delete PROJ-123 10001 --yes
```

Comment IDs come from `issue comment list --json` or `issue view --json`.

## Transition an Issue

List where the issue can go, then move it. Status names match ignoring case.

```bash
jira-arriba issue transition PROJ-123 --list
jira-arriba issue transition PROJ-123 --status "In Progress"
jira-arriba issue transition PROJ-123 --status Resolved
```

## Create an Issue

```bash
jira-arriba issue create --project PROJ --type Bug --summary "Crash on start" \
  --description-file description.md --assignee @me --label bug --label triage
```

`--description` takes inline Markdown, `--parent` makes a sub-task or places a story under an epic,
and `--from-json` reads a file in acli's `--generate-json` layout with flags overriding its fields.

## Edit an Issue

```bash
jira-arriba issue edit PROJ-123 --summary "Updated summary"
jira-arriba issue edit PROJ-123 --description-file description.md
jira-arriba issue edit PROJ-123 --assignee @me --add-label needs-review --remove-label triage
jira-arriba issue edit PROJ-123 --assignee none     # unassign
```

## Attachments

Attachments are found in the issue's attachment field, its changelog, and the inline images and
links of the description and comments, so pasted screenshots download even when the Attachment
field is hidden. Zip files are extracted into sibling folders.

```bash
jira-arriba attachment list PROJ-123
jira-arriba attachment download PROJ-123 --dir ./PROJ-123
jira-arriba attachment download PROJ-123 --name '*.log' --name '*.txt' --no-extract
jira-arriba attachment upload PROJ-123 crash.log screenshot.png
jira-arriba attachment delete 10042 --yes
```

Without `--dir`, downloads go to a `jira-arriba/PROJ-123` folder in the temp directory, and the
command prints the path.

## Projects

```bash
jira-arriba project list
jira-arriba project list --query platform
```

## ADF and Raw API Calls

Convert Markdown to ADF, or ADF JSON from the API back to Markdown:

```bash
jira-arriba adf from-md comment.md
jira-arriba adf to-md issue.json
```

For a REST call jira-arriba has no command for, reuse its login. The acli login is OAuth, which
Atlassian only accepts through its gateway with the site's cloud ID, and `@<(...)` keeps the header
out of the process list:

```bash
CLOUD_ID=$(jira-arriba auth status --json | jq -r .cloudId)
curl -sS -H @<(jira-arriba auth token --header) \
  "https://api.atlassian.com/ex/jira/$CLOUD_ID/rest/api/3/myself"
```

With a `JIRA_API_TOKEN` login the header is basic auth and the base is `https://<site>/rest/api/3`.

## Notifications

`jira-arriba notify watch` polls your issues and raises a desktop notification for each assignment,
status change, comment, or mention. `--install` keeps it running from login, `--uninstall` stops it,
and `--once --since 2h` replays recent activity and exits.
