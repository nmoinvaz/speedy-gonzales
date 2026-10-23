#!/usr/bin/env bash
# SessionStart hook that installs the gh-arriba extension the GitHub commands call.
# Stdout becomes Claude's context, so the script stays silent unless the extension is still missing.

# Without gh there is nothing to install into, and the GitHub commands can't run anyway.
command -v gh >/dev/null 2>&1 || exit 0

installed() {
  gh extension list 2>/dev/null | awk '$1 == "gh" && $2 == "arriba" { found = 1 } END { exit !found }'
}

installed && exit 0

if ! gh extension install nmoinvaz/gh-arriba >/dev/null 2>&1 || ! installed; then
  echo "The gh-arriba GitHub CLI extension is missing and could not be installed. If the user runs" \
    "a GitHub command from the arriba plugin, tell them to run: gh extension install nmoinvaz/gh-arriba"
fi
exit 0
