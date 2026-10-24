---
name: gh
description: Non-obvious tips and workarounds for the GitHub CLI (gh) that prevent common pitfalls
---

# GitHub CLI reference for non-obvious behaviors

## Review threads

`gh` has no command to list, reply to, or resolve PR review threads. Use the `gh-arriba` extension:

```bash
gh arriba pr threads {pr-number} --json          # unresolved, current threads with their IDs
gh arriba pr reply {comment-id} "Fixed." --resolve
gh arriba pr resolve {thread-id}...              # PRRT_ IDs or comment IDs, --undo to reopen
```

## Requesting PR reviewers

`gh pr edit --add-reviewer` can fail with cryptic empty-string errors. Use `gh arriba`, which calls the REST endpoint:

```bash
gh arriba pr reviewers {pr-number} --add username
```

## Rerunning failed checks

`gh run rerun` takes one workflow run at a time. Use `gh arriba`, which reruns the failed jobs of
every run on a PR, or on all your open PRs when given `owner/repo`:

```bash
gh arriba pr retry {pr-number}
```

## Rebasing a PR

`gh pr update-branch --rebase` rebases server-side, so the commits lose their signatures. Use
`gh arriba`, which rebases locally with your signing key and pushes with a lease. Add `--remote` for
the server-side rebase:

```bash
gh arriba pr rebase {pr-number}
```

## Asking Dependabot to rebase

`gh arriba` comments `@dependabot rebase` on each PR, and prompts for which ones when given none:

```bash
gh arriba dependabot rebase {pr-number}...   # or --all
```

## Downloading workflow job logs

`gh run view --log` can be unreliable for large logs. Download job logs to files for searching. It takes a run ID, a job ID, or an Actions URL, and prints the path of each log:

```bash
gh arriba run logs {run-id} --repo {owner}/{repo} --failed -o /tmp/logs
```

## Downloading workflow artifacts

`gh api repos/.../artifacts/{id}/zip > foo.zip` can truncate large artifacts (≥1GB+) without erroring — the resulting file fails to unzip with "End-of-central-directory signature not found." Use `gh run download` instead, which streams the artifact correctly and unzips the outer wrapper for you:

```bash
gh run download {run-id} --repo {owner}/{repo} --name {artifact-name} --dir /tmp/out
```

The artifact's contents land directly in `--dir` (no outer `.zip` to unwrap). You still need to extract any inner `.tar.gz`/`.zip` payloads yourself.

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
