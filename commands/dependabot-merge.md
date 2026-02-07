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

Run this command to list every open Dependabot PR with its mergeable state and check status:

```bash
gh pr list --repo <owner>/<repo> --author "app/dependabot" --state open --json number,title,mergeable,reviewDecision,headRefName,createdAt,url --jq '.[]'
```

Then for each PR, check if CI is passing (note: use `state` field, not `conclusion`):

```bash
gh pr checks <number> --repo <owner>/<repo> --json name,state --jq '.[]'
```

Categorize each PR into one of these groups:
- **Ready to merge** — mergeable state is MERGEABLE and all checks have state = "SUCCESS"
- **Not ready** — checks are failing (state = "FAILURE"), pending (state = "PENDING" or "QUEUED"), or PR has merge conflicts

Tell me how many total Dependabot PRs exist and how many are ready to merge.
If none are ready, list the blocked ones with their reasons and stop.
Only proceed with PRs that are ready to merge.

### Identify lock-step dependency groups

Some dependencies need to be updated together. Identify lock-step groups by looking for packages that:
1. Share a common prefix in their package name — this could be:
   - Scoped packages (e.g., `@typescript-eslint/parser` and `@typescript-eslint/eslint-plugin` share `@typescript-eslint/`)
   - Unscoped packages with a shared prefix (e.g., `react` and `react-router-dom` both start with `react`)
2. Are currently on the same version
3. Are being updated to the same target version

The matching version numbers (both current and target) are the strongest signal that packages belong together. Group these PRs together for presentation and merging. Present lock-step groups before individual PRs.

---

## Step 2: For each ready PR (or lock-step group), present an upgrade summary

### For lock-step groups

If this is a lock-step group, fetch details for all PRs in the group and present them together:

```
📦 **Lock-step group: <common-prefix>** (X packages)
   `<old-version>` → `<new-version>`  (<semver-change: patch | minor | major>)

   Packages:
   - <package-1> (PR #<number>)
   - <package-2> (PR #<number>)
   - ...

   Changes (combined):
   - <bullet summary of notable changes across all packages>

   Impact Analysis:
   - Semver: <colored-impact-text>
   - Total files changed: <count> (<additions> additions, <deletions> deletions)
```

Then ask what to do using AskUserQuestion with options: **Merge all**, **Skip all**, **Stop**.

---

### For individual PRs

Get the full PR details (the body contains Dependabot's release notes and changelogs):

```bash
gh pr view <number> --repo <owner>/<repo> --json title,body,createdAt,files,additions,deletions
```

Parse the package name and version information from the title. The title typically includes the package name, old version, and new version (e.g., "Bump <package> from <old> to <new>"), though the exact format may vary.

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

### For lock-step groups

Merge all PRs in the group sequentially. For each PR in the group:
```bash
gh pr comment <number> --repo <owner>/<repo> --body "Reviewed and approved with the help of Claude Code. (Lock-step update with <other-packages>)"
gh pr review <number> --repo <owner>/<repo> --approve
gh pr merge <number> --repo <owner>/<repo> --rebase --delete-branch
```

Wait for each merge to complete before starting the next one (to avoid conflicts). Report the status of each merge, then confirm overall success or report any failures.

### For individual PRs

First add a review comment, approve the PR, then rebase merge:
```bash
gh pr comment <number> --repo <owner>/<repo> --body "Reviewed and approved with the help of Claude Code."
gh pr review <number> --repo <owner>/<repo> --approve
gh pr merge <number> --repo <owner>/<repo> --rebase --delete-branch
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
<prefix>         #<n1>, #<n2>, ...     <old> → <new>         Merged all / Skipped all

Individual PRs:
PR#   Package              Version Change        Action
───   ───────              ──────────────        ──────
<#>   <package>            <old> → <new>         Merged (rebase) / Skipped

Not ready (blocked):
<#>   <package>            <reason: failing checks / merge conflict>
```
