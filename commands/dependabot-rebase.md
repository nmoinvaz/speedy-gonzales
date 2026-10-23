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
   - If $ARGUMENTS is provided, pass `-R $ARGUMENTS` to every `gh arriba` call below
   - If $ARGUMENTS is empty, `gh arriba` uses the current repository

2. **Fetch all open Dependabot PRs**:
   ```bash
   gh arriba dependabot list [-R {owner/repo}] --json
   ```
   - The PRs are spread across `ready`, `needs_rebase`, `blocked`, and the `members` of each entry
     in `groups`. Each has `number`, `title`, `head_ref`, and `url`
   - If `counts.total` is 0, inform user and exit

3. **Display PRs to user**:
   - Show a formatted list with PR number, title, and branch name
   - Ask user which PRs to rebase using AskUserQuestion with:
     - Question: "Which Dependabot PRs would you like to rebase?"
     - Set multiSelect: true to allow selecting multiple PRs
     - Include an option for each PR showing: "#{number}: {title}"
     - Add a first option: "All PRs (Recommended)" that will rebase all PRs

4. **Rebase selected PRs**:
   - For all PRs:
     ```bash
     gh arriba dependabot rebase [-R {owner/repo}] --all --yes
     ```
   - For the selected PRs:
     ```bash
     gh arriba dependabot rebase {pr_number}... [-R {owner/repo}]
     ```
   - It comments `@dependabot rebase` on each and prints a confirmation per PR

5. **Summary**:
   - Report total number of PRs that were sent rebase commands
   - Remind user that Dependabot will process the rebase requests asynchronously
