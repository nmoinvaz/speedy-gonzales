---
name: commit
description: Generate a concise commit message for staged changes and commit
allowed-tools: Bash
---

1. First verify there are staged changes with `git diff --cached --stat`

2. If no staged changes, give the option to stage all changes. If I chose to stage all the git modified files, run `git add -A` and continue. If not, stop.

3. **Run linters on staged files** before committing:
   - Detect which linters are available and relevant to the project:
     - If `Cargo.toml` exists: run `cargo clippy --all-targets -- -D warnings` and `cargo fmt --check`
     - If `package.json` exists and has a `lint` script: run `yarn lint` or `npm run lint`
     - If `pyproject.toml` or `setup.py` exists: run `ruff check .` if ruff is installed, otherwise try `flake8`
     - If `.clang-format` exists: run `clang-format --dry-run --Werror` on staged C/C++ files
     - If a `Makefile` has a `lint` target: run `make lint`
     - If `.pre-commit-config.yaml` exists: run `pre-commit run --files` on staged files
   - Only run linters that are installed on the system (check with `which`)
   - If any linter reports errors, show them and ask whether to fix them before continuing or proceed anyway

4. **Check if new branch is needed**:
   - Get current branch: `git branch --show-current`
   - If already on a feature/bug branch (not main/master/dev/develop), skip to step 5
   - If on main/master/dev/develop, ask: "Would you like to create a new branch for this work?"
     - Use AskUserQuestion with options:
       - "Yes, create a feature branch"
       - "Yes, create a bug fix branch"
       - "No, commit to current branch"

5. **Create new branch** (if requested):
   - Use the `branch-name` skill to create a branch with proper naming conventions

6. **Analyze changes and create commit**:
   - Use the `commit-msg` skill to generate commit message options and create the commit

7. **Run CodeRabbit review** (if available):
   - Check if `cr` is installed: `which cr`
   - If installed, check auth status: `cr auth status 2>&1`
   - If authenticated, run `cr` to review the commit
   - Show the review output to the user
   - If `cr` is not installed or not authenticated, skip silently

8. Ask the user if they want to push the commit

9. Show the result of the commit and push

10. **Create GitHub PR**:
   - Use the `gh-pr` command to create a PR with labels and reviewer assignment
