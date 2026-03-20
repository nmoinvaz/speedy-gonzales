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
