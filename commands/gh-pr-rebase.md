---
name: gh-pr-rebase
description: Rebase a GitHub PR onto its base branch
argument-hint: "[PR URL]"
allowed-tools: Bash
---

Rebase a GitHub PR onto its base branch.

## Arguments

$ARGUMENTS should be a GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)

## Instructions

1. Parse the PR URL from $ARGUMENTS to extract:
   - Owner
   - Repository name
   - PR number

2. If $ARGUMENTS is empty or not a valid GitHub PR URL, ask the user to provide one.

3. Ask the user which rebase method they prefer:
   - **Local rebase (signed commits)** - Rebases locally using your GPG key, then pushes. Commits will show as "Verified" with your signature.
   - **Remote rebase (unsigned)** - Uses GitHub API to rebase server-side. Faster but commits won't be signed.

4. **If remote rebase**: Use the GitHub CLI:
   ```bash
   gh api repos/{owner}/{repo}/pulls/{pr_number}/update-branch \
     -X PUT \
     -f update_method=rebase
   ```

5. **If local rebase**: Perform a safe local rebase that preserves the current working state:

   a. Get PR details (head branch, base branch):
      ```bash
      gh pr view {pr_number} --repo {owner}/{repo} --json headRefName,baseRefName
      ```

   b. Create a temporary worktree (run from main repo, not /tmp):
      ```bash
      git worktree add /tmp/rebase-pr-{pr_number} -b temp-rebase-{pr_number}
      ```

   c. Fetch latest refs and reset the temp branch to the PR head.
      **Important**: Don't use `gh pr checkout` - it fails if the branch is checked out elsewhere.
      Instead, fetch and reset:
      ```bash
      git -C /tmp/rebase-pr-{pr_number} fetch origin
      git -C /tmp/rebase-pr-{pr_number} reset --hard origin/{head_branch}
      ```

   d. Rebase onto the base branch:
      ```bash
      git -C /tmp/rebase-pr-{pr_number} rebase origin/{base_branch}
      ```

   e. If rebase succeeds, force push to the PR branch:
      **Important**: Push from temp branch to the actual PR branch name.
      ```bash
      git -C /tmp/rebase-pr-{pr_number} push origin temp-rebase-{pr_number}:{head_branch} --force-with-lease
      ```

   f. Clean up the temporary worktree.
      **Important**: Run cleanup from the main repo directory, never from inside the worktree.
      ```bash
      git worktree remove /tmp/rebase-pr-{pr_number}
      git branch -D temp-rebase-{pr_number}
      ```

6. After a successful rebase, comment on the PR:
   ```bash
   gh pr comment {pr_number} --repo {owner}/{repo} --body "Rebased with Claude Code."
   ```

7. Report the result to the user:
   - On success: Confirm the PR was rebased (and whether commits are signed)
   - On failure: Explain the error (common issues: conflicts exist, rebase not allowed, PR already up to date)
   - If conflicts occur during local rebase, clean up the worktree and inform the user they need to resolve conflicts manually
