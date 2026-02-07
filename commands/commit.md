---
name: commit
description: Generate a concise commit message for staged changes and commit
allowed-tools: Bash
---

1. First verify there are staged changes with `git diff --cached --stat`

2. If no staged changes, give the option to stage all changes. If I chose to stage all the git modified files, run `git add -A` and continue. If not, stop.

3. **Check if new branch is needed**:
   - Get current branch: `git branch --show-current`
   - If already on a feature/bug branch (not main/master/dev/develop), skip to step 4
   - If on main/master/dev/develop, ask: "Would you like to create a new branch for this work?"
     - Use AskUserQuestion with options:
       - "Yes, create a feature branch"
       - "Yes, create a bug fix branch"
       - "No, commit to current branch"

4. **Create new branch** (if requested):
   - Use the `branch-name` skill to create a branch with proper naming conventions

5. **Analyze changes and create commit**:
   - Use the `commit-msg` skill to generate commit message options and create the commit

6. Ask the user if they want to push the commit

7. Show the result of the commit and push

8. **Create GitHub PR**:
   - Use the `gh-pr` command to create a PR with labels and reviewer assignment
