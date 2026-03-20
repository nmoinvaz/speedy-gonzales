---
name: commit-msg
description: Analyze staged git changes and generate commit message options with title and body
allowed-tools: Bash
---

# Commit message guidelines

Each commit message has a title and body, separated by a blank line. Match the existing commit formatting in the repository first; use these defaults where the repo has no clear convention.

**Title**:
- Aim for 50 characters, hard limit of 72 (keeps messages scannable in `git log --oneline` and avoids truncation)
- Use the imperative mood — write as a command, not a description. The title should complete the sentence: "If applied, this commit will ___"
- Lead with a strong action verb (e.g., Add, Fix, Refactor, Remove, Update, Replace, Extract, Simplify, Improve)
- Capitalize the first word and omit trailing periods

**Body**:
- Explain *what* changed and *why*, not *how* — the diff shows the how
- Only describe the final outcome; exclude investigative steps, failed attempts, or debugging detours from the conversation that led to the change
- 1-3 sentences providing context, motivation, or consequences not evident from the title
- Each sentence should add depth or highlight a distinct aspect of the change
- Wrap lines at 72 characters for readability in terminals and git tools

**Voice**: Read and follow the voice guidelines in `skills/code-voice/SKILL.md`

# Workflow

1. Get the staged diff for analysis:
   ```bash
   git diff --cached
   ```

2. Check previous commit message format in the repository:
   ```bash
   git log --oneline -10
   ```

3. Search staged changes for ticket IDs (patterns like PROJ-123, D4T-123, etc.)

4. Generate 3 distinct commit message options following the format above. Each option should use a different verb and framing — not rephrase the same sentence.

5. Follow these guidelines:
   - Match the format used in previous commits in the repository
   - If a ticket ID was found, include it in the title (typically as a prefix)
   - Do not add Claude as a co-author in the commit message

6. Present the options to the user for selection using AskUserQuestion

7. Create the commit with the selected title and body:
   ```bash
   git commit -m "<title>" -m "<body>"
   ```
