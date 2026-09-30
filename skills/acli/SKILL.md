---
name: acli
description: Common Atlassian CLI (acli) commands for Jira operations
allowed-tools: Bash(acli --version)
---

# Atlassian CLI (acli) Quick Reference

Common `acli` commands for Jira operations used across this project's workflows.

## Prerequisites

- `acli` must be installed and authenticated: `acli jira auth login --web`
- Check auth status: `acli jira auth status`

Installed version:

!`acli --version || true`

If the output above says the version is outdated, tell the user before running any other command.

## Key Flag for Subcommands

The `view` command accepts the issue key as a positional argument, but subcommands like `comment list`, `comment create`, `transition`, `edit`, etc. require the `--key` flag:

```bash
acli jira workitem view PROJ-123                          # positional OK
acli jira workitem comment list --key PROJ-123            # --key required
acli jira workitem comment create --key PROJ-123 --body-file comment.json  # --key required
```

## Always Use ADF

Always write comment bodies and issue descriptions in Atlassian Document Format (ADF). Plain text loses all formatting, and markdown or wiki markup renders as literal characters.

Write the ADF to a JSON file and pass the file path, since inline JSON breaks easily under shell quoting. See [ADF Formatting](#adf-formatting) for the node structure.

## View Issue Details

```bash
acli jira workitem view PROJ-123
```

With all fields (description, comments, etc.):

```bash
acli jira workitem view PROJ-123 --fields "*all"
```

JSON output for parsing:

```bash
acli jira workitem view PROJ-123 --json
```

Specific fields only:

```bash
acli jira workitem view PROJ-123 --fields "summary,status,priority,description,comment"
```

## Search Issues with JQL

```bash
acli jira workitem search --jql 'summary ~ "CVE-2024-1234" AND summary ~ "repo-name"' --json
```

Search by text across all fields:

```bash
acli jira workitem search --jql 'text ~ "search terms" AND key != PROJ-123' --json
```

Search by component:

```bash
acli jira workitem search --jql 'component = "my-component" AND key != PROJ-123' --json
```

Search recently resolved issues:

```bash
acli jira workitem search --jql 'text ~ "search terms" AND status in (Resolved, Done, Closed) AND resolved >= -30d' --json
```

Limit results and select fields:

```bash
acli jira workitem search --jql 'project = PROJ' --fields "key,summary,status" --limit 20 --json
```

## Add Comment to Issue

Write the comment as an ADF document in `comment.json`:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Comment text here"}]
    }
  ]
}
```

Then post it:

```bash
acli jira workitem comment create --key PROJ-123 --body-file comment.json
```

Update an existing comment with `--body-adf`, since `comment update --body-file` only takes plain text:

```bash
acli jira workitem comment update --key PROJ-123 --id 10001 --body-adf comment.json
```

## List Comments on Issue

```bash
acli jira workitem comment list --key PROJ-123 --json
```

Use `view` to see the raw ADF, since `comment list` flattens bodies to plain text and drops list items:

```bash
acli jira workitem view PROJ-123 --fields "comment" --json
```

## Transition Issue Status

First check available transitions:

```bash
acli jira workitem view PROJ-123 --fields "status" --json
```

Then transition:

```bash
acli jira workitem transition --key PROJ-123 --status "Done"
acli jira workitem transition --key PROJ-123 --status "In Progress"
acli jira workitem transition --key PROJ-123 --status "Resolved"
```

## Create Issue

Write the issue definition in `workitem.json` with an ADF `description`. The `assignee` and `labels` fields are optional.

```json
{
  "projectKey": "PROJ",
  "type": "Bug",
  "summary": "Bug title",
  "assignee": "user@example.com",
  "labels": ["bug", "triage"],
  "description": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [{"type": "text", "text": "Description"}]
      }
    ]
  }
}
```

Then create it:

```bash
acli jira workitem create --from-json workitem.json
```

## Edit Issue

```bash
acli jira workitem edit --key PROJ-123 --summary "Updated summary"
acli jira workitem edit --key PROJ-123 --assignee "@me"
```

## ADF Formatting

ADF is the JSON format Jira uses for rich text with headings, code blocks, lists, etc. The root is always a `doc` node with `"version": 1`.

Generate a sample JSON template:

```bash
acli jira workitem create --generate-json
acli jira workitem edit --generate-json
```

### Editing with ADF

Write a JSON file with `issues` and `description` fields:

```json
{
  "issues": ["PROJ-123"],
  "description": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "heading",
        "attrs": {"level": 2},
        "content": [{"type": "text", "text": "Section Title"}]
      },
      {
        "type": "paragraph",
        "content": [
          {"type": "text", "text": "Normal text and "},
          {"type": "text", "text": "inline code", "marks": [{"type": "code"}]},
          {"type": "text", "text": " in a paragraph."}
        ]
      },
      {
        "type": "codeBlock",
        "attrs": {"language": "json"},
        "content": [{"type": "text", "text": "{\"key\": \"value\"}"}]
      },
      {
        "type": "bulletList",
        "content": [
          {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Bullet item"}]}]}
        ]
      },
      {
        "type": "orderedList",
        "content": [
          {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Numbered item"}]}]}
        ]
      }
    ]
  }
}
```

Then apply:

```bash
acli jira workitem edit --from-json workitem.json --yes
```

### ADF Node Reference

| Node | Usage |
|---|---|
| `heading` | `attrs.level`: 1-6 |
| `paragraph` | Container for text nodes |
| `codeBlock` | `attrs.language`: json, bash, etc. |
| `bulletList` | Contains `listItem` nodes |
| `orderedList` | Contains `listItem` nodes |
| `text` | `marks`: `code`, `strong`, `em`, `link` |

### Known Limitations

- Markdown and wiki markup are never rendered, they appear as literal text
- `comment update` accepts ADF only through `--body-adf`, its `--body-file` flag is plain text

## List Projects

```bash
acli jira project list
```
