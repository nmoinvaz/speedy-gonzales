---
name: testrail
description: Interact with the TestRail Test Management API. Use when fetching test plans, test runs, test cases, submitting test results, or attaching screenshots and logs to test evidence. Supports the full execution lifecycle from locating tests to recording step-by-step outcomes.
---

# TestRail Test Management

## Authentication

**Env vars** (required by all scripts):
```
TESTRAIL_URL=https://[account].testrail.io
TESTRAIL_EMAIL=testrail@company.com
TESTRAIL_PASSWORD=<api_key>
```

Credentials stored in 1Password: **"TestRail"** in **SSN - QA** vault.

**Install:** `pip3 install testrail-api`

---

## Object Hierarchy

```
Project (e.g. Solsta = ID 2)
  └── Suite (test case library)
        └── Section (folder within a suite)
              └── Case (reusable test case template with steps)

  └── Milestone (release/sprint marker)

  └── Plan (groups multiple runs together)
        └── Entry (one per suite in the plan)
              └── Run (test execution instance)
                    └── Test (live instance of a Case — auto-created)
                          └── Result (outcome you submit)
                                └── Attachment (screenshot, log)
```

**Key relationships:**
- A **Case** becomes a **Test** when included in a **Run**
- You submit **Results** to a Test (multiple results = history)
- **Runs inside a Plan** are in `entries[].runs[]` — NOT returned by `get_runs`
- **Attachments** are uploaded separately after submitting a result

**Status IDs:** 1=Passed, 2=Blocked, 3=Untested, 4=Retest, 5=Failed

---

## Scripts

All scripts in `skills/testrail/scripts/`. Run with `python3 skills/testrail/scripts/<script>.py`.

### Browsing & Discovery

| Script | Purpose | Key Flags |
|--------|---------|-----------|
| `get_projects.py` | List all projects | `--names-only`, `--active-only` |
| `get_suites.py` | List suites in a project | `--project-id`, `--names-only` |
| `get_sections.py` | List sections/folders | `--project-id`, `--suite-id`, `--tree` |
| `get_cases.py` | List test cases | `--project-id`, `--section-id`, `--with-steps`, `--limit` |
| `get_milestones.py` | List milestones | `--project-id`, `--id`, `--active-only` |
| `get_plan.py` | Find plans by name/ID or list all | `--id`, `--project-id`, `--name`, `--list`, `--active-only` |
| `get_runs.py` | Get runs inside a plan | `--plan-id`, `--names-only` |
| `get_tests.py` | Get test instances in a run | `--run-id`, `--status`, `--names-only` |
| `get_steps.py` | Get steps for a case or test | `--case-id`, `--test-id`, `--json` |

### Submitting Results

| Script | Purpose | Key Flags |
|--------|---------|-----------|
| `add_result.py` | Submit a result with optional step outcomes | `--run-id`, `--case-id`, `--status`, `--comment`, `--elapsed`, `--step-results-file` |
| `add_attachment.py` | Attach a file to a result or run | `--result-id`, `--run-id`, `--file` |
| `submit_test.py` | Submit result with step outcomes | `--run-id`, `--case-id`, `--status`, `--comment`, `--elapsed`, `--step-results-file` |

All scripts support `--json` for raw JSON output. Run any script with `--help` for full options.

---

## Common Workflows

### Find and explore a test plan

```bash
# List plans for Solsta
python3 skills/testrail/scripts/get_plan.py --project-id 2 --list --active-only

# Get full plan detail (entries + runs)
python3 skills/testrail/scripts/get_plan.py --id 15

# List runs in the plan
python3 skills/testrail/scripts/get_runs.py --plan-id 15 --names-only

# List tests in a run
python3 skills/testrail/scripts/get_tests.py --run-id 201 --names-only
```

### Execute a test case

```bash
# 1. Get the steps
python3 skills/testrail/scripts/get_steps.py --case-id 39

# 2. Execute steps (manual or automation)

# 3. Attach screenshots to the run as you go
python3 skills/testrail/scripts/add_attachment.py --run-id 201 --file /tmp/step1.png
# → attachment_id=55 (use this in step results JSON)

# 4. Submit result with inline screenshot refs in step actuals
python3 skills/testrail/scripts/submit_test.py \
    --run-id 201 --case-id 39 --status passed \
    --comment "All steps verified" --elapsed "2m 15s" \
    --step-results-file /tmp/step_results.json
```

### Submit with per-step inline screenshots (preferred)

Screenshots render **inline** in TestRail's step results view. This requires a 3-step process
because attachment IDs are only known after upload.

#### ⚠️ CRITICAL: HTML Formatting Rules for Step Results

TestRail step results (`custom_step_results`) require specific HTML formatting to render properly:

1. **Wrap text in `<p>` tags** — This triggers `markdown_editor_id: 1` which enables HTML rendering. Without `<p>` tags, all HTML is escaped and shows as raw text.
2. **Use `<blockquote>` for expected results** — Renders with a colored left border, visually distinct.
3. **Use `<img>` tags for inline images** — Place after the `<p>` block: `<img src="index.php?/attachments/get/<id>" />`
4. **Do NOT use markdown** — `![alt](url)` syntax does NOT render in step results.
5. **All three fields support HTML** — `content`, `expected`, and `actual` all render HTML when `<p>` tags are present.

#### Step results JSON format

```json
[
    {
        "content": "<p>Navigate to login page</p>",
        "expected": "<blockquote>Login page loads with username and password fields</blockquote>",
        "actual": "<p>Page loaded correctly. Username and password fields visible.</p><img src=\"index.php?/attachments/get/55\" />",
        "status_id": 1
    },
    {
        "content": "<p>Click Submit</p>",
        "expected": "<blockquote>Dialog appears confirming login</blockquote>",
        "actual": "<p>Nothing happened. No dialog appeared.</p><img src=\"index.php?/attachments/get/56\" />",
        "status_id": 5
    }
]
```

**Field breakdown:**
- `content` → Shown under **Step** heading. Wrap in `<p>` tags.
- `expected` → Shown under **Expected Result** heading. Wrap in `<blockquote>` for visual distinction.
- `actual` → Shown under **Actual Result** heading. Wrap observation in `<p>`, append `<img>` for screenshot.
- `status_id` → 1=Passed, 5=Failed, 2=Blocked, 4=Retest.

#### Inline screenshots workflow (single result, no duplicates)

```bash
# During testing: attach each screenshot to the RUN as you capture it
python3 skills/testrail/scripts/add_attachment.py --run-id 16 --file screenshots/step1.png
# → attachment_id=55
python3 skills/testrail/scripts/add_attachment.py --run-id 16 --file screenshots/step2.png
# → attachment_id=56

# After testing: submit result with HTML img refs baked into step actuals
# In your step results JSON, use <img> tags (NOT markdown):
#   "actual": "<p>Step passed.</p><img src=\"index.php?/attachments/get/55\" />"
python3 skills/testrail/scripts/submit_test.py \
    --run-id 16 --case-id 78 --status passed \
    --comment "All steps verified" --elapsed "4m 00s" \
    --step-results-file /tmp/steps_with_images.json
# → One result, inline screenshots, no duplicates
```

**Key insight:** Attaching to the **run** (`--run-id`) doesn't require a result ID,
so you get attachment IDs first, bake them into the step results, and submit once.
This avoids the duplicate result problem caused by TestRail having no "update result" API.

### Browse the test case library

```bash
# Section tree
python3 skills/testrail/scripts/get_sections.py --project-id 2 --tree

# Cases in a section
python3 skills/testrail/scripts/get_cases.py --project-id 2 --section-id 31 --with-steps

# All cases (careful — could be large)
python3 skills/testrail/scripts/get_cases.py --project-id 2 --names-only
```

---

## Gotchas

1. **Runs in plans are hidden.** `get_runs` (standalone) won't return them. Use `get_plan` → `entries[].runs[]` or the `get_runs.py --plan-id` script.
2. **No "start test" API.** Just fetch steps, execute, then submit a result. Use `status_id: 4` (Retest) as an "in progress" marker if needed.
3. **Attachments are separate.** Submit result first, get `result_id`, then attach files. Or use `submit_test.py` which does both.
4. **Step results field name** is `custom_step_results` (not `step_results`).
5. **Single-suite projects** (like Solsta) don't need `--suite-id` for most queries.
6. **No "update result" API.** You can only add new results, never modify existing ones. To avoid duplicates when adding inline screenshots, attach to the **run** first (`add_attachment.py --run-id`), then bake the attachment IDs into step results before submitting.
7. **Inline image syntax:** Use `<img src="index.php?/attachments/get/<attachment_id>" />` — NOT markdown `![alt](url)`. The attachment must exist on the same run/test. Attachment IDs are global within a project.
8. **HTML rendering requires `<p>` tags.** If you submit step results without `<p>` tags wrapping the text, TestRail escapes all HTML (shows raw `<img>` as text). Always wrap text content in `<p>` tags to trigger `markdown_editor_id: 1`.
9. **Use `<blockquote>` for expected results.** Renders with a colored left border for visual distinction from the actual result.
