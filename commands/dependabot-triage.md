---
name: dependabot-triage
description: Triage Dependabot security alerts for a GitHub repo with Jira integration
argument-hint: "[owner/repo]"
allowed-tools: Bash
---

Triage Dependabot security alerts for the GitHub repo: $ARGUMENTS

Follow these steps carefully for each open alert. Do not batch — handle them one at a time.

---

## Step 0: Verify the Jira login

Before any Jira operations, load the `/arriba:jira-arriba` skill for command syntax reference. It shows whether `jira-arriba` is installed and logged in. If either is missing, follow the skill's instructions to the user and stop.

---

## Step 1: Fetch all open Dependabot alerts

Run this command to list every open alert, most severe first:

```bash
gh arriba dependabot alerts -R <owner>/<repo> --json
```

Each alert has `number`, `package`, `ecosystem`, `severity`, `cve` (null when the advisory has
none), `ghsa`, `summary`, `manifest`, `patched` (the first fixed version), `url`, and `fix_pr`, the
open Dependabot PR for the same package with its `number`, `title`, and `url`, or null.

If there are no open alerts, tell me and stop.

---

## Step 2: For each open alert, one at a time

### 2a: Check for an associated Dependabot PR

Use the alert's `fix_pr` from Step 1. It is null when no open Dependabot PR updates that package.

### 2b: Present the alert summary

Present a brief summary including:
- Alert number
- Package name
- Severity (critical / high / medium / low)
- CVE ID, or the GHSA ID when there is no CVE
- One-line description of the vulnerability
- **Associated PR** (if found in 2a): PR number, title, and URL

Then ask me what I want to do using AskUserQuestion. The options must be:

1. **Merge PR** _(only include this option if a Dependabot PR was found)_ — Merge the associated Dependabot PR to fix the alert
2. **Dismiss: fix_started** — A fix has already been started
3. **Dismiss: inaccurate** — This alert is inaccurate or incorrect
4. **Dismiss: no_bandwidth** — No bandwidth to fix this
5. **Dismiss: not_used** — This code is not actually used
6. **Dismiss: tolerable_risk** — Risk is tolerable to this project
7. **Skip** — Leave this alert open and move to the next one

---

## Step 3: If I choose to merge the PR

Comment on the PR, approve it (required by branch protection policies), rebase merge it, and delete
its branch:

```bash
gh arriba dependabot merge <pr-number> -R <owner>/<repo> --yes \
  --comment "Approved and merged via Claude Code dependabot-triage."
```

If the merge succeeds, the Dependabot alert should be automatically resolved by GitHub. Verify by checking the alert state:

```bash
gh api repos/<owner>/<repo>/dependabot/alerts/<number> --jq '.state'
```

If the alert is still open, GitHub marks it fixed once the dependency graph picks up the merge,
usually within minutes. Report it as pending. The API can't set an alert to fixed by hand.

Confirm success or report failure before moving on.

---

## Step 4: If I choose to dismiss, run the dismiss command

```bash
gh arriba dependabot dismiss <number> -R <owner>/<repo> --reason <reason> --yes \
  --comment "Dismissed via Claude Code triage"
```

Confirm success or report failure before moving on.

---

## Step 5: Search Jira for an associated ticket

After handling each alert (merged, dismissed, or skipped), search Jira for a related ticket.

IMPORTANT: Use `summary ~` instead of `text ~` because Jira's `text` field tokenizes CVE IDs
(hyphens + numbers) incorrectly and returns no results. The `summary` field works reliably.

First, search for the alert's identifier and repo name together in the summary field, using the CVE, or the GHSA ID when `cve` is null. If no results, try a broader search with just the identifier, then one with the package name.

```bash
jira-arriba issue search --jql 'summary ~ "CVE-2024-1234" AND summary ~ "repo-name"' --fields key,summary,status --json
jira-arriba issue search --jql 'summary ~ "CVE-2024-1234"' --fields key,summary,status --json
jira-arriba issue search --jql 'summary ~ "GHSA-xxxx-xxxx-xxxx" AND summary ~ "repo-name"' --fields key,summary,status --json
jira-arriba issue search --jql 'summary ~ "package-name" AND summary ~ "repo-name" AND status not in (Resolved, Done, Closed)' --fields key,summary,status --json
```

Filter the results to find tickets that are not already Resolved/Done/Closed.

---

## Step 6: If a Jira ticket is found

Show me the ticket key, summary, and current status. If the alert was skipped, stop here and leave the ticket as it is. Otherwise ask me if I want to transition it to Resolved.

If I confirm:
1. Add a comment to the ticket describing what happened, filling in the alert number, package, the CVE or GHSA ID used in the search, and the outcome, `was merged` for a merged PR or `was dismissed as <reason>` for a dismissal:
   ```bash
   jira-arriba issue comment add <TICKET-KEY> "Dependabot alert #<N> (<package> <CVE-or-GHSA>) <was merged|was dismissed as <reason>> in GitHub. Triaged via Claude Code."
   ```
2. Transition the issue:
   ```bash
   jira-arriba issue transition <TICKET-KEY> --status Resolved
   ```

Only transition if I confirm.

If a Dependabot PR was merged for this alert, also add a comment on the GitHub PR linking to the Jira ticket:

```bash
gh pr comment <pr-number> --repo <owner>/<repo> --body "Associated Jira ticket: <TICKET-KEY> (<ticket-summary>)"
```

---

## Step 7: Repeat

Move to the next open alert and repeat from Step 2. After all alerts are processed, print a final summary table showing:
- Each alert number and package
- Action taken (PR merged, dismissed with reason, or skipped)
- Associated Jira ticket (if any) and whether it was transitioned
