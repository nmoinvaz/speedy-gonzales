---
name: gh
description: Non-obvious tips and workarounds for the GitHub CLI (gh) that prevent common pitfalls
---

# GitHub CLI reference for non-obvious behaviors

## Requesting PR reviewers

`gh pr edit --add-reviewer` can fail with cryptic empty-string errors. Use the API directly instead:

```bash
gh api repos/{owner}/{repo}/pulls/{pr-number}/requested_reviewers \
  -f "reviewers[]=username"
```

## Downloading workflow job logs

`gh run view --log` can be unreliable for large logs. Download job logs directly via the API and save to a file for searching:

```bash
gh api repos/{owner}/{repo}/actions/jobs/{job-id}/logs > /tmp/job.log
```

To get job IDs for a run:

```bash
gh run view {run-id} --repo {owner}/{repo} --json jobs --jq '.jobs[] | {name, id, status, conclusion}'
```

## Stacked pull requests with `gh-stack`

The `github/gh-stack` extension (`gh extension install github/gh-stack`) manages a local stack of branches and the corresponding stack of PRs. A few non-obvious details:

### Adopting an existing branch into a new stack

If you already have a branch with work and an open PR, `gh stack init` without arguments errors out. Pass the branch name with `-a`/`--adopt` and the trunk with `-b`:

```bash
gh stack init -a --base dev nathan/dev/feature-one
```

This registers the existing branch as the bottom of a new stack rooted at `dev` without creating any new commits or branches.

### Adding a new layer on top

```bash
gh stack add nathan/dev/feature-two
```

Creates a new branch based on the current stack top and checks it out. You can then commit, and later `gh stack submit --auto` will push all branches in the stack and open PRs with the correct base chain (e.g. `feature-two` → `feature-one` → `dev`).

### Viewing the stack

```bash
gh stack view
```

Prints an ASCII diagram of the stack with current branch, PR number, commit sha, and trunk. Much more useful than `git log --graph` for stack navigation.

### Navigating the stack

- `gh stack down` — check out the next branch toward trunk (parent in the stack).
- `gh stack up` — check out the next branch away from trunk (child in the stack).
- `gh stack bottom` / `gh stack top` — jump to the ends.

### Pushing and syncing

`gh stack submit --auto` pushes every branch in the stack, creates or updates PRs on GitHub, and sets each PR's base to the branch below it. Safe to re-run after amending commits on any branch in the stack — it force-pushes the affected branches and leaves the untouched ones alone.

To re-sync without opening PRs:

```bash
gh stack push
```

### Gotchas

- `gh stack submit` does not stage or commit anything — stage and commit with `git` first, then submit.
- After rebasing the bottom branch onto a new trunk sha, use `gh stack rebase` (not `git rebase`) to propagate the new base through every layer.
- If CI fails only on the top PR, the base PR still shows as mergeable — don't merge the base PR without checking the stack view first, because merging mid-stack orphans the upper layers.
