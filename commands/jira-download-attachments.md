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

Set the output directory from `$2`, or default to `/tmp/<issue-key>`. The Python script in step 5 creates it.

### 2. Extract the cloud ID from acli config

```bash
CLOUD_ID=$(yq '.profiles[0].cloud_id' ~/.config/acli/global_auth_config.yaml)
```

### 3. Refresh the OAuth token

Run any lightweight acli command to force a token refresh (the keychain token has a short TTL):

```bash
acli jira workitem view <ISSUE-KEY> --fields "summary" --json
```

### 4. Extract the OAuth access token from the macOS keychain

The token is stored as a gzipped, base64-encoded JSON blob under the service name `acli`:

```bash
ACCOUNT_ID=$(yq '.profiles[0].account_id' ~/.config/acli/global_auth_config.yaml)
TOKEN_BLOB=$(security find-generic-password -s acli -a "oauth:${CLOUD_ID}:${ACCOUNT_ID}" -w)
ACCESS_TOKEN=$(echo "$TOKEN_BLOB" | sed 's|^go-keyring-base64:||' | base64 -d | gunzip | jq -r '.access_token')
```

On Linux, the keyring backend may differ. If `security` is not available, check `secret-tool` or the Go keyring file at `~/.local/share/keyrings/`.

### 5. Run the downloader

The bundled script fetches the issue JSON, resolves each attachment's 303 redirect to its signed media URL, downloads every file, and extracts any `.zip` archives into sibling subdirectories. It prints per-file progress and a final summary.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/commands/jira-download-attachments.py" \
  --issue-key <ISSUE-KEY> \
  --cloud-id "$CLOUD_ID" \
  --token "$ACCESS_TOKEN" \
  --output-dir <output-dir>
```

If the script prints `No attachments or inline media found.`, stop and tell the user the ticket has nothing to download.
