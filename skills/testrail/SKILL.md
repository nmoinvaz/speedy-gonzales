---
name: testrail
description: Interact with TestRail through the testrail-arriba CLI. Use when fetching test plans, test runs, test cases, submitting test results, or attaching screenshots and logs to test evidence. Supports the full execution lifecycle from locating tests to recording step-by-step outcomes.
allowed-tools: Bash(testrail-arriba --version), Bash(testrail-arriba auth status)
---

# TestRail with testrail-arriba

[testrail-arriba](https://github.com/arriba-tools/testrail) is the CLI this project's TestRail
workflows use. It takes step outcomes in Markdown, uploads the screenshots they name to the run, and
sends the HTML TestRail renders, so step results are never written as HTML by hand.

## Prerequisites

Installed version and login:

!`testrail-arriba --version 2>&1 || echo "testrail-arriba is not installed"`

!`testrail-arriba auth status 2>&1 || true`

If it is not installed, tell the user to download it from the
[releases](https://github.com/arriba-tools/testrail/releases) and put it on the `PATH`, or run
`cargo install --git https://github.com/arriba-tools/testrail`, and stop.

If there is no login, tell the user to run `testrail-arriba auth login`, which stores the API key in
the keyring, and stop. `TESTRAIL_URL`, `TESTRAIL_EMAIL`, and `TESTRAIL_API_KEY` in the environment
work without a stored login, and `TESTRAIL_PASSWORD` is accepted in place of the key.

The QA credentials are in 1Password, item **"TestRail"** in the **SSN - QA** vault. Pipe the key
to `auth login --site <site> --email <email> --token` to store it without a prompt.

## Conventions

- Every ID takes TestRail's prefixed form, such as `C39`, `R201`, or `T1001`, or the page's URL.
- `--project` (`-p`) takes the project's ID or name, as in `-p Solsta` or `-p 2`.
- Add `--json` to any command whose output you need to parse.
- Lists stop at 50 unless `--limit` or `--all` says otherwise, and say so on stderr when more remain.
- `attachment delete` asks before acting, `--yes` skips the prompt.
- Pass `--site acme.testrail.io` when several logins are stored.

## How TestRail Fits Together

```
Project                              -p takes its ID or name
├── Suite → Section → Case (C39)     the test and its steps: case view
├── Milestone
├── Plan → Run (R201)                a plan's runs: run list --plan
└── Run (R201)                       runs outside plans: run list -p
      └── Test (T1001)               one case in either kind of run: test view
            └── Result               added with result add, never edited
```

A case becomes a test when a run includes it, and each result added to a test joins its history.

## Find a Plan and What Is Left to Test

```bash
testrail-arriba plan list -p Solsta --active --name "2.1"
testrail-arriba plan view 15                 # entries with every run
testrail-arriba run list --plan 15
testrail-arriba test list R201 --status untested,retest
testrail-arriba test list --plan 15 --case C52   # one case on each platform in a plan
```

## Browse the Case Library

```bash
testrail-arriba section list -p Solsta --tree
testrail-arriba case list -p Solsta --section 31
testrail-arriba case list -p Solsta --ref PROJ-123   # cases behind a Jira issue
testrail-arriba case list -p Solsta --grep sso       # a word anywhere in a case's text
testrail-arriba case view C39
```

`--suite` is needed only when the project has several suites. `milestone list`, `suite list`, and
`project list --active` cover the rest.

## Execute a Test

```bash
# 1. Read the steps, the run's configuration, and the latest results.
testrail-arriba test view T1001

# 2. Run the steps, saving a screenshot per step.

# 3. Write the outcomes to steps.json, then check what would be sent.
testrail-arriba result add --test T1001 -s failed --steps steps.json --dry-run

# 4. Add the result once.
testrail-arriba result add --test T1001 -s failed -e "4m" --version 2.1.0 \
    --comment "Fails at step 2." --steps steps.json --attach console.log
```

`--run R201 --case C39` works in place of `--test`. `--comment-file` reads a longer comment,
`--defect` links issues, and `--field NAME=VALUE` sets custom result fields.

### Steps file

A JSON array with one object per step, in the case's order. Text is Markdown, and image paths
resolve against the file's folder.

```json
[
  {"status": "passed", "actual": "The page loaded with both fields.\n\n![](shots/step1.png)"},
  {"status": "failed", "actual": "Nothing happened after **Submit**.\n\n![](shots/step2.png)"}
]
```

| Field | Sent as |
|-------|---------|
| `content` | HTML paragraphs, or the case's step when left out |
| `expected` | HTML in a `<blockquote>`, or the case's expected result when left out |
| `actual` | HTML paragraphs, with images lifted out after them as `<img>` tags |
| `status` or `status_id` | A status name, as `status list` shows them, or its ID |

Each image is uploaded to the run once, however often it appears, and its ID is written into the
`<img>` tag. `--step-image 2=shot.png` adds a screenshot to a step without editing the file. Text
that already starts with an HTML tag is sent as it is, and `--raw` sends every field as given.

## Results and Attachments

```bash
testrail-arriba result list --test T1001
testrail-arriba result list --run R201 --case C39
testrail-arriba attachment add shots/*.png --run R201    # prints each ID and its inline src
testrail-arriba attachment list --test T1001
testrail-arriba attachment download --run R201 -o ./R201
testrail-arriba status list                              # names and IDs, custom ones included
```

Downloads go to a `testrail-arriba` folder in the temp directory unless `-o` names one, and each
file name starts with its attachment ID.

## Raw API Calls

For an endpoint testrail-arriba has no command for, `api` reuses its login:

```bash
testrail-arriba api get_case_fields
testrail-arriba api "get_cases/2&suite_id=1"
```

`-d` posts a JSON body, from the argument, `@FILE`, or `-` for stdin.

## Gotchas

1. **Results cannot be edited.** TestRail has no update result API, so a second `result add` adds
   another result to the history. Run with `--dry-run` first.
2. **Runs in plans are hidden** from `run list -p`. Use `run list --plan` or `plan view`.
3. **There is no start test API.** Read the steps, execute them, then add a result. A `retest`
   status works as an in-progress marker.
4. **Inline images need the run.** `result add` uploads them there itself. When writing HTML by hand
   with `--raw`, attach to the run first with `attachment add --run` and use the printed `src`.
5. **HTML renders only inside `<p>` tags.** Without them TestRail escapes the HTML and ignores
   Markdown image syntax, which is why `--raw` text must carry its own `<p>` tags.
