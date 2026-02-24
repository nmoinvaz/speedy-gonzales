---
name: acli
description: Common Atlassian CLI (acli) commands for Jira operations
---

# Atlassian CLI (acli) Quick Reference

Common `acli` commands for Jira operations used across this project's workflows.

## Prerequisites

- `acli` must be installed and authenticated: `acli jira auth login --web`
- Check auth status: `acli jira auth status`

## View Issue Details

```bash
acli jira workitem view PROJ-123
```

With all fields (description, comments, etc.):

```bash
acli jira workitem view PROJ-123 --fields "*all"
```

JSON output for parsing:

```bash
acli jira workitem view PROJ-123 --json
```

Specific fields only:

```bash
acli jira workitem view PROJ-123 --fields "summary,status,priority,description,comment"
```

## Search Issues with JQL

```bash
acli jira workitem search --jql 'summary ~ "CVE-2024-1234" AND summary ~ "repo-name"' --json
```

Search by text across all fields:

```bash
acli jira workitem search --jql 'text ~ "search terms" AND key != PROJ-123' --json
```

Search by component:

```bash
acli jira workitem search --jql 'component = "my-component" AND key != PROJ-123' --json
```

Search recently resolved issues:

```bash
acli jira workitem search --jql 'text ~ "search terms" AND status in (Resolved, Done, Closed) AND resolved >= -30d' --json
```

Limit results and select fields:

```bash
acli jira workitem search --jql 'project = PROJ' --fields "key,summary,status" --limit 20 --json
```

## Add Comment to Issue

```bash
acli jira workitem comment create --key PROJ-123 --body "Comment text here"
```

Multi-line comment from a file:

```bash
acli jira workitem comment create --key PROJ-123 --body-file comment.txt
```

## List Comments on Issue

```bash
acli jira workitem view PROJ-123 --fields "comment" --json
```

## Transition Issue Status

First check available transitions:

```bash
acli jira workitem view PROJ-123 --fields "status" --json
```

Then transition:

```bash
acli jira workitem transition --key PROJ-123 --status "Done"
acli jira workitem transition --key PROJ-123 --status "In Progress"
acli jira workitem transition --key PROJ-123 --status "Resolved"
```

## Create Issue

```bash
acli jira workitem create --project PROJ --type Bug --summary "Bug title" --description "Description"
```

With assignee and labels:

```bash
acli jira workitem create --project PROJ --type Task --summary "Title" \
  --assignee "user@example.com" --label "bug,triage"
```

## Edit Issue

```bash
acli jira workitem edit --key PROJ-123 --summary "Updated summary"
acli jira workitem edit --key PROJ-123 --assignee "@me"
```

## List Projects

```bash
acli jira project list
```
