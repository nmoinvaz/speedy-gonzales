---
name: fixup
description: Apply staged changes to a selected commit in history (rewrites history)
allowed-tools: Bash
---

Apply the currently staged changes to a commit by rewriting git history.

1. First verify there are staged changes with `git diff --cached --stat`

2. If no staged changes, give the option to stage all changes. If I chose to stage all the git modified files, run `git add -A` and continue. If not, stop.

3. Get the last 8 commits in the repository:
   ```bash
   git log --oneline -8
   ```

4. Figure out what might be the best commit to apply the staged changes to

5. Give the user the option to enter which commit they want to apply the staged changes to

6. Once the user selects a commit, create a fixup commit:
   ```bash
   git commit --fixup=<selected-hash>
   ```

7. Perform an interactive rebase with autosquash:
   ```bash
   GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <selected-hash>~1
   ```

8. Report success or any conflicts that need resolution

**If there are rebase conflicts**:
- Explain what happened
- Show which files have conflicts
- Tell the user they can resolve conflicts and run `git rebase --continue`, or abort with `git rebase --abort`
