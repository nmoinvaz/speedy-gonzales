---
name: cq-review
description: Run a full code quality review using 6 parallel specialized agents
allowed-tools: Bash, Read, Grep, Glob, Write, Task
---

# Full Code Quality Review — 6 Parallel Agents

Run a comprehensive code quality review by launching 6 specialized subagents in parallel. Each agent focuses on one dimension of code quality, produces an independent report, and **saves it to disk**.

## Setup

Before launching agents, create the output directory:

```bash
mkdir -p .code-quality
```

## Instructions

Launch ALL 6 of the following agents simultaneously using the Task tool (all in a single message, so they run in parallel). Each uses `subagent_type: "general-purpose"`.

Each agent will save its own report to `.code-quality/<dimension>.md`. After all 6 complete, you will synthesize their findings into a unified summary and save that too.

---

### Agent 1: Readability & Naming

Prompt: Read the contents of `commands/cq-readability.md` and follow the agent instructions within it to analyze this repository. IMPORTANT: Save your report to `.code-quality/readability.md` in the repository root.

### Agent 2: Duplication & DRY

Prompt: Read the contents of `commands/cq-duplication.md` and follow the agent instructions within it to analyze this repository. IMPORTANT: Save your report to `.code-quality/duplication.md` in the repository root.

### Agent 3: Structure & Complexity

Prompt: Read the contents of `commands/cq-structure.md` and follow the agent instructions within it to analyze this repository. IMPORTANT: Save your report to `.code-quality/structure.md` in the repository root.

### Agent 4: Formatting & Style Consistency

Prompt: Read the contents of `commands/cq-formatting.md` and follow the agent instructions within it to analyze this repository. IMPORTANT: Save your report to `.code-quality/formatting.md` in the repository root.

### Agent 5: Error Handling & Robustness

Prompt: Read the contents of `commands/cq-error-handling.md` and follow the agent instructions within it to analyze this repository. IMPORTANT: Save your report to `.code-quality/error-handling.md` in the repository root.

### Agent 6: Coupling & Cohesion

Prompt: Read the contents of `commands/cq-coupling.md` and follow the agent instructions within it to analyze this repository. IMPORTANT: Save your report to `.code-quality/coupling.md` in the repository root.

---

## After All Agents Complete

1. **Read the saved reports** from `.code-quality/` to get each agent's findings (especially their Executive Summary and grades).
2. **Synthesize** them into a unified final summary.
3. **Save the final summary** to `.code-quality/SUMMARY.md`.

Use this format for the final summary:

```
# Code Quality Review — Final Summary
> Generated: [current date]
> Repository: [repo name/path]

## Scorecard
| Dimension               | Grade | Key Issue                  |
|------------------------|-------|----------------------------|
| Readability & Naming    | ?     | ...                        |
| Duplication & DRY       | ?     | ...                        |
| Structure & Complexity  | ?     | ...                        |
| Formatting & Style      | ?     | ...                        |
| Error Handling          | ?     | ...                        |
| Coupling & Cohesion     | ?     | ...                        |
| **Overall**             | ?     |                            |

## Top 10 Findings Across All Dimensions
1. ...

## Prioritized Action Plan
### Quick Wins (< 1 hour each)
- ...

### Medium Effort (1-4 hours each)
- ...

### Major Refactors (> 4 hours)
- ...

## Individual Reports
- [Readability & Naming](readability.md)
- [Duplication & DRY](duplication.md)
- [Structure & Complexity](structure.md)
- [Formatting & Style](formatting.md)
- [Error Handling](error-handling.md)
- [Coupling & Cohesion](coupling.md)
```

This gives a complete, persistent record of the review in `.code-quality/` that survives context compaction and can be referenced in future conversations.
