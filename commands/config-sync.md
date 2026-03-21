---
name: config-sync
description: Sync project config files (.claude/CLAUDE.md, .vscode/settings.json, .vscode/launch.json) to/from a GitHub gist
allowed-tools: Bash
---

Run the config-sync script and report what it did:

```bash
bash "$SPEEDY_GONZALES_DIR/scripts/config-sync.sh"
```

If the script is not found at that path, look for it relative to the
plugin root at `~/Source/speedy-gonzales/scripts/config-sync.sh`.
