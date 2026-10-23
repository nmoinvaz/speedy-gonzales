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
   - If $ARGUMENTS is provided, pass `-R $ARGUMENTS` to every `gh arriba` call below
   - If $ARGUMENTS is empty, `gh arriba` uses the current repository

2. **Preview the release plan**:
   ```bash
   gh arriba release [-R {owner/repo}] --dry-run --json
   ```
   - `previous` is the most recent release tag, or null when there are no releases
   - `version` is `previous` with the patch number incremented, keeping any `v` prefix, or `1.0.0`
     when there are no releases
   - `workflow` and `workflow_path` name the Release workflow it found
   - `inputs[]` lists every `workflow_dispatch` input with `name`, `value`, `description`, `type`,
     `required`, `default`, and `options`. Its `source` is `version` for the version input,
     `default` or `unset` for the rest, and `missing` for a required input with no default
   - Display to user: "Most recent release: {previous}", or say there are no releases yet
   - If it fails because no workflow mentions release, or several do, inform the user. When the
     user picks one of the listed workflows, add `-w {name}` to every call below

3. **Ask user for new version number**:
   - Use AskUserQuestion with:
     - Question: "What version number should the new release be?"
     - Option 1: "Increment patch version to {version} (Recommended)"
     - Option 2: "Enter custom version number"
   - If user selects custom, ask a follow-up question to get the version number using AskUserQuestion with a text input option

4. **Ask about other workflow inputs**:
   - Display all workflow inputs (besides version) to the user
   - Use AskUserQuestion to ask: "Do you want to modify any workflow inputs?"
     - Option 1: "Use default values (Recommended)"
     - Option 2: "Customize workflow inputs"
   - Always ask for inputs whose `source` is `missing`, since the workflow requires them
   - If user chooses customize, for each input:
     - Use AskUserQuestion to get the value
     - Include the description and default value in the question
     - For boolean inputs, provide Yes/No options
     - For choice inputs, provide the available `options`
     - For string inputs, allow text entry

5. **Confirm release details**:
   - Show the final plan with the chosen values:
     ```bash
     gh arriba release [-R {owner/repo}] --version {version} [-f name=value ...] --dry-run
     ```
   - Use AskUserQuestion to ask: "Ready to create release {version}?"
     - Option 1: "Yes, create release (Recommended)"
     - Option 2: "Cancel"
   - If user selects cancel, exit without triggering the workflow

6. **Trigger the workflow**:
   ```bash
   gh arriba release [-R {owner/repo}] --version {version} [-f name=value ...] --yes
   ```
   - Pass `-f` only for inputs the user set. Defaults stay with the workflow
   - It prints the workflow run URL once the run appears

7. **Summary**:
   - Display: "Release workflow started for {owner/repo} version {version}"
   - Provide the workflow run URL for tracking
   - Show the command to follow the run: `gh run watch {run_id} --repo {owner/repo}`
