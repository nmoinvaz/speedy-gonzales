---
name: gist-config-sync
description: Sync project config files (.claude/CLAUDE.md, .vscode/settings.json, .vscode/launch.json) to/from a GitHub gist
allowed-tools: Bash, Read, Grep
---

Before syncing, scan each file for passwords, API keys, tokens, or
other secrets. If any are found, show them and ask before proceeding.

If the user asks to sync their personal claude directory, run:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/config-sync.sh" --name claude-personal --root ~ .claude/CLAUDE.md .claude/statusline.sh
```

After a pull, run `chmod +x ~/.claude/statusline.sh`.

Otherwise sync the current project:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/config-sync.sh"
```
