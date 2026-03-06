---
name: acli
description: Common Atlassian CLI (acli) commands for Jira operations
---

# Atlassian CLI (acli) Quick Reference

Common `acli` commands for Jira operations used across this project's workflows.

## Prerequisites

- `acli` must be installed and authenticated: `acli jira auth login --web`
- Check auth status: `acli jira auth status`

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

```bash
acli jira workitem comment create --key PROJ-123 --body "Comment text here"
```

Multi-line comment from a file:

```bash
acli jira workitem comment create --key PROJ-123 --body-file comment.txt
```

## List Comments on Issue

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

```bash
acli jira workitem create --project PROJ --type Bug --summary "Bug title" --description "Description"
```

With assignee and labels:

```bash
acli jira workitem create --project PROJ --type Task --summary "Title" \
  --assignee "user@example.com" --label "bug,triage"
```

## Edit Issue

```bash
acli jira workitem edit --key PROJ-123 --summary "Updated summary"
acli jira workitem edit --key PROJ-123 --assignee "@me"
```

## ADF Formatting (Rich Text Descriptions)

The `--description` and `--description-file` flags only accept plain text. To set a rich-text description with headings, code blocks, lists, etc., use `--from-json` with Atlassian Document Format (ADF).

Generate a sample JSON template:

```bash
acli jira workitem create --generate-json
acli jira workitem edit --generate-json
```

### Creating with ADF

Write a JSON file with the ADF `description` field, then use `--from-json`:

```bash
acli jira workitem create --from-json workitem.json
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

- `--description` and `--description-file` do NOT render wiki markup or markdown — they produce plain text only
- Comment creation (`comment create`) does not support ADF; comment update does via `--body-adf`

## List Projects

```bash
acli jira project list
```
