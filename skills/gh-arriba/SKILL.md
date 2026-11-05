---
name: gh-arriba
description: GitHub workflows with the gh-arriba extension, for PR review threads, pending reviews, failed checks, retries, signed rebases, reviewers, labels, workflow logs, releases, and Dependabot
allowed-tools: Bash(gh arriba --version)
---

# gh-arriba Quick Reference

[gh-arriba](https://github.com/arriba-tools/gh) is the `gh` extension this project's GitHub workflows
use. It covers what `gh` lacks or gets wrong, such as review threads, pending reviews, and signed
rebases.

## Prerequisites

Installed version:

!`gh arriba --version 2>&1 || echo "gh-arriba is not installed"`

The plugin installs it at session start. If it is still missing, tell the user to run
`gh extension install nmoinvaz/gh-arriba` and stop.

## Conventions

- A `PR` argument takes a number, URL, or branch, and defaults to the PR for the current branch.
- `-R owner/repo` targets another repository.
- Add `--json` to any command whose output you need to parse.
- `-y` skips confirmation prompts.

## Review Threads

`gh` has no command to list, reply to, or resolve review threads.

```bash
gh arriba pr threads 123 --json                 # unresolved, current threads with their IDs
gh arriba pr threads --bots --review-bodies     # CodeRabbit findings in review bodies too
gh arriba pr threads --humans --since-last-review
gh arriba pr reply 2468013579 "Fixed in abc123." --resolve
gh arriba pr resolve PRRT_kwDO... 2468013580    # thread or comment IDs, --undo to reopen
gh arriba pr apply --dry-run                    # reviewers' suggestion blocks as edits
gh arriba pr dump 123 -o /tmp/pr-123.txt        # whole discussion as grep-friendly text
```

`pr comment show` and `pr comment edit` take a comment's URL or ID, and edit replaces the body of
one you posted.

## Pending Reviews

GitHub allows one pending review per user, so these add to it rather than starting another.

```bash
gh arriba pr review lines 123                   # line ranges that accept inline comments
gh arriba pr review add 123 src/main.rs:42-48 - <<'MD'
1. This leaks the handle when `open` fails.
MD
gh arriba pr review show 123
gh arriba pr review submit 123 --event comment --body "A few issues, numbered inline."
gh arriba pr review discard 123
```

`--side left` puts the comment on the base side of the diff.

## Checks and Failures

`gh run rerun` takes one run at a time, and `gh run view --log` is unreliable for large logs.

```bash
gh arriba pr checks 123 --wait --fail-fast      # exits non-zero when a check failed
gh arriba pr failures 123                       # failed steps with their error lines
gh arriba pr failures 123 --job windows --grep 'error C\d+'
gh arriba pr retry 123                          # reruns failed and cancelled checks
gh arriba pr retry --mine                       # every open PR you authored
```

`pr checks --sha HEAD` first waits for the PR head to reach a commit you just pushed.

## Rebasing

`gh pr update-branch --rebase` rebases server-side, so the commits lose their signatures.
`pr rebase` rebases locally with your signing key and pushes with a lease.

```bash
gh arriba pr rebase 123 --check                 # conflicting files, without rebasing
gh arriba pr rebase 123
gh arriba pr rebase 123 --remote                # server-side, unsigned
```

It comments "Rebased." on the PR unless `--no-comment` is passed.

## Reviewers and Labels

`gh pr edit --add-reviewer` can fail with cryptic empty-string errors. `pr reviewers` calls the REST
endpoint instead.

```bash
gh arriba pr reviewers 123                      # suggests top contributors
gh arriba pr reviewers 123 --add octocat
gh arriba pr labels 123 --suggest               # ranks the repo's labels against the PR
gh arriba pr labels 123 --add bug --remove triage
```

## Workflow Runs

```bash
gh arriba run logs 1234567890 --failed -o /tmp/logs --errors
gh arriba run watch                             # every run for the local HEAD commit
gh arriba run watch --branch main -w Release --notify
gh arriba run artifacts --pr 123 --download -D /tmp/out
gh arriba run dispatch build --ref main --watch
```

`run logs` takes a run ID, job ID, or Actions URL, and prints the path of each saved log.

## Releases

`release` dispatches the repo's release workflow with the next version.

```bash
gh arriba release --dry-run --json              # previous tag, next version, workflow inputs
gh arriba release --version 1.4.0 --yes --watch
gh arriba release --bump minor --yes
```

`-f KEY=VALUE` sets another workflow input, and `-w` dispatches a workflow other than the release one.

## Dependabot

```bash
gh arriba dependabot list                       # ready, needs rebase, and blocked, with lock-step sets
gh arriba dependabot merge --all-ready
gh arriba dependabot rebase --all               # comments @dependabot rebase on each PR
gh arriba dependabot alerts
gh arriba dependabot dismiss 42 --reason not_used --comment "Only used in tests."
```

`dependabot merge` prompts for each ready PR when given none, and `--auto` enables auto-merge.

## Other Commands

| Command | Description |
|---------|-------------|
| `worktree list` | Worktrees with their PR, its state and checks, and unpushed work |
| `worktree add <PR>` | Check one of your PRs out into a new worktree |
| `worktree prune --dry-run` | Worktrees of your merged or closed PRs that prune would remove |
| `runners` | Self-hosted runners and what they are running, `--org` for an organization |
| `inbox clean` | Mark done the notifications whose PR or issue merged or closed |
| `notify watch` | Desktop notifications for new GitHub notifications |
| `config sync` | Sync project config files to and from a gist |

Run `gh arriba <command> --help` for the full options.
