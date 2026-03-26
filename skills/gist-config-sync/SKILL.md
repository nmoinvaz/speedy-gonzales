---
name: gist-config-sync
description: Sync project config files to/from a GitHub gist
---

Before pushing, scan each file for passwords, API keys, tokens, or
other secrets. If any are found, show them and ask before proceeding.

The script reads its file list from the YAML manifest in the gist
when no files are given as arguments. Pass files only when creating
a new gist or changing the tracked set.

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

If the visibility is "PRIVATE", pass `--private`. Pass any
user-provided files as arguments, or omit them to use the manifest:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/config-sync.sh" \
  [--private] \
  [files...]
```
