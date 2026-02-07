---
name: branch
description: Create a new git branch with naming conventions based on repository patterns
allowed-tools: Bash
---

Create a new branch following the repository's naming conventions:

1. **Determine branch type**:
   - Use AskUserQuestion with options:
     - "Feature branch"
     - "Bug fix branch"

2. **Analyze repository branch naming conventions**:
   - Get recent branch names:
     ```bash
     git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short)' --count=20
     ```
   - Look for patterns like:
     - `feature/TICKET-123-description`
     - `bugfix/TICKET-123-description`
     - `username/feature/TICKET-123-description`
     - `TICKET-123-description`

3. **Search for ticket IDs**:
   - Check the conversation history for any mentioned ticket IDs (patterns like PROJ-123, etc.)
   - If there are staged changes, search them for ticket IDs
   - If no ticket ID found, ask the user for a ticket ID or description

4. **Generate branch name**:
   - Follow the repository's detected convention
   - **For bug fix branches, add incremental suffix**:
     - Check for existing branches matching the base name pattern:
       ```bash
       git branch --list '<base-branch-name>*'
       ```
     - If no matches exist, append `/1` to the branch name
     - If matches exist (e.g., `bugfix/PROJ-123/1`, `bugfix/PROJ-123/2`), use the next number
     - Example: if `bugfix/PROJ-123/1` and `bugfix/PROJ-123/2` exist, create `bugfix/PROJ-123/3`

5. **Confirm and create**:
   - Present the suggested name and ask for confirmation or modification
   - Create the branch: `git checkout -b <branch-name>`
