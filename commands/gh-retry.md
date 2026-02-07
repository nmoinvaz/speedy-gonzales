---
name: gh-retry
description: Rerun all failed and cancelled workflow runs for a GitHub PR
argument-hint: "[PR number, URL, or reference]"
allowed-tools: Bash
---

Rerun all failed workflow runs for the given GitHub PR: $ARGUMENTS

1. Parse the PR identifier from the arguments. It can be:
   - A PR number (e.g., `123`)
   - A PR URL (e.g., `https://github.com/owner/repo/pull/123`)
   - A PR reference with repo (e.g., `owner/repo#123`)

2. Get the head SHA of the PR:
   ```bash
   gh pr view <pr> --json headRefOid -q .headRefOid
   ```

3. List all workflow runs for that commit SHA:
   ```bash
   gh run list --repo <owner/repo> --commit <sha> --json databaseId,name,conclusion,status
   ```

4. Identify workflows with conclusion "failure" or "cancelled". If there are none, report that all workflows are passing or pending.

5. For each failed or cancelled workflow run, get the jobs:
   ```bash
   gh run view <run-id> --repo <owner/repo> --json jobs --jq '.jobs[] | {name, conclusion}'
   ```

6. Display a tree showing what will be rerun, then ask for confirmation:
   ```
   Workflows to rerun:
   ├── **Build** (`21610828075`)
   │   ├── Build - Ubuntu (failure)
   │   ├── Build - Windows (failure)
   │   └── Build - macOS (failure)
   └── **Coverage** (`21610828076`)
       └── Coverage - Windows (failure)

   Proceed with rerun?
   ```
   - Workflow names should be **bold**
   - Run IDs should be in `backticks`
   - Only show jobs with conclusion "failure" or "cancelled" in the tree (these are the ones that will be rerun)

7. Once confirmed, for each workflow rerun only the failed jobs:
   ```bash
   gh run rerun <run-id> --repo <owner/repo> --failed
   ```

8. Report what was rerun.
