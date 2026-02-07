---
name: jira-fix-bug
description: Fetch a Jira bug report and attempt to fix it
argument-hint: "[Jira URL or issue key]"
model: opus
allowed-tools: Bash, Edit, Grep, Glob, Read
---

Fetch a Jira bug report and attempt to fix it.

## Arguments

$ARGUMENTS should be a Jira URL (e.g., https://company.atlassian.net/browse/PROJ-123) or a Jira issue key (e.g., PROJ-123).

## Instructions

1. **Extract issue key from argument**:
   - If $ARGUMENTS is a URL, extract the issue key from the `/browse/` part
   - If $ARGUMENTS is just a key (e.g., PROJ-123), use it directly
   - Validate the key format (should be PROJECT-NUMBER format)

2. **Fetch issue details**:
   Get full issue details including summary, description, status, priority, components, and labels.

3. **Fetch issue comments** for additional context.

4. **Display bug summary to user**:
   Present a clear summary of the bug:
   ```
   🐛 Jira Issue: {key}

   Summary: {summary}
   Status: {status}
   Priority: {priority}

   Description:
   {description}

   Recent Comments:
   {list recent comments if any}
   ```

5. **Search for similar issues**:
   Extract key terms from the summary and description, then search for related issues using JQL:
   - Search by text: `text ~ "{key-terms}" AND key != {issue-key}`
   - Search by component: `component = {component} AND key != {issue-key}`
   - Search recently resolved: `text ~ "{key-terms}" AND status in (Resolved, Done, Closed) AND resolved >= -30d`

   Display similar issues found:
   ```
   📋 Similar Issues Found:

   Open/In Progress:
   - {key}: {summary} ({status})

   Recently Resolved:
   - {key}: {summary} (Resolved {date})
   ```

   If similar issues are found, briefly note any patterns or common themes.

6. **Check git history for related changes**:
   - Search commit history for the issue key and similar issue keys:
     ```bash
     git log --all --grep="{issue-key}" --oneline
     git log --all --grep="{similar-issue-key}" --oneline
     ```
   - Search for commits related to affected files or components:
     ```bash
     git log --all --grep="{key-terms}" --oneline
     ```
   - For relevant commits, examine the actual changes:
     ```bash
     git show {commit-hash}
     # OR for file-specific history
     git log -p -- {file-path}
     ```
   - Look for fix patterns:
     - What files were changed in similar bug fixes?
     - What was the fix approach (e.g., adding missing props, changing state order, etc.)?
     - Were multiple files changed following the same pattern?
     - Was the current bug's file missed in a previous fix?

   Display git history findings:
   ```
   📜 Git History:

   Related commits:
   - {hash}: {message} (fixed {similar-issue-key})
   - {hash}: {message}

   Fix pattern observed:
   {description of what the fix did and how}

   Files changed in similar fixes:
   - {file1}
   - {file2}
   - {file3} (current bug file - was it missed?)
   ```

7. **Analyze the bug**:
   - Read the description and comments carefully
   - Review any similar issues found for additional context
   - Review git history findings for fix patterns
   - Identify what the bug is about
   - Look for:
     - Error messages or stack traces
     - Steps to reproduce
     - Expected vs actual behavior
     - Affected files or components mentioned
     - Patterns from similar issues
     - Patterns from related git commits
   - If the description mentions specific files, search for them in the codebase
   - Consider: Was this file missed in a previous related fix?

8. **Search the codebase**:
   - Use the Grep tool to search for relevant code mentioned in the bug
   - Use the Glob tool to find files related to the issue
   - Use the Task tool with subagent_type=Explore if you need to broadly explore the codebase
   - Read relevant files to understand the current implementation
   - If a fix pattern was identified from git history, check if other files need the same fix:
     - Search for files with similar patterns to those fixed previously
     - Check if they have the bug or have already been fixed

9. **Propose a fix**:
   - Explain what you found and what you think the issue is
   - Reference any similar issues that informed your understanding
   - Reference git history and fix patterns that informed your approach
   - If this file was missed in a previous fix, explain that clearly
   - Propose a solution with specific code changes
   - If the fix pattern suggests other files might need the same fix, mention those too
   - Ask the user: "Would you like me to implement this fix?"
     - Use AskUserQuestion with options:
       - "Yes, implement the fix (Recommended)"
       - "No, just explain the issue"
       - "Search for more information first"

10. **If user approves, implement the fix**:
    - Make the necessary code changes using the Edit tool
    - If multiple files need the same fix pattern, apply it to all affected files
    - Run relevant tests if applicable
    - Create a summary of changes made

11. **Create commit**:
    - Use the `commit-msg` skill to generate commit message options and create the commit

12. **Update Jira issue** (ask for permission first):
    - Ask user: "Would you like me to add a comment to the Jira issue?"
    - If yes, add a comment with:
      - Brief description of the fix
      - Files changed
      - Link to commit (if available)
      - Reference to similar issues and related commits if relevant

13. **Ask about status transition**:
    - Ask user: "Would you like to transition this issue?"
    - Show available transitions and let user choose (e.g., "In Progress", "In Review", "Done")

## Important Notes

- Always read and understand the bug thoroughly before proposing changes
- Similar issues can provide valuable context and may reveal if this is part of a larger pattern
- Git history is crucial - related commits often reveal the exact fix pattern needed
- Look for cases where a file was missed in a previous related fix
- If the bug description is unclear, ask the user for clarification
- If you cannot find the relevant code, tell the user and ask for guidance
- Do not make changes without user approval
- Be cautious about making large changes - prefer small, targeted fixes
- When a fix pattern is identified, check if other files need the same fix
