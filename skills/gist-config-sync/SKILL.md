---
name: gist-config-sync
description: Sync project config files to/from a GitHub gist
---

Before syncing, scan each file for passwords, API keys, tokens, or
other secrets. If any are found, show them and ask before proceeding.

If the user asks to sync their personal claude directory, run:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/config-sync.sh" \
  --name claude-personal \
  --root ~ \
  .claude/CLAUDE.md \
  .claude/settings.json \
  .claude/statusline.sh
```

After a pull, run `chmod +x ~/.claude/statusline.sh`.

Otherwise sync the current project. First determine the repository
visibility so private repos get a private gist:

```bash
repo_visibility=$(gh repo view --json visibility -q '.visibility')
```

If the visibility is "PRIVATE", pass `--private`:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/config-sync.sh" \
  --private \
  .claude/CLAUDE.md \
  .vscode/cmake-variants.yaml \
  .vscode/settings.json \
  .vscode/launch.json \
  .vscode/tasks.json
```

Otherwise omit `--private`:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/config-sync.sh" \
  .claude/CLAUDE.md \
  .vscode/cmake-variants.yaml \
  .vscode/settings.json \
  .vscode/launch.json \
  .vscode/tasks.json
```
