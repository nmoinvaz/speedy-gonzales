---
name: jira-download-attachments
description: Download all attachments and inline media from a Jira ticket
argument-hint: "<Jira URL or issue key> [output-dir]"
allowed-tools: Bash, Read
---

Download all attachments and inline media from a Jira ticket: $ARGUMENTS

## Arguments

- `$1`: A Jira URL (e.g., `https://company.atlassian.net/browse/PROJ-123`) or a Jira issue key (e.g., `PROJ-123`).
- `$2` (optional): Output directory. Defaults to `/tmp/<issue-key>`.

## Prerequisites

Use `acli` for Jira authentication. Before any operations, load the `/arriba:acli` skill for command syntax reference and verify that `acli` is authenticated by running `acli jira auth status`. If not authenticated, tell the user to run `acli jira auth login --web` and stop.

## Steps

### 1. Parse arguments

Extract the issue key from `$1`:
- If it is a URL, extract the key from the `/browse/` path segment
- If it is already a key (e.g., `PROJ-123`), use it directly
- Validate the format matches `[A-Z][A-Z0-9]+-[0-9]+`

Set the output directory from `$2`, or default to `/tmp/<issue-key>`.

### 2. Extract the site and cloud ID from acli config

```bash
yq '.profiles[0].site' ~/.config/acli/global_auth_config.yaml
yq '.profiles[0].cloud_id' ~/.config/acli/global_auth_config.yaml
```

### 3. Refresh the OAuth token

Run any lightweight acli command to force a token refresh (the keychain token has a short TTL):

```bash
acli jira workitem view <ISSUE-KEY> --fields "summary" --json
```

### 4. Extract the OAuth access token from the macOS keychain

The token is stored as a gzipped, base64-encoded JSON blob under the service name `acli`:

```bash
CLOUD_ID=<cloud_id from step 2>
ACCOUNT_ID=$(yq '.profiles[0].account_id' ~/.config/acli/global_auth_config.yaml)
TOKEN_BLOB=$(security find-generic-password -s acli -a "oauth:${CLOUD_ID}:${ACCOUNT_ID}" -w)
ACCESS_TOKEN=$(echo "$TOKEN_BLOB" | sed 's|^go-keyring-base64:||' | base64 -d | gunzip | jq -r '.access_token')
```

On Linux, the keyring backend may differ. If `security` is not available, check `secret-tool` or the Go keyring file at `~/.local/share/keyrings/`.

### 5. Fetch the issue with rendered fields

The rendered HTML maps inline media IDs to real attachment content URLs. Fetch the issue with `expand=renderedFields`:

```bash
curl -sS \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${CLOUD_ID}/rest/api/3/issue/<ISSUE-KEY>?expand=renderedFields&fields=attachment,description,comment" \
  -o /tmp/<ISSUE-KEY>-rendered.json
```

### 6. Extract attachment IDs and filenames

Parse the rendered HTML across description and all comments to find every attachment reference. Two patterns appear in the HTML:

- **Inline images**: `<img src="...attachment/content/<ID>" alt="<filename>">`
- **File links**: `<a href="...attachment/content/<ID>" ... data-attachment-name="<filename>">`

Use python to extract them:

```python
import sys, re, json

with open(sys.argv[1]) as f:
    data = json.load(f)

rendered = data.get("renderedFields", {})
parts = []

desc = rendered.get("description") or ""
parts.append(desc)

comments = rendered.get("comment", {}).get("comments", [])
for c in comments:
    body = c.get("body", "")
    if body:
        parts.append(body)

html = "\n".join(parts)

attachments = {}

# Images with alt text
for m in re.finditer(r'attachment/content/(\d+)"[^>]*?alt="([^"]+)"', html):
    attachments[m.group(1)] = m.group(2)

# File links with data-attachment-name
for m in re.finditer(r'attachment/content/(\d+)"[^>]*?data-attachment-name="([^"]+)"', html):
    attachments[m.group(1)] = m.group(2)

# Catch any remaining attachment URLs without a parseable filename
for m in re.finditer(r'attachment/content/(\d+)', html):
    if m.group(1) not in attachments:
        attachments[m.group(1)] = f"attachment-{m.group(1)}"

for aid, name in sorted(attachments.items()):
    print(f"{aid}\t{name}")
```

If nothing is found, tell the user the ticket has no attachments or inline media.

### 7. Download each attachment

The Jira attachment content endpoint returns a 303 redirect to a signed media URL. Fetch the redirect URL first, then download from it:

```bash
mkdir -p <output-dir>

# For each attachment ID and filename:
REDIRECT_URL=$(curl -sS \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/json" \
  "https://api.atlassian.com/ex/jira/${CLOUD_ID}/rest/api/3/attachment/content/<ID>" \
  -o /dev/null -w "%{redirect_url}")

curl -sS -L -o "<output-dir>/<filename>" "$REDIRECT_URL"
```

Loop over all attachment IDs from step 6 and download each one.

### 8. Report results

List the downloaded files with sizes:

```bash
ls -lh <output-dir>/
```

Print a summary: how many files were downloaded, total size, and the output directory path.
