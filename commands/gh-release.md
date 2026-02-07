---
name: gh-release
description: Create a new GitHub release by triggering the Release workflow
argument-hint: "[owner/repo]"
allowed-tools: Bash
---

Create a new GitHub release by triggering the Release workflow.

## Arguments

$ARGUMENTS should be a GitHub repository in the format `owner/repo`, or empty to use the current repository.

## Instructions

1. **Determine the repository**:
   - If $ARGUMENTS is provided, use it as the repository
   - If $ARGUMENTS is empty, get current repo: `gh repo view --json owner,name` and format as `owner/name`

2. **Get the most recent release**:
   ```bash
   gh release list --repo {owner/repo} --limit 1 --json tagName,name
   ```
   - Extract the version number from the tag name (typically `vX.Y.Z` or `X.Y.Z`)
   - Display to user: "Most recent release: {tagName}"
   - If no releases exist, inform user and suggest starting with `1.0.0`

3. **Ask user for new version number**:
   - Parse the current version to extract major.minor.patch (e.g., `1.2.3`)
   - Calculate incremented patch version (e.g., `1.2.4`)
   - Use AskUserQuestion with:
     - Question: "What version number should the new release be?"
     - Option 1: "Increment patch version to {calculated_next_version} (Recommended)"
     - Option 2: "Enter custom version number"
   - If user selects custom, ask a follow-up question to get the version number using AskUserQuestion with a text input option

4. **Find the Release workflow**:
   ```bash
   gh workflow list --repo {owner/repo} --json name,id,path
   ```
   - Look for a workflow with "release" in the name (case-insensitive)
   - If multiple matches, prefer exact match "Release" or "release"
   - If no Release workflow found, inform user and exit

5. **Get workflow inputs**:
   ```bash
   gh workflow view {workflow_id_or_name} --repo {owner/repo} --yaml
   ```
   - Parse the `workflow_dispatch.inputs` section from the YAML
   - Identify all input fields and their properties (description, required, default, type)
   - Note: The version field should be detected automatically

6. **Ask about other workflow inputs**:
   - Display all workflow inputs (besides version) to the user
   - Use AskUserQuestion to ask: "Do you want to modify any workflow inputs?"
     - Option 1: "Use default values (Recommended)"
     - Option 2: "Customize workflow inputs"
   - If user chooses customize, for each input:
     - Use AskUserQuestion to get the value
     - Include the description and default value in the question
     - For boolean inputs, provide Yes/No options
     - For choice inputs, provide the available choices
     - For string inputs, allow text entry

7. **Confirm release details**:
   - Display a clear summary of all release details:
     - Repository: {owner/repo}
     - New version: {version}
     - Previous version: {previous_version}
     - All workflow inputs with their values (including defaults)
   - Use AskUserQuestion to ask: "Ready to create release {version}?"
     - Option 1: "Yes, create release (Recommended)"
     - Option 2: "Cancel"
   - If user selects cancel, exit without triggering the workflow

8. **Trigger the workflow**:
   ```bash
   gh workflow run {workflow_id_or_name} --repo {owner/repo} --field version={version} [--field input_name=value ...]
   ```
   - Include the version field
   - Include any other customized fields
   - Confirm to user: "Triggered Release workflow for version {version}"
   - Provide the workflow run URL for tracking

9. **Summary**:
   - Display: "Release workflow started for {owner/repo} version {version}"
   - Show command to check workflow status: `gh run list --repo {owner/repo} --workflow=Release --limit 1`
   - Remind user they can view the workflow run in GitHub Actions
