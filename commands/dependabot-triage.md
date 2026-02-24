---
name: dependabot-triage
description: Triage Dependabot security alerts for a GitHub repo with Jira integration
argument-hint: "[owner/repo]"
allowed-tools: Bash
---

Triage Dependabot security alerts for the GitHub repo: $ARGUMENTS

Follow these steps carefully for each open alert. Do not batch — handle them one at a time.

---

## Step 0: Verify acli authentication

Before any Jira operations, verify that `acli` is authenticated by running `acli jira auth status`. If not authenticated, tell the user to run `acli jira auth login --web` and stop.

Refer to the `acli` skill for command syntax reference.

---

## Step 1: Fetch all open Dependabot alerts

Run this command to list every open alert:

```bash
gh api repos/<owner>/<repo>/dependabot/alerts --jq '.[] | select(.state == "open") | {number, dependency: .dependency.package.name, severity: .security_advisory.severity, summary: .security_advisory.summary, ghsa_id: .security_advisory.ghsa_id, cve_id: (.security_advisory.identifiers[] | select(.type == "CVE") | .value) // "N/A", published: .security_advisory.published_at}'
```

If there are no open alerts, tell me and stop.

---

## Step 2: For each open alert, one at a time

### 2a: Check for an associated Dependabot PR

Search for an open Dependabot pull request that addresses this alert:

```bash
gh pr list --repo <owner>/<repo> --state open --author app/dependabot --json number,title,url --jq '.[] | select(.title | test("<package-name>"; "i"))'
```

### 2b: Present the alert summary

Present a brief summary including:
- Alert number
- Package name
- Severity (critical / high / medium / low)
- CVE ID
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

First, approve the Dependabot PR (required by branch protection policies):

```bash
gh pr review <pr-number> --repo <owner>/<repo> --approve
```

Then merge using rebase:

```bash
gh pr merge <pr-number> --repo <owner>/<repo> --rebase
```

If the merge succeeds, the Dependabot alert should be automatically resolved by GitHub. Verify by checking the alert state:

```bash
gh api repos/<owner>/<repo>/dependabot/alerts/<number> --jq '.state'
```

Then post a comment on the PR noting it was merged during triage:

```bash
gh pr comment <pr-number> --repo <owner>/<repo> --body "Merged via Claude Code dependabot-triage."
```

If the alert is still open after merging, mark it as fixed:

```bash
gh api --method PATCH repos/<owner>/<repo>/dependabot/alerts/<number> \
  -f state=fixed
```

Confirm success or report failure before moving on.

---

## Step 4: If I choose to dismiss, run the dismiss command

```bash
gh api --method PATCH repos/<owner>/<repo>/dependabot/alerts/<number> \
  -f state=dismissed \
  -f dismissed_reason=<reason> \
  -f dismissed_comment="Dismissed via Claude Code triage"
```

Confirm success or report failure before moving on.

---

## Step 5: Search Jira for an associated ticket

After handling each alert (merged, dismissed, or skipped), search Jira for a related ticket.

IMPORTANT: Use `summary ~` instead of `text ~` because Jira's `text` field tokenizes CVE IDs
(hyphens + numbers) incorrectly and returns no results. The `summary` field works reliably.

First, search for the CVE and repo name together in the summary field. If no results, try a broader search with just the CVE.

Filter the results to find tickets that are not already Resolved/Done/Closed.

---

## Step 6: If a Jira ticket is found

Show me the ticket key, summary, and current status. Then ask me if I want to transition it to Resolved.

If I confirm:
1. Add a comment to the ticket describing the action taken (e.g., "Dependabot alert #N (package CVE-ID) was merged/dismissed in GitHub. Triaged via Claude Code.")
2. Transition the issue to "Resolved"

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
