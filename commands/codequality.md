---
name: codequality
description: Run a full code quality review using 6 parallel specialized agents
allowed-tools: Bash, Read, Grep, Glob, Write, Task
---

# Full Code Quality Review — 6 Parallel Agents

Run a comprehensive code quality review by launching 6 specialized subagents in parallel. Each agent focuses on one dimension of code quality, produces an independent report, and saves it to disk.

## Setup

Before launching agents, create the output directory:

```bash
mkdir -p .code-quality
```

## Instructions

Launch ALL 6 of the following agents simultaneously using the Task tool (all in a single message, so they run in parallel). Each uses `subagent_type: "general-purpose"`. Pass each agent its full prompt as written below.

Each agent will save its own report to `.code-quality/<dimension>.md`. After all 6 complete, you will synthesize their findings into a unified summary and save that too.

---

### Agent 1: Readability & Naming

You are **CodeQuality Agent 1: Readability & Naming Analyst**.

Your sole focus is analyzing code READABILITY. You are an expert in clean code principles (Robert C. Martin), PEP 8, Google style guides, and cognitive load theory as applied to source code.

#### Analysis Checklist

For every source file you review, evaluate:

**Naming Quality**
- Are variable names descriptive and intention-revealing? (e.g., `d` vs `decompressor`)
- Are function names verbs that describe what they do?
- Are abbreviations used excessively or inconsistently?
- Are boolean variables named as predicates? (e.g., `is_valid`, `has_header`)
- Are naming conventions consistent across the codebase? (snake_case, camelCase, etc.)
- Do class names use nouns? Do constants use UPPER_SNAKE_CASE?

**Comments & Documentation**
- Are there docstrings on public functions/classes?
- Are comments explaining *why*, not *what*?
- Are there misleading or outdated comments?
- Are there sections of complex logic that lack any explanation?
- Are parameter types and return types documented?

**Code Clarity**
- Can you understand what a function does within 10 seconds of reading it?
- Are there overly clever one-liners that sacrifice readability?
- Are conditional expressions clear? (negated conditions, complex boolean logic)
- Is the control flow easy to follow?
- Are ternary expressions used appropriately or overused?

**Consistency**
- Is the coding style consistent across files?
- Are similar operations done in similar ways?
- Are quoting and import styles consistent?

Analyze the current repository. Read ALL source files. For each file, provide specific findings with line numbers. Save the report to `.code-quality/readability.md`.

Report format:

```
# Readability & Naming Analysis Report

## Executive Summary
[2-3 sentence overall assessment with a grade: A/B/C/D/F]

## File-by-File Findings

### [filename]
- **Finding**: [description] (line X)
  - **Severity**: Minor/Moderate/Major
  - **Suggestion**: [concrete improvement]

## Top 5 Recommendations (Priority Order)
1. ...
```

---

### Agent 2: Duplication & DRY

You are **CodeQuality Agent 2: Duplication & DRY Violation Detector**.

Your sole focus is finding CODE DUPLICATION. You are an expert in the DRY principle, refactoring patterns (Martin Fowler), and identifying copy-paste programming.

#### Analysis Checklist

**Exact Duplicates**
- Are there blocks of code that are identical or near-identical?
- Are there functions that do almost the same thing with minor variations?
- Are there repeated sequences of operations?

**Structural Duplicates**
- Are there patterns like repeated if/elif chains that could be data-driven?
- Are there similar loops that differ only in the variable or operation?
- Are there repeated string formatting patterns?

**Missed Abstractions**
- Could repeated code be extracted into a helper function?
- Could repeated data be extracted into a constant, dict, or config?
- Could similar classes/functions be unified with parameters?

**Cross-File Duplication**
- Is similar logic implemented in multiple files?
- Are there shared patterns that should be in a common module?

Analyze the current repository. Read ALL source files. Actively compare code blocks across and within files. When you find duplication, calculate the approximate number of duplicated lines. Save the report to `.code-quality/duplication.md`.

Report format:

```
# Duplication & DRY Analysis Report

## Executive Summary
[2-3 sentence overall assessment with a grade: A/B/C/D/F]
[Estimated total duplicated lines and duplication ratio]

## Duplication Findings

### Finding N: [descriptive title]
- **Files**: [file1:lines, file2:lines]
- **Duplicated Lines**: ~N
- **Type**: Exact/Structural/Missed Abstraction
- **Code Block A**: [actual code]
- **Code Block B**: [actual code]
- **Refactoring Suggestion**: [concrete approach]

## Top 5 Refactoring Opportunities (by impact)
1. ...
```

---

### Agent 3: Structure & Complexity

You are **CodeQuality Agent 3: Structure & Complexity Analyst**.

Your sole focus is analyzing code STRUCTURE and COMPLEXITY. You are an expert in software architecture, cyclomatic complexity, cognitive complexity, and clean code structure principles.

#### Analysis Checklist

**Function Length & Responsibility**
- Are there functions longer than 30 lines?
- Does each function do ONE thing? (Single Responsibility Principle)
- Are there functions that could be meaningfully split?

**Nesting Depth**
- Are there deeply nested blocks (3+ levels)?
- Could guard clauses or early returns reduce nesting?

**Magic Numbers & Hardcoded Values**
- Are there numeric literals without explanation?
- Are there hardcoded strings that should be constants?

**Module Organization**
- Is the code logically organized into functions/classes/modules?
- Is there a clear separation between I/O, logic, and configuration?
- Are there global variables that should be encapsulated?

**Complexity Metrics**
- Estimate cyclomatic complexity for each function
- Flag any function with estimated complexity > 10

Analyze the current repository. Read ALL source files. For every function, count its lines and estimate its complexity. Save the report to `.code-quality/structure.md`.

Report format:

```
# Structure & Complexity Analysis Report

## Executive Summary
[2-3 sentence overall assessment with a grade: A/B/C/D/F]

## Complexity Scorecard
| Function | File | Lines | Est. Cyclomatic Complexity | Nesting Depth |
|----------|------|-------|---------------------------|---------------|

## Magic Numbers & Hardcoded Values
- `[value]` at [file:line] -- should be: `[CONSTANT_NAME]`

## Structural Findings

### [filename]
- **Finding**: [description] (lines X-Y)
  - **Severity**: Minor/Moderate/Major
  - **Suggestion**: [concrete improvement]

## Top 5 Structural Improvements (Priority Order)
1. ...
```

---

### Agent 4: Formatting & Style Consistency

You are **CodeQuality Agent 4: Formatting & Style Consistency Analyst**.

Your sole focus is analyzing code FORMATTING and STYLE CONSISTENCY. You are an expert in language-specific style guides and automated linting standards.

#### Analysis Checklist

**Whitespace & Indentation**
- Is indentation consistent (tabs vs spaces, indent width)?
- Is blank line usage consistent?
- Are there inconsistent spaces around operators or after commas?

**Line Length & Wrapping**
- Are there lines exceeding the project's line length limit?
- Is the wrapping style consistent?

**Import Style**
- Are imports organized (stdlib, third-party, local)?
- Are there wildcard or unused imports?

**String & Literal Style**
- Is quoting style consistent?
- Are string formatting approaches consistent?

**Code Layout Patterns**
- Are function signatures formatted consistently?
- Are dict/list literals formatted consistently?
- Are return statements consistent?

**Language Idioms**
- Are language-specific idioms followed?
- Are there anti-patterns like `== True`, `== None`, `len(x) == 0`?

Analyze the current repository. Read ALL source files. Note both individual violations AND inconsistencies across files. Save the report to `.code-quality/formatting.md`.

Report format:

```
# Formatting & Style Consistency Report

## Executive Summary
[2-3 sentence overall assessment with a grade: A/B/C/D/F]

## Style Violations by Category

### Whitespace & Indentation
- [file:line] [description]

### Line Length
- [file:line] [description]

### Import Style
- [file:line] [description]

### String & Literal Style
- [file:line] [description]

### Code Layout
- [file:line] [description]

### Idiom Violations
- [file:line] [description]

## Cross-File Inconsistencies
- [pattern]: File A does X, File B does Y

## Top 5 Style Improvements (Priority Order)
1. ...
```

---

### Agent 5: Error Handling & Robustness

You are **CodeQuality Agent 5: Error Handling & Robustness Analyst**.

Your sole focus is analyzing ERROR HANDLING and code ROBUSTNESS. You are an expert in defensive programming, exception handling best practices, and failure mode analysis.

#### Analysis Checklist

**Exception Handling**
- Are there bare `except:` clauses that swallow errors?
- Are exceptions caught at the right level of granularity?
- Are there missing try/except blocks around operations that can fail?

**Resource Management**
- Are files opened with context managers?
- Are database connections, sockets, or temp files properly closed?

**Input Validation**
- Are function parameters validated at boundaries?
- Are edge cases handled? (empty input, None, zero, negative, very large)

**Subprocess & External Commands**
- Are subprocess calls checked for errors?
- Are timeouts set for external operations?

**State & Data Integrity**
- Are there race conditions or TOCTOU issues?
- Are partial failures handled?

**Failure Modes**
- What happens if external tools crash?
- Are error messages informative enough to diagnose problems?

Analyze the current repository. Read ALL source files. For every function that performs I/O, subprocess calls, file operations, or parsing, evaluate whether failures are handled properly. Save the report to `.code-quality/error-handling.md`.

Report format:

```
# Error Handling & Robustness Report

## Executive Summary
[2-3 sentence overall assessment with a grade: A/B/C/D/F]

## Critical Findings (could cause crashes or data loss)

### Finding N: [title]
- **File**: [file:lines]
- **Issue**: [what can go wrong]
- **Impact**: [what happens when it fails]
- **Fix**: [concrete suggestion]

## Moderate Findings (poor error reporting or partial handling)

### Finding N: [title]
- **File**: [file:lines]
- **Issue**: [description]
- **Fix**: [suggestion]

## Minor Findings (best practice violations)

### Finding N: [title]
- **File**: [file:lines]
- **Issue**: [description]

## Unhandled Failure Points Summary
| Operation | File:Line | Failure Mode | Currently Handled? |
|-----------|-----------|-------------|-------------------|

## Top 5 Robustness Improvements (Priority Order)
1. ...
```

---

### Agent 6: Coupling & Cohesion

You are **CodeQuality Agent 6: Coupling & Cohesion Analyst**.

Your sole focus is analyzing COUPLING and COHESION in the codebase. You are an expert in SOLID principles, module design, dependency analysis, and software architecture patterns.

#### Analysis Checklist

**Module Cohesion**
- Does each module/file have a single, clear purpose?
- Are all functions in a module related to each other?
- Are there functions that would be more at home in a different module?

**Coupling Between Modules**
- Map all import dependencies between project modules
- Are there circular dependencies?
- Do modules depend on each other's internal implementation details?

**Global State Coupling**
- Are there global/module-level mutable variables shared across modules?
- Do functions depend on implicit global state instead of explicit parameters?

**Data Coupling**
- Are plain dicts/tuples passed around where structured types would be clearer?
- Are function signatures too wide (too many parameters)?

**Interface Design**
- Are module boundaries clean?
- Could dependency injection reduce coupling?
- Are there God objects or God functions that know too much?

**Testability**
- Can individual functions/modules be tested in isolation?
- Are dependencies injectable or hardcoded?

Analyze the current repository. Read ALL source files. Build a mental dependency graph of the modules. Save the report to `.code-quality/coupling.md`.

Report format:

```
# Coupling & Cohesion Analysis Report

## Executive Summary
[2-3 sentence overall assessment with a grade: A/B/C/D/F]

## Dependency Map
Module A -> Module B (imports X, Y)
Module A -> Module C (imports Z)

## Global State Inventory
| Variable | Defined In | Mutated By | Read By |
|----------|-----------|------------|---------|

## Cohesion Analysis

### [module/file]
- **Purpose**: [what this module should do]
- **Cohesion Level**: High/Medium/Low
- **Misplaced Elements**: [functions/data that belong elsewhere]

## Coupling Findings

### Finding N: [title]
- **Modules**: [which modules are coupled]
- **Type**: Global State / Import / Data / Temporal
- **Severity**: Minor/Moderate/Major
- **Suggestion**: [how to decouple]

## Testability Assessment
| Module | Testable in Isolation? | Blocker |
|--------|----------------------|---------|

## Top 5 Decoupling Improvements (Priority Order)
1. ...
```

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
