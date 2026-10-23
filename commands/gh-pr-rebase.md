---
name: gh-pr-rebase
description: Rebase a GitHub PR onto its base branch
argument-hint: "[PR URL or number]"
allowed-tools: Bash
---

Rebase a GitHub PR onto its base branch.

## Arguments

$ARGUMENTS should be a GitHub PR URL (e.g., https://github.com/owner/repo/pull/123) or PR number, or empty to use the current branch's PR.

## Instructions

1. Ask the user which rebase method they prefer:
   - **Local rebase (signed commits)** - Rebases locally using your GPG key, then pushes. Commits will show as "Verified" with your signature.
   - **Remote rebase (unsigned)** - Uses GitHub API to rebase server-side. Faster but commits won't be signed.

2. **If remote rebase**:
   ```bash
   gh arriba pr rebase $ARGUMENTS --remote
   ```

3. **If local rebase**, run it from a clone of the PR's base repository:
   ```bash
   gh arriba pr rebase $ARGUMENTS
   ```
   - When the checked-out branch is the PR's head branch, it rebases in place
   - Otherwise it rebases in a temporary worktree, so the current checkout is left alone
   - It pushes with a lease on the PR head, so commits someone else pushed are never overwritten

   Both methods comment "Rebased." on the PR after a successful rebase.

4. Report the result to the user:
   - On success: Confirm the PR was rebased (and whether commits are signed)
   - Already up to date: Say so, nothing was pushed
   - On conflicts: List the conflicting files it printed and tell the user they need to resolve them manually
   - On failure: Explain the error (common issues: uncommitted changes, a local branch missing commits from the PR, or a PR from a fork, which needs the remote method)
