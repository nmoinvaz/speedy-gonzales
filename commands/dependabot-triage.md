---
name: dependabot-triage
description: Triage Dependabot security alerts for a GitHub repo with Jira integration
argument-hint: "[owner/repo]"
allowed-tools: Bash, mcp__plugin_atlassian_atlassian__searchJiraIssuesUsingJql, mcp__plugin_atlassian_atlassian__addCommentToJiraIssue, mcp__plugin_atlassian_atlassian__getTransitionsForJiraIssue, mcp__plugin_atlassian_atlassian__transitionJiraIssue, mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources
---

Triage Dependabot security alerts for the GitHub repo: $ARGUMENTS

Follow these steps carefully for each open alert. Do not batch — handle them one at a time.

---

## Step 0: Get Atlassian Cloud ID

Before any Jira operations, call `getAccessibleAtlassianResources` to get the cloud ID. Use this cloud ID for all subsequent Jira MCP tool calls.

---

## Step 1: Fetch all open Dependabot alerts

Run this command to list every open alert:

```bash
gh api repos/<owner>/<repo>/dependabot/alerts --jq '.[] | select(.state == "open") | {number, dependency: .dependency.package.name, severity: .security_advisory.severity, summary: .security_advisory.summary, ghsa_id: .security_advisory.ghsa_id, cve_id: (.security_advisory.identifiers[] | select(.type == "CVE") | .value) // "N/A", published: .security_advisory.published_at}'
```

If there are no open alerts, tell me and stop.

---

## Step 2: For each open alert, one at a time

Present a brief summary including:
- Alert number
- Package name
- Severity (critical / high / medium / low)
- CVE ID
- One-line description of the vulnerability

Then ask me what I want to do using AskUserQuestion. The options must be:

1. **Dismiss: fix_started** — A fix has already been started
2. **Dismiss: inaccurate** — This alert is inaccurate or incorrect
3. **Dismiss: no_bandwidth** — No bandwidth to fix this
4. **Dismiss: not_used** — This code is not actually used
5. **Dismiss: tolerable_risk** — Risk is tolerable to this project
6. **Skip** — Leave this alert open and move to the next one

---

## Step 3: If I choose to dismiss, run the dismiss command

```bash
gh api --method PATCH repos/<owner>/<repo>/dependabot/alerts/<number> \
  -f state=dismissed \
  -f dismissed_reason=<reason> \
  -f dismissed_comment="Dismissed via Claude Code triage"
```

Confirm success or report failure before moving on.

---

## Step 4: Search Jira for an associated ticket

After handling each alert (dismissed or skipped), search Jira for a related ticket using the `searchJiraIssuesUsingJql` MCP tool.

IMPORTANT: Use `summary ~` instead of `text ~` because Jira's `text` field tokenizes CVE IDs
(hyphens + numbers) incorrectly and returns no results. The `summary` field works reliably.

First, search for the CVE and repo name together:

```
jql: summary ~ "<CVE-ID>" AND summary ~ "<repo-name>"
fields: ["summary", "status"]
```

If no results, try a broader search with just the CVE:

```
jql: summary ~ "<CVE-ID>"
fields: ["summary", "status"]
```

Filter the results to find tickets that are not already Resolved/Done/Closed.

---

## Step 5: If a Jira ticket is found

Show me the ticket key, summary, and current status. Then ask me if I want to transition it to Resolved.

If I confirm, first add a comment using the `addCommentToJiraIssue` MCP tool:

```
issueIdOrKey: "<TICKET-KEY>"
commentBody: "Dependabot alert #<number> (<package> <CVE-ID>) was dismissed in GitHub with reason: <reason>. Dismissed via Claude Code triage."
```

Then get available transitions using `getTransitionsForJiraIssue` to find the transition ID for "Resolved", and apply it using `transitionJiraIssue`.

Only transition if I confirm.

---

## Step 6: Repeat

Move to the next open alert and repeat from Step 2. After all alerts are processed, print a final summary table showing:
- Each alert number and package
- Action taken (dismissed with reason, or skipped)
- Associated Jira ticket (if any) and whether it was transitioned
