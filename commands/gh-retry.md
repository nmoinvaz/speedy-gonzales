---
name: gh-retry
description: Rerun all failed and cancelled workflow runs for a GitHub PR or all my PRs in a repo
argument-hint: "[PR number/URL/reference, or repo URL/owner/repo]"
allowed-tools: Bash
---

Rerun all failed workflow runs: $ARGUMENTS

## Step 1: Rerun

Pass the argument through. `gh arriba` treats a PR number, PR URL, or `owner/repo#123` as a
**single PR**, and a repo URL or `owner/repo` as **all my open PRs in that repo**:

```bash
gh arriba pr retry $ARGUMENTS
```

Rerunning is non-destructive, so it reruns immediately without asking. For each PR it:
- Reads the current check status of the head commit, keeping only the latest attempt of each check
  so earlier reruns are not counted as failures
- Prints a tree of the failed and cancelled jobs grouped by PR and workflow run, with run IDs
- Reruns only the failed jobs of each run
- Lists failed external statuses that are not GitHub Actions as skipped, since they can't be rerun
- When nothing failed but checks are still pending, checks githubstatus.com and warns if GitHub
  Actions is degraded or has an outage

## Step 2: Report what was rerun

Relay the tree it printed. Call out any run that could not be rerun and why, such as a run still in
progress, and any GitHub Actions outage warning. If nothing failed, report that all checks are
passing or pending.
