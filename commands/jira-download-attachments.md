---
name: jira-download-attachments
description: Download all attachments and inline media from a Jira ticket
argument-hint: "<Jira URL or issue key> [output-dir]"
allowed-tools: Bash, Read
---

Download all attachments and inline media from a Jira ticket: $ARGUMENTS

## Arguments

- `$1`: A Jira URL (e.g., `https://company.atlassian.net/browse/PROJ-123`) or a Jira issue key (e.g., `PROJ-123`). `jira-arriba` accepts either as is.
- `$2` (optional): Output directory. Without it the files land in a `jira-arriba/<issue-key>` folder in the temp directory, and the command prints the path.

## Prerequisites

Load the `/arriba:jira-arriba` skill for command syntax reference. It shows whether `jira-arriba` is installed and logged in. If either is missing, follow the skill's instructions to the user and stop.

## Steps

### 1. Download

```bash
jira-arriba attachment download <ISSUE-KEY-OR-URL> --dir <output-dir>
```

Drop `--dir` when `$2` was not given. The command finds attachments in the issue's attachment field, its changelog, and the inline images and links of the description and comments, follows each file's redirect to its signed media URL, extracts any `.zip` archives into sibling subdirectories, and prints per-file progress with a final summary.

If it reports that the issue has no attachments or inline media, stop and tell the user the ticket has nothing to download.

### 2. Report

List the downloaded files with their sizes, and point out screenshots, logs, and extracted archives the user will likely want to look at first.
