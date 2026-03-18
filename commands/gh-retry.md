---
name: gh-retry
description: Rerun all failed and cancelled workflow runs for a GitHub PR or all my PRs in a repo
argument-hint: "[PR number/URL/reference, or repo URL/owner/repo]"
allowed-tools: Bash
---

Rerun all failed workflow runs: $ARGUMENTS

## Step 1: Determine mode and collect PRs

Parse the argument to determine if this is a **single PR** or **all my PRs in a repo**:

- **Single PR**: A PR number (e.g., `123`), PR URL (e.g., `https://github.com/owner/repo/pull/123`), or PR reference (e.g., `owner/repo#123`)
- **Repo-wide**: A repo URL (e.g., `https://github.com/owner/repo`), or `owner/repo` without a PR number — list all open PRs by the current user:
  ```bash
  gh pr list --repo <owner/repo> --author @me --json number,title,headRefOid
  ```

## Step 2: For each PR, get the head SHA

```bash
gh pr view <pr> --json headRefOid -q .headRefOid
```

## Step 3: List all workflow runs for that commit SHA

```bash
gh run list --repo <owner/repo> --commit <sha> --json databaseId,name,conclusion,status
```

## Step 4: Identify failures

Identify workflows with conclusion "failure" or "cancelled". If all workflows are still "queued" or "in_progress" with no failures, check GitHub Actions status before reporting:
```bash
curl -s https://www.githubstatus.com/api/v2/components.json | jq '.components[] | select(.name == "Actions") | {name, status}'
```
If Actions is degraded or has a major outage, inform the user that GitHub Actions is experiencing issues and their runs may be stuck. Otherwise, report that all workflows are passing or pending.

## Step 5: Get failed jobs for each failed workflow run

```bash
gh run view <run-id> --repo <owner/repo> --json jobs --jq '.jobs[] | {name, conclusion}'
```

## Step 6: Display a tree and rerun failed jobs

Always group by PR:

```
Workflows to rerun:
PR #123 - Add feature X
├── **Build** (`21610828075`)
│   ├── Build - Ubuntu (failure)
│   ├── Build - Windows (failure)
│   └── Build - macOS (failure)
└── **Coverage** (`21610828076`)
    └── Coverage - Windows (failure)
PR #456 - Fix bug Y
└── **Orchestrator** (`21610828077`)
    └── Coverage - Windows (failure)
```
- Workflow names should be **bold**
- Run IDs should be in `backticks`
- Only show jobs with conclusion "failure" or "cancelled" in the tree (these are the ones that will be rerun)

Immediately rerun without asking for confirmation (rerunning is non-destructive):
```bash
gh run rerun <run-id> --repo <owner/repo> --failed
```

## Step 7: Report what was rerun
