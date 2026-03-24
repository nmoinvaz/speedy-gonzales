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

## Step 2: For each PR, get the current check status

Use `gh pr checks` to get the authoritative, current state of all checks
for the PR. This correctly reflects rerun results, unlike `gh run list`
which can show stale job data from before a rerun completed.

```bash
gh pr checks <pr> --repo <owner/repo>
```

## Step 3: Identify failures

Parse the `gh pr checks` output for checks with status "fail" or
"cancelled". If all checks are still "pending" with no failures, check
GitHub Actions status before reporting:
```bash
curl -s https://www.githubstatus.com/api/v2/components.json | jq '.components[] | select(.name == "Actions") | {name, status}'
```
If Actions is degraded or has a major outage, inform the user that GitHub Actions is experiencing issues and their runs may be stuck. Otherwise, report that all checks are passing or pending.

## Step 4: Extract run IDs from failed checks

Each failed check URL contains the run ID (e.g.,
`https://github.com/owner/repo/actions/runs/12345/job/67890`). Extract
the unique run IDs from the URLs of all failed and cancelled checks.

## Step 5: Display a tree and rerun failed jobs

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

## Step 6: Report what was rerun
