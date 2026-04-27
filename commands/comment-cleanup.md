---
name: comment-cleanup
description: Walk through changed code comments and pick a writing variation for each
argument-hint: "[git ref or range]"
allowed-tools: Bash, Edit, Read
---

Walk through every code comment that was added or modified in the current changes and offer rewriting variations with different levels of conciseness and technical detail.

All rewrite suggestions must follow the voice and style guidance in `/arriba:code-voice`.

## Arguments

`$ARGUMENTS` is an optional git ref or range that scopes which diff to scan:
- A single ref (e.g. `main`, `HEAD~3`) → diff `<ref>..HEAD` plus working-tree changes
- A range (e.g. `main...HEAD`) → use as-is
- Empty → diff vs the merge-base with the default branch, plus working-tree changes

## Instructions

1. **Determine the diff scope**:
   - If `$ARGUMENTS` is set, use it
   - Otherwise:
     - Detect the default branch:
       ```bash
       git remote show origin 2>/dev/null | sed -n 's/.*HEAD branch: //p'
       ```
       Fall back to `main`, then `master` if origin is unreachable
     - Find the merge-base: `git merge-base HEAD <default-branch>`
     - Scope: `<merge-base>..HEAD` plus working-tree (staged + unstaged) changes
   - Print the resolved scope to the user before proceeding

2. **Collect changed comment lines**:
   - Get the unified diff for the scope:
     ```bash
     git diff <scope> --unified=0 -- ':!*.lock' ':!*.sum' ':!vendor/*' ':!node_modules/*'
     ```
   - For each `+` line, decide if it is (or contains a changed portion of) a code comment, based on the file extension:
     - `//`, `///`, `//!` — C, C++, Rust, Go, Java, JS/TS, Swift, Kotlin, C#, Scala
     - `#` — Python, Ruby, Shell, YAML, TOML, Makefile, Dockerfile, Perl
     - `/* … */` — C, C++, Java, JS/TS, CSS, Rust block comments (handle multi-line spans as one comment)
     - `<!-- … -->` — HTML, XML, Markdown
     - `--` — SQL, Lua, Haskell, Ada
     - `;` — Lisp/Scheme/Clojure, ASM, INI
     - `"""…"""` / `'''…'''` — Python docstrings (treat the whole block as one comment)
   - Skip pure removals (a `-` comment line with no matching `+`) — no point rewriting deleted comments
   - For modified comments (a `-`/`+` pair on the same comment), treat the new version as the candidate
   - Skip comments inside files matched by `.gitignore`-style ignore lists already filtered above
   - Deduplicate when a multi-line block comment spans several `+` lines — present it as one entry

3. **If no candidates are found**:
   - Tell the user "No added or modified code comments found in the selected scope." and exit

4. **Survey project-level comment conventions** (once, before processing any comment):
   - Pick a representative sample of source files in the repo. Bias toward files that share a language with the candidates and toward files the candidates already live in.
   - Read enough of those files to characterise:
     - Typical comment density (sparse, moderate, heavy).
     - Preferred form (single-line `//` / `#` vs block `/* */` vs docstrings).
     - Where comments cluster (function headers, non-obvious branches, public API only, TODOs).
     - Tone (terse fragments, full sentences, formal doc comments).
     - Whether the project uses a documented doc-comment dialect (rustdoc, godoc, JSDoc, Doxygen, etc.).
     - Anything the project deliberately does *not* comment (e.g. obvious code, getters).
   - Look for an explicit style guide in the repo: `CONTRIBUTING.md`, `STYLE.md`, `docs/style*`, language-specific lint configs (`.clang-format`, `rustfmt.toml`, `.eslintrc*`, `pyproject.toml`).
   - Keep this survey in working memory; reuse it for every candidate. Do not re-survey per comment.

5. **Show a one-line preview list first**:
   ```
   Found {N} changed comments:
     1. path/to/file.rs:42  // current first line of the comment …
     2. path/to/file.py:117 # …
     …
   ```
   Then proceed through them one at a time.

6. **For each comment**, display:
   ```
   Comment {i} of {N}
   ─────────────────────────────
   File: {path}:{line}
   Language: {detected}

   Surrounding code:
   {3–5 lines of context above and below}

   Current comment:
   {comment text exactly as it appears}
   ─────────────────────────────
   ```

7. **Generate rewriting variations**:
   - Read the file around the comment with the Read tool to understand what code the comment is annotating.
   - The first time a candidate from a given file is reached, also sample comments elsewhere in that same file to capture **local** convention: do nearby comments name invariants, link to specs, stay terse, sit above functions, sit beside lines? Cache this per file and reuse it for the rest of that file's candidates.
   - Reconcile the project survey, the local file convention, `/arriba:code-voice`, and these baseline rules:
     - Comment the **why**, not the **what**
     - Single-line preferred, word-break at ~100 characters
     - Don't reference the current task, ticket, or caller (those rot)
     - If a comment only restates obvious code, prefer suggesting **Delete**
   - When project or file convention conflicts with the baseline guidance, prefer the project's convention — the surrounding code is the live style guide. Call out the conflict to the user only if it materially changes the suggestion.
   - Produce up to four rewrite options that span the conciseness × technical-detail axis:
     1. **Terse** — shortest plausible form. Fragment, drop articles, just the load-bearing words.
     2. **Concise** — one short complete sentence stating the intent or the non-obvious why.
     3. **Detailed** — one sentence that names the specific invariant, constraint, edge case, or external reference (spec, RFC, standard) that justifies the code. No ticket numbers, no "added for X".
     4. **Multi-line** — only if the why genuinely needs more than one line; otherwise omit this option. Each line word-wrapped at ~100 chars and prefixed with the same comment syntax.
   - Every variation must:
     - Preserve the original comment syntax (`//`, `#`, `/* */`, etc.)
     - Preserve the original indentation
     - Stay within ~100 characters per line

8. **Ask the user to choose**:
   Use AskUserQuestion with the generated variations as options, plus:
   - **Keep current** — leave the comment unchanged
   - **Delete** — remove the comment entirely (recommend this in the question text when the comment only restates the code)
   - **Edit** — let me write my own
   - **Skip** — move on without deciding

9. **Apply the choice**:
   - Variation chosen → use Edit to replace the exact comment text
   - **Edit** → ask the user for the replacement text, then apply
   - **Delete** → remove the comment line(s); also remove a trailing blank line if removal would leave a doubled blank
   - **Keep current** / **Skip** → no file change
   - After any file change, re-read the file to confirm the edit landed cleanly before moving on

10. **Move to the next comment** and repeat. If a later comment lives in a file already edited, recompute its line number from the current file before applying.

11. **Final summary**:
    ```
    Comment Cleanup Summary
    ══════════════════════════════════════
    Comments reviewed: {N}
    - Rewritten:  {count}
    - Deleted:    {count}
    - Kept:       {count}
    - Skipped:    {count}

    Files modified:
      - {path}
      - {path}
    ```

12. **Offer to stage the changes**:
    - Show `git diff -- <files-modified>` so the user can eyeball the result
    - Use AskUserQuestion to ask whether to stage:
      - **Stage all** → `git add <files-modified>`
      - **Leave unstaged**

## Notes

- Every rewrite — Terse, Concise, Detailed, Multi-line, or user **Edit** — must follow `/arriba:code-voice`.
- Only modify comments. Never touch surrounding code.
- Preserve indentation, comment markers, and trailing whitespace policy of the file.
- Treat multi-line `/* … */` blocks and Python docstrings as a single comment unit.
- Skip generated, vendored, and lock files.
- Line numbers shift after edits — always recompute from the current file state, don't trust the original diff offsets.
