---
name: gh-pr
description: Create a GitHub Pull Request for the current branch with labels and reviewer assignment
allowed-tools: Bash
---

Create or manage a GitHub Pull Request for the current branch:

1. **Check for existing PR**:
   ```bash
   gh pr view --json url,number 2>/dev/null
   ```
   - If a PR already exists, skip to step 3 (labels) and mention the existing PR URL

2. **Create the PR** (if no existing PR):
   - Ask if the user wants to create a GitHub Pull Request
   - If yes:
     - Check if the branch has been pushed (if not, push it first with `git push -u origin <branch>`)
     - Determine the base branch:
       ```bash
       git remote show origin | grep 'HEAD branch'
       ```
     - Analyze all commits on this branch vs the base branch to generate a PR title and description
     - Write the PR description as a concise paragraph explaining the change (not bullet points)
     - Do not include a test plan section in the PR description
     - At the bottom of the PR description, add: "Summary generated with Claude Code."
     - Create the PR:
       ```bash
       gh pr create --title "<title>" --body "<description>"
       ```
     - Present the PR URL to the user

3. **Suggest and apply labels**:
   - Get available labels from the repository:
     ```bash
     gh label list --json name,description --limit 100
     ```
   - Get labels currently on the PR:
     ```bash
     gh pr view <pr-number> --json labels --jq '.labels[].name'
     ```
   - Analyze the changes and select 3-4 most relevant labels to suggest based on:
     - Type of change (bug fix → "bug", new feature → "enhancement", etc.)
     - Files modified (e.g., package.json → "dependencies", .github/ → "github_actions")
     - Components affected (e.g., API changes → "manifest", UI changes → "ui/ux")
   - Use AskUserQuestion with multiSelect: true showing:
     - The 3-4 suggested labels as options (pre-analyze which are most relevant)
     - User can select "Other" to type additional label names
     - If PR already has labels, mention them in the question text
   - Apply selected labels:
     ```bash
     gh pr edit <pr-number> --add-label "label1,label2"
     ```

4. **Request a review**:
   - Get top contributors to the repository (excluding current user):
     ```bash
     gh api repos/{owner}/{repo}/contributors --jq '.[].login' | head -10
     ```
   - Get the current GitHub username:
     ```bash
     gh api user --jq '.login'
     ```
   - Filter out the current user from the contributors list
   - Present the top contributors using AskUserQuestion and ask who should review the PR
     - Include a "Skip - don't request review" option
   - If user selects a reviewer:
     ```bash
     gh pr edit <pr-number> --add-reviewer "<username>"
     ```
