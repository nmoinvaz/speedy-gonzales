---
name: dependabot-rebase
description: Trigger Dependabot to rebase its PRs by commenting on them
argument-hint: "[owner/repo]"
allowed-tools: Bash
---

Trigger Dependabot to rebase its PRs by commenting on them.

## Arguments

$ARGUMENTS should be a GitHub repository in the format `owner/repo`, or empty to use the current repository.

## Instructions

1. **Determine the repository**:
   - If $ARGUMENTS is provided, use it as the repository
   - If $ARGUMENTS is empty, get current repo: `gh repo view --json owner,name` and format as `owner/name`

2. **Fetch all open Dependabot PRs**:
   ```bash
   gh pr list --repo {owner/repo} --author app/dependabot --json number,title,headRefName,url --state open
   ```
   - If no Dependabot PRs found, inform user and exit

3. **Display PRs to user**:
   - Show a formatted list with PR number, title, and branch name
   - Ask user which PRs to rebase using AskUserQuestion with:
     - Question: "Which Dependabot PRs would you like to rebase?"
     - Set multiSelect: true to allow selecting multiple PRs
     - Include an option for each PR showing: "#{number}: {title}"
     - Add a first option: "All PRs (Recommended)" that will rebase all PRs

4. **Rebase selected PRs**:
   - For each selected PR, post a comment to trigger Dependabot rebase:
     ```bash
     gh pr comment {pr_number} --repo {owner/repo} --body "@dependabot rebase"
     ```
   - Show confirmation message for each PR: "Triggered rebase for PR #{number}"

5. **Summary**:
   - Report total number of PRs that were sent rebase commands
   - Remind user that Dependabot will process the rebase requests asynchronously
