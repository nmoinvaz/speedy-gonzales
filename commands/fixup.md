---
name: fixup
description: Apply staged changes to a selected commit in history (rewrites history)
allowed-tools: Bash
---

Apply the currently staged changes to a commit by rewriting git history.

1. First verify there are staged changes with `git diff --cached --stat`

2. If no staged changes, give the option to stage all changes. If I chose to stage all the git modified files, run `git add -A` and continue. If not, stop.

3. Get the last 8 commits and the staged diff:
   ```bash
   git log --oneline -8
   git diff --cached --stat
   ```

4. Determine which staged files and lines are affected:
   ```bash
   git diff --cached --name-only
   git diff --cached --unified=0
   ```

5. Rank commits by how well they match the staged changes, preferring in this order:
   - **Same purpose**: commits whose message describes the same feature/fix that the staged changes accomplish
   - **Same lines**: commits that previously touched the same lines in the same files (check with `git log -p` or `git blame`)
   - **Same files**: commits that touched any of the same files

   Present the ranked list to the user with a recommended commit and a brief reason for the recommendation.

6. Give the user the option to accept the recommendation or select a different commit

7. Once the user selects a commit, create a fixup commit:
   ```bash
   git commit --fixup=<selected-hash>
   ```

8. Perform an interactive rebase with autosquash:
   ```bash
   GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <selected-hash>~1
   ```

9. Report success or any conflicts that need resolution

**If there are rebase conflicts**:
- Explain what happened
- Show which files have conflicts
- Tell the user they can resolve conflicts and run `git rebase --continue`, or abort with `git rebase --abort`
