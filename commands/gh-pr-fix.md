---
name: gh-pr-fix
description: Fix unresolved PR review comments from Copilot or CodeRabbit
argument-hint: "[PR URL or number]"
allowed-tools: Bash, Edit, Grep, Read
---

Fix unresolved PR review comments from Copilot or CodeRabbit.

## Arguments

$ARGUMENTS should be a GitHub PR URL (e.g., https://github.com/owner/repo/pull/123) or PR number, or empty to use the current branch's PR.

## Instructions

1. **Determine the PR**:
   - If $ARGUMENTS is a URL, parse the owner, repo, and PR number
   - If $ARGUMENTS is a number, use it with the current repo
   - If $ARGUMENTS is empty, get the PR for the current branch:
     ```bash
     gh pr view --json number,url
     ```
   - If no PR exists, inform the user and exit

2. **Fetch all review comments**:
   ```bash
   gh api repos/{owner}/{repo}/pulls/{pr_number}/comments --paginate
   ```

3. **Filter for unresolved Copilot/CodeRabbit comments**:
   - Filter comments where `user.login` is `copilot-pull-request-reviewer` or `coderabbitai[bot]`
   - Exclude comments that are part of resolved review threads
   - Check if comment is in a resolved thread using the `in_reply_to_id` field and thread resolution status
   - To check resolution status, you may need to fetch review threads:
     ```bash
     gh api graphql -f query='
       query($owner: String!, $repo: String!, $pr: Int!) {
         repository(owner: $owner, name: $repo) {
           pullRequest(number: $pr) {
             reviewThreads(first: 100) {
               nodes {
                 isResolved
                 comments(first: 10) {
                   nodes {
                     id
                     databaseId
                     body
                     author { login }
                     path
                     line
                   }
                 }
               }
             }
           }
         }
       }
     ' -f owner={owner} -f repo={repo} -F pr={pr_number}
     ```
   - Only include threads where `isResolved` is `false`

4. **If no unresolved comments found**:
   - Inform the user: "No unresolved comments from Copilot or CodeRabbit found."
   - Exit

5. **Process each unresolved comment one at a time**:
   For each comment, display:
   ```
   Comment {N} of {total}
   ─────────────────────────────
   File: {path}:{line}
   From: {author}

   {comment body}
   ─────────────────────────────
   ```

6. **Ask user what to do**:
   Use AskUserQuestion with options:
   - **Fix it** - Attempt to fix this issue
   - **Skip with reply** - Skip and reply with a reason
   - **Skip** - Move to the next comment without action

7. **If "Fix it" selected**:
   a. Read the relevant file and understand the context around the line mentioned

   b. **Check git history for context**:
      - Get the history of the specific file:
        ```bash
        git log --oneline -10 -- {file_path}
        ```
      - Look at recent changes to the affected lines:
        ```bash
        git log -p -3 -- {file_path}
        ```
      - Search for related commits that might explain the current code:
        ```bash
        git log --all --oneline --grep="{function_name or key_term}"
        ```
      - If relevant commits are found, examine them:
        ```bash
        git show {commit-hash}
        ```
      - Look for patterns:
        - Why was the code written this way originally?
        - Were there previous attempts to fix similar issues?
        - Is this part of a pattern that exists elsewhere in the codebase?

      Display git history findings if relevant:
      ```
      📜 Git History Context:

      Recent changes to {file}:
      - {hash}: {message}
      - {hash}: {message}

      Related commits:
      - {hash}: {message}

      Context: {brief explanation of why code is structured this way}
      ```

   c. Analyze the comment to understand what change is being requested

   d. **Search for similar patterns** in the codebase if the fix might apply elsewhere:
      - Use Grep to find similar code patterns
      - Note if other files might need the same fix

   e. Implement the fix using the Edit tool

   f. Show the diff of your changes:
      ```bash
      git diff {file_path}
      ```

   g. Ask user to accept or reject using AskUserQuestion:
      - **Accept** - Stage and commit this fix
      - **Reject** - Discard changes and move to next comment
      - **Edit** - Let me modify the fix before accepting

   h. If "Accept" selected:
      - Stage the changed file: `git add {file_path}`
      - Use the `commit-msg` skill to generate commit message options and create the commit
      - **Reply to the comment** explaining what was done:
        - If the fix addresses the concern directly: reply "Ok will fix"
        - If the reviewer's assumption was incorrect: explain why (e.g., "The assumption that X happens is incorrect because Y. Added a comment to clarify this.")
        - Post the reply:
          ```bash
          gh api repos/{owner}/{repo}/pulls/{pr_number}/comments \
            -f body="{reply}" \
            -F in_reply_to={comment_id}
          ```
      - Resolve the review thread:
        ```bash
        gh api graphql -f query='
          mutation($threadId: ID!) {
            resolveReviewThread(input: {threadId: $threadId}) {
              thread { isResolved }
            }
          }
        ' -f threadId={thread_node_id}
        ```

   i. If "Reject" selected:
      - Discard changes: `git checkout -- {file_path}`
      - Move to next comment

   j. If "Edit" selected:
      - Ask user what they want to change
      - Apply their requested modifications
      - Show the new diff and repeat the accept/reject question

8. **If "Skip with reply" selected**:
   - Ask user for the reason using AskUserQuestion with text input option
   - Post a reply to the comment:
     ```bash
     gh api repos/{owner}/{repo}/pulls/{pr_number}/comments \
       -f body="{reason}" \
       -F in_reply_to={comment_id}
     ```
   - Optionally resolve the thread if the user indicates the issue is not applicable

9. **If "Skip" selected**:
   - Move to the next comment without any action

10. **Repeat** for all remaining unresolved comments

11. **Final summary**:
    After processing all comments, show a summary:
    ```
    PR Review Comments Summary
    ══════════════════════════════════════
    Total comments processed: {N}
    - Fixed and committed: {count}
    - Skipped with reply: {count}
    - Skipped: {count}

    Commits created:
    - {hash}: {title}
    - {hash}: {title}
    ```

12. **Ask about pushing**:
    If any commits were created:
    - **Analyze commits for squash candidates**:
      - Group commits that touch the same file
      - Group commits with related themes (e.g., "OAuth2 improvements", "error handling")
      - Commits touching completely different files with unrelated purposes are NOT squash candidates
    - Present options using AskUserQuestion:
      - "Push as-is (Recommended)" - if no good squash candidates exist
      - "Squash: {commit1} + {commit2} → '{suggested title}'" - for each squash candidate group
      - "Don't push yet"
    - If squashing, use interactive rebase to combine, then push
    - If push as-is: `git push`

## Notes

- The command processes comments one at a time to allow careful review
- Each fix creates its own atomic commit for easy tracking and potential reverting
- Bot accounts to look for: `copilot-pull-request-reviewer`, `coderabbitai[bot]`
- If a file has multiple comments, they are still processed one at a time
- Always show the full context of the comment before asking for action
- Git history analysis helps understand why code was written a certain way and reveals fix patterns
- If a fix pattern is identified, check if other files might need the same change

## Types of Fixes

Not all fixes require changing code behavior. Valid fixes include:
- **Code changes**: Modifying logic, adding error handling, etc.
- **Adding clarifying comments**: When the reviewer misunderstands existing behavior, adding a comment to clarify can be the appropriate fix
- **Documentation updates**: Improving docstrings or inline documentation

## Reply Guidelines

When replying to comments after fixing:
- **Direct fix**: Reply "Ok will fix" when the fix addresses the concern as requested
- **Incorrect assumption**: If the reviewer's assumption is wrong, explain why (e.g., "The assumption that this contacts the server on every call is incorrect - the implementation uses internal caching. Added a comment to clarify.")
- Keep replies concise but informative
