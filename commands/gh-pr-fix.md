---
name: gh-pr-fix
description: Verify and fix unresolved PR review comments from Copilot or CodeRabbit
argument-hint: "[PR URL or number]"
allowed-tools: Bash, Edit, Grep, Read
---

Verify and fix unresolved PR review comments from Copilot or CodeRabbit.

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
   CodeRabbit also lists findings in its review bodies with no thread, under collapsed nitpick and
   outside-diff sections. Fetch those too and treat each `path:line` entry as a comment with no
   thread, so it gets verified and fixed but never replied to or resolved:
   ```bash
   gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews --paginate \
     --jq '.[] | select(.user.login == "coderabbitai[bot]") | .body'
   ```

3. **Filter for unresolved Copilot/CodeRabbit comments**:
   - Filter comments where `user.login` is `copilot-pull-request-reviewer` or `coderabbitai[bot]`
   - Exclude comments that are part of resolved review threads
   - Check if comment is in a resolved thread using the `in_reply_to_id` field and thread resolution status
   - Fetch the review threads, which carry the thread `id` needed to resolve them later:
     ```bash
     gh api graphql --paginate --slurp -f query='
       query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
         repository(owner: $owner, name: $repo) {
           pullRequest(number: $pr) {
             reviewThreads(first: 100, after: $endCursor) {
               pageInfo { hasNextPage endCursor }
               nodes {
                 id
                 isResolved
                 isOutdated
                 comments(first: 10) {
                   nodes {
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
   - Only include threads where `isResolved` and `isOutdated` are both `false`
   - Match each REST comment to its thread by `databaseId`, and keep the thread `id` for resolving

4. **If no unresolved comments found**:
   - Inform the user: "No unresolved comments from Copilot or CodeRabbit found."
   - Exit

5. **Process each unresolved comment one at a time**:
   Verify silently first, then display one block per comment (step 6e). Surface what bears on the
   decision, enough to judge the verdict without opening the PR.

6. **Verify the issue is real**:
   a. Clearly restate the comment as one testable claim

   b. Read the code around the referenced line

   c. Check the claim against the code:
      - Trace callers and types with Grep
      - Look for an existing guard or check
      - Verify library behavior against its source
      - Run a test when that is cheaper than reasoning

   d. **Check git history for context** when the code looks deliberate:
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

      Fold anything relevant into the verdict's reason. Do not print a separate history block.

   e. Display the comment and verdict as one block:
      ```
      Comment {N} of {total}  {path}:{line}  {author}
      {comment body trimmed to its point, drop details blocks, suggestion blocks, and AI prompts}

      Claim: {one sentence}
      🔍 {Real | Partially real | Not real | Unclear}: {one or two sentences giving the reason}
      For: {code lines or command output that support the claim, a few lines at most}
      Against: {what cuts the other way, omit the line when nothing does}
      ```
      Partially real means the problem is real but the reviewer's fix is wrong or overstated.
      Add one line of git history only when it changed the verdict.

   f. When Real or Partially real, follow the block with the proposed fix as a `diff` code block.
      This is the user's only look at the change before it is committed, so make it complete: the
      same fix anywhere else the pattern appears, plus any include or declaration it needs.

7. **Ask user what to do**:
   This is the only prompt for the comment. Use AskUserQuestion with options, recommending the
   first when Real or Partially real and the third when Not real:
   - **Fix it** - Apply the diff shown above and commit it
   - **Fix it differently** - Say what to change, then it is applied and committed
   - **Skip with reply** - Skip and reply with a reason
   - **Skip** - Move to the next comment without action

8. **If "Fix it" or "Fix it differently" selected**:
   a. For "Fix it differently", ask what to change and fold it into the fix

   b. Implement the fix using the Edit tool, applying the diff shown in step 6f plus whatever the
      user asked for

   c. If the applied change differs from the diff shown, show only the difference as a `diff`
      code block, for information. Do not ask again, the user already chose to fix it.

   d. Stage, commit, reply, and resolve without asking:
      - Stage the changed files: `git add {file_paths}`
      - Commit the fix with a concise message describing the change
      - **Reply to the comment** in one terse sentence without asking the user. Review-body
        findings have no thread, so skip the reply and the resolve for those:
        - If the fix addresses the concern directly: reply "Fixed."
        - If Partially real: one sentence saying what was fixed instead and why
        - If the reviewer's assumption was incorrect: one sentence saying why
        - Post the reply, piping the body through jq so quotes and backticks survive:
          ```bash
          jq -Rs '{body: rtrimstr("\n")}' <<'EOF' | gh api repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies --input -
          {reply}
          EOF
          ```
      - Resolve the review thread using the `id` from the thread query:
        ```bash
        gh api graphql -f query='
          mutation($threadId: ID!) {
            resolveReviewThread(input: {threadId: $threadId}) {
              thread { isResolved }
            }
          }
        ' -f threadId={thread_id}
        ```

9. **If "Skip with reply" selected**:
   - Write one terse sentence from the verification evidence stating why the comment is not being addressed
   - Post it without asking the user to review or edit it
   - Post a reply to the comment:
     ```bash
     jq -Rs '{body: rtrimstr("\n")}' <<'EOF' | gh api repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies --input -
     {reason}
     EOF
     ```
   - Resolve the thread with the mutation from step 8d if the issue is not real or not applicable
   - Review-body findings have no thread, so skip both and move on

10. **If "Skip" selected**:
    - Move to the next comment without any action

11. **Repeat** for all remaining unresolved comments

12. **Final summary**:
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

13. **Ask about pushing**:
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
- One prompt per comment, the fix is committed without a second confirmation
- Comments are verified before any action so false positives get a reply, not a patch
- Each fix creates its own atomic commit for easy tracking and potential reverting
- Bot accounts to look for: `copilot-pull-request-reviewer`, `coderabbitai[bot]`
- If a file has multiple comments, they are still processed one at a time
- Show one compact block per comment, the claim and the verdict, before asking for action
- Surface what is relevant to the decision, enough to judge the verdict, and omit history or diffs that do not change it
- Git history analysis helps understand why code was written a certain way and reveals fix patterns
- If a fix pattern is identified, check if other files might need the same change

## Types of Fixes

Not all fixes require changing code behavior. Valid fixes include:
- **Code changes**: Modifying logic, adding error handling, etc.
- **Adding clarifying comments**: When the reviewer misunderstands existing behavior, adding a comment to clarify can be the appropriate fix
- **Documentation updates**: Improving docstrings or inline documentation

## Reply Guidelines

Replies are one terse sentence, posted without asking the user how to word them:
- **Direct fix**: "Fixed."
- **Partially real**: State what was fixed instead and why
- **Not real**: State why, citing the evidence (e.g., "This is cached internally, so it does not contact the server on every call.")
- **Skipped**: State why it is not being addressed
- No preamble, no thanks, no restating the comment
