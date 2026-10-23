---
name: dependabot-merge
description: Interactively review and merge Dependabot PRs for a GitHub repo
argument-hint: "[owner/repo]"
allowed-tools: Bash
---

Work through each mergeable Dependabot PR one at a time, similar to yarn upgrade-interactive.

Interactively review and merge Dependabot PRs for the GitHub repo: $ARGUMENTS

---

## Step 1: Fetch all open Dependabot PRs and their check status

Run this command to list every open Dependabot PR, categorized and grouped:

```bash
gh arriba dependabot list -R <owner>/<repo> --json
```

- `counts` has the `total`, `ready`, `needs_rebase`, and `blocked` totals
- `ready`, `needs_rebase`, and `blocked` list the PRs outside any lock-step group. Each PR has
  `number`, `title`, `url`, `created_at`, `additions`, `deletions`, `changed_files`, `reason` (why
  it is blocked), and `update` with `package`, `from`, `to`, and `change` (`patch`, `minor`, or
  `major`)
- `groups` lists the lock-step groups (see below)

Each PR falls into one of these groups:
- **Ready to merge** — mergeable and all checks passing
- **Needs rebase** — checks passing but conflicting with or behind its base
- **Not ready** — checks failing or pending, with the `reason`

Tell me how many total Dependabot PRs exist, how many are ready to merge, and how many need a rebase.
If none are ready or rebaseable, list the blocked ones with their reasons and stop.
Proceed with PRs that are ready to merge. PRs that need a rebase will be handled specially within lock-step groups (see below).

### Lock-step dependency groups

Some dependencies need to be updated together. `gh arriba` groups PRs whose packages share a name
prefix or scope (e.g., `@typescript-eslint/parser` and `@typescript-eslint/eslint-plugin` share
`@typescript-eslint/`) and that move from the same current version to the same target version. Each
entry in `groups` has `prefix`, `from`, `to`, `change`, `status`, and `members`, the full PRs in
merge order. Present lock-step groups before individual PRs.

**Lock-step groups with rebase-needed PRs:** A group whose `status` is `needs_rebase` has a first PR
that needs a rebase. Include the group in the presentation. The first PR in a lock-step group is the
one that must merge first — subsequent PRs in the group typically conflict because they touch the
same lock file. Mark these groups with a 🔄 indicator. A group whose `status` is `blocked` has a
member with failing or pending checks, so it is not ready.

---

## Step 2: For each ready PR (or lock-step group), present an upgrade summary

### For lock-step groups

If this is a lock-step group, fetch details for all PRs in the group and present them together:

```
📦 **Lock-step group: <common-prefix>** (X packages)
   `<old-version>` → `<new-version>`  (<semver-change: patch | minor | major>)

   Packages:
   - <package-1> (PR #<number>) — Ready ✅
   - <package-2> (PR #<number>) — Needs rebase 🔄
   - ...

   Changes (combined):
   - <bullet summary of notable changes across all packages>

   Impact Analysis:
   - Semver: <colored-impact-text>
   - Total files changed: <count> (<additions> additions, <deletions> deletions)
```

If all PRs in the group are ready, ask with options: **Merge all**, **Skip all**, **Stop**.

If the first PR to merge needs a rebase, ask with options: **Rebase & auto-merge all**, **Skip all**, **Stop**.

---

### For individual PRs

Get the PR body, which contains Dependabot's release notes and changelogs:

```bash
gh pr view <number> --repo <owner>/<repo> --json body
```

The package name, versions, semver change, and file counts come from the PR's entry in Step 1.

Extract key changes from the PR body's release notes and changelog sections. Focus on:
- New features
- Bug fixes
- Breaking changes
- Security updates
- Performance improvements

Present a clear upgrade summary using this format:

```
📦 **<package-name>**
   `<old-version>` → `<new-version>`  (<semver-change: patch | minor | major>)
   PR #<number> — opened <date>

   Changes:
   - <bullet summary of what changed, extracted from the PR body / changelog>

   Impact Analysis:
   - Semver: <colored-impact-text>
   - Files changed: <count> (<additions> additions, <deletions> deletions)
   - <any notable observations: breaking changes, new dependencies, deprecations>
```

IMPORTANT FORMATTING RULES:
1. The package name MUST be displayed in **bold** markdown
2. The version numbers should be displayed in `backticks` (code format) to stand out
3. For the Impact Analysis, use emoji indicators based on risk level:
   - **Patch** updates (0.0.x): Use 🟢 prefix — "Low risk — bug fixes and security patches"
   - **Minor** updates (0.x.0): Use 🟡 prefix — "Medium risk — new features, backward compatible"
   - **Major** updates (x.0.0): Use 🔴 prefix — "High risk — potential breaking changes, review carefully"

Then ask what to do using AskUserQuestion.

---

## Step 3: Ask the user what to do

Options:
1. **Merge** — Approve, rebase and merge this PR
2. **Skip** — Leave this PR open and move to the next one
3. **Stop** — Stop reviewing, skip all remaining PRs

---

## Step 4: If merging, execute the merge

Each `gh arriba dependabot merge` call comments, approves (skipped when already approved), merges
with a rebase, and deletes the branch. It prints what it did for each PR and exits non-zero if any
PR failed.

### For lock-step groups — all ready

Merge the first PR, then the rest. Run the second command only after the first finishes, so it sees
the conflicts the first merge caused:
```bash
gh arriba dependabot merge <first> -R <owner>/<repo> --yes \
  --comment "Reviewed and approved with the help of Claude Code. (Lock-step update of <prefix> <from> → <to>)"
gh arriba dependabot merge <rest...> -R <owner>/<repo> --auto --yes \
  --comment "Reviewed and approved with the help of Claude Code. (Lock-step update of <prefix> <from> → <to>)"
```

Each remaining PR that still merges cleanly merges right away. Each that now conflicts on the shared
lock file gets auto-merge enabled and an `@dependabot rebase` comment. Report the status of each
merge, then confirm overall success or report any failures.

### For lock-step groups — rebase & auto-merge

When the user chose **Rebase & auto-merge all**, the first PR in the group needs a Dependabot rebase
before it can merge. Approve every PR in the group, enable auto-merge on each, and request a
Dependabot rebase on each one that conflicts:
```bash
gh arriba dependabot merge <all group PRs> -R <owner>/<repo> --auto --yes \
  --comment "Reviewed and approved with the help of Claude Code. (Lock-step update of <prefix> <from> → <to>)"
```

**Report the status**: Tell the user that auto-merge has been enabled on all PRs in the group and a rebase has been requested where needed. Explain that once Dependabot rebases and CI passes, the PRs will merge automatically in sequence (each subsequent PR will be rebased by Dependabot as the previous one merges). If it reports that auto-merge is disabled in the repo settings, tell the user.

### For individual PRs

```bash
gh arriba dependabot merge <number> -R <owner>/<repo> --yes \
  --comment "Reviewed and approved with the help of Claude Code."
```

Confirm success or report failure before moving on.

If the user chose "Stop", skip all remaining PRs and go to the summary.

---

## Step 5: Repeat

Move to the next ready PR and repeat from Step 2.

---

## Step 6: Final summary

After all PRs are processed, print a summary table:

```
Dependabot PR Merge Summary — <owner>/<repo>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Lock-step groups:
Group            PRs                   Version Change        Action
─────            ───                   ──────────────        ──────
<prefix>         #<n1>, #<n2>, ...     <old> → <new>         Merged all / Rebase & auto-merge / Skipped all

Individual PRs:
PR#   Package              Version Change        Action
───   ───────              ──────────────        ──────
<#>   <package>            <old> → <new>         Merged (rebase) / Skipped

Not ready (blocked):
<#>   <package>            <reason: failing checks / merge conflict>
```
