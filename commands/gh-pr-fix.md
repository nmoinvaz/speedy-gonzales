---
name: gh-pr-fix
description: Verify and fix unresolved PR review comments from humans, Copilot, or CodeRabbit
argument-hint: "[PR URL or number]"
allowed-tools: Bash, Edit, Grep, Read
---

Verify and fix unresolved PR review comments from any reviewer, human or bot.

## Arguments

$ARGUMENTS should be a GitHub PR URL (e.g., https://github.com/owner/repo/pull/123) or PR number, or empty to use the current branch's PR.

## Instructions

1. **Determine the PR**:
   - Pass $ARGUMENTS to `gh arriba` as is. It accepts a URL, a number, or nothing for the current
     branch's PR
   - When the PR lives in a different repo than the working directory, add `-R {owner}/{repo}` to
     every `gh arriba` call below
   - If no PR exists, `gh arriba` fails. Inform the user and exit

2. **Fetch all review comments**, from every reviewer:
   ```bash
   gh arriba pr threads $ARGUMENTS --review-bodies --json
   ```
   - `.pr` has the PR `number`, `url`, and `author`
   - `.threads[]` holds only unresolved, current threads. Each has the thread `id` (`PRRT_...`)
     used to resolve it, `path`, `line`, `start_line`, and `comments[]`, where each comment has
     the `id` used to reply, `author`, `bot`, and `body`
   - `.findings[]` holds the CodeRabbit findings that exist only in its review bodies, under the
     collapsed nitpick and outside-diff sections. Each has `path`, `start_line`, `line`, `title`,
     and `body`. Treat each as a comment with no thread, so it gets verified and fixed but never
     replied to or resolved

3. **Filter for reviewer comments**:
   - Keep threads whose first comment is from someone other than `.pr.author`, human or bot

4. **If no unresolved comments found**:
   - Inform the user: "No unresolved review comments found."
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
      user asked for. When the fix is exactly the reviewer's ```` ```suggestion ```` block, apply
      it with `gh arriba pr apply $ARGUMENTS --thread {thread_id}` instead. It needs the PR head
      checked out with no local changes to that file

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
        - Post the reply on stdin, so quotes and backticks survive. Add `--resolve` only when the
          thread's first comment has `bot: true`, since a human reviewer resolves their own once
          they have seen the fix:
          ```bash
          gh arriba pr reply {comment_id} - [--resolve] <<'EOF'
          {reply}
          EOF
          ```

9. **If "Skip with reply" selected**:
   - Write one terse sentence from the verification evidence stating why the comment is not being addressed
   - Post it without asking the user to review or edit it
   - Post a reply to the comment, adding `--resolve` when the issue is not real or not applicable.
     As in step 8d, only bot threads are resolved, a human reviewer closes their own:
     ```bash
     gh arriba pr reply {comment_id} - [--resolve] <<'EOF'
     {reason}
     EOF
     ```
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
- Bot reviewers such as `copilot-pull-request-reviewer` and `coderabbitai` have `bot: true` in the thread JSON. Everyone else is a human
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
