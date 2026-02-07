---
name: commit-msg
description: Analyze staged git changes and generate commit message options with title and body
allowed-tools: Bash
---

Analyze the staged changes and generate commit message options:

1. Get the staged diff for analysis:
   ```bash
   git diff --cached
   ```

2. Check previous commit message format in the repository:
   ```bash
   git log --oneline -10
   ```

3. Search staged changes for ticket IDs (patterns like PROJ-123, D4T-123, etc.)

4. Generate 3 commit message options. Each option should have:
   - **Title**:
     - Clear and concise summary
     - Under 72 characters
   - **Body**:
     - 1-3 sentences providing non-obvious value
     - Elaborate on the changes beyond what the title conveys
     - Each sentence should add depth or highlight a distinct aspect of the change
     - Explain the "why" or technical context not evident from the title
     - Word-break wrapped at 80 characters max per line

5. Follow these guidelines:
   - Match the format used in previous commits in the repository
   - If a ticket ID was found, include it in the title (typically as a prefix)
   - Do not add Claude as a co-author in the commit message

6. Present the options to the user for selection using AskUserQuestion

7. Create the commit with the selected title and body:
   ```bash
   git commit -m "<title>" -m "<body>"
   ```
