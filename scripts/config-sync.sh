#!/usr/bin/env bash
# config-sync: Sync project config files to/from a single GitHub gist.
#
# Tracked files: .claude/CLAUDE.md, .vscode/settings.json, .vscode/launch.json
# Gist naming:   "<project> config-sync"
# Gist filenames: <project>+<path> with + as dir separator (e.g. zlib-ng+.claude+CLAUDE.md)
# Sync rule:     whichever side was modified more recently wins.

set -euo pipefail

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
PROJECT_NAME=$(basename "$PROJECT_ROOT")
GIST_DESC="${PROJECT_NAME} config-sync"

# Tracked file paths (relative to project root)
LOCAL_PATHS=(".claude/CLAUDE.md" ".vscode/settings.json" ".vscode/launch.json")

# Convert a local path to a gist-safe filename using + as directory separator.
# Preserves leading dots and original filenames.
# .claude/CLAUDE.md     -> zlib-ng+.claude+CLAUDE.md
# .vscode/settings.json -> zlib-ng+.vscode+settings.json
gist_name_for() {
    local p="$1"
    p="${p#./}"
    p=$(echo "$p" | sed 's|/|+|g')
    echo "${PROJECT_NAME}+${p}"
}

# --- Helpers ---

file_mtime() {
    if [[ "$(uname)" == "Darwin" ]]; then
        stat -f '%m' "$1"
    else
        stat -c '%Y' "$1"
    fi
}

iso_to_epoch() {
    local ts="$1"
    if [[ "$(uname)" == "Darwin" ]]; then
        date -j -u -f '%Y-%m-%dT%H:%M:%S' "${ts%Z}" '+%s' 2>/dev/null || echo 0
    else
        date -d "$ts" '+%s' 2>/dev/null || echo 0
    fi
}

# --- Find newest local mtime ---

local_epoch=0
local_files=()
for f in "${LOCAL_PATHS[@]}"; do
    fp="$PROJECT_ROOT/$f"
    if [[ -f "$fp" ]]; then
        local_files+=("$f")
        mtime=$(file_mtime "$fp")
        (( mtime > local_epoch )) && local_epoch=$mtime
    fi
done

if (( ${#local_files[@]} == 0 )); then
    echo "No tracked config files found in $PROJECT_ROOT"
    exit 1
fi

# --- Find existing gist ---

gist_id=""
gist_line=$(gh gist list --limit 100 2>/dev/null | grep -F "$GIST_DESC" || true)
if [[ -n "$gist_line" ]]; then
    gist_id=$(echo "$gist_line" | awk '{print $1}' | head -1)
fi

# --- Determine direction ---

if [[ -z "$gist_id" ]]; then
    direction="create"
else
    updated_at=$(gh api "gists/$gist_id" --jq '.updated_at' 2>/dev/null || echo "")
    if [[ -n "$updated_at" ]]; then
        remote_epoch=$(iso_to_epoch "$updated_at")
    else
        remote_epoch=0
    fi

    if (( local_epoch > remote_epoch )); then
        direction="push"
    elif (( remote_epoch > local_epoch )); then
        direction="pull"
    else
        direction="in-sync"
    fi
fi

# --- Execute ---

case "$direction" in
    create)
        echo "Creating gist: $GIST_DESC"
        # gh gist create uses the local filename, so we must use the API
        # to control gist filenames with the project prefix.
        api_args=(-X POST -f "description=$GIST_DESC" -f "public=true")
        for f in "${local_files[@]}"; do
            gist_name=$(gist_name_for "$f")
            content=$(cat "$PROJECT_ROOT/$f")
            api_args+=(-f "files[$gist_name][content]=$content")
        done
        gist_id=$(gh api gists "${api_args[@]}" --jq '.id')
        echo "Pushed ${#local_files[@]} file(s): ${local_files[*]}"
        ;;

    push)
        echo "Local is newer — pushing to gist $gist_id"
        existing_files=$(gh gist view "$gist_id" --files)
        pushed=0
        for f in "${local_files[@]}"; do
            gist_name=$(gist_name_for "$f")
            if echo "$existing_files" | grep -qF "$gist_name"; then
                gh gist edit "$gist_id" -f "$gist_name" "$PROJECT_ROOT/$f"
            else
                # Add new file via API since gh gist edit -a uses the local filename
                content=$(cat "$PROJECT_ROOT/$f")
                gh api "gists/$gist_id" -X PATCH -f "files[$gist_name][content]=$content" --silent
            fi
            echo "  pushed $f -> $gist_name"
            pushed=$((pushed + 1))
        done
        echo "Pushed $pushed file(s)"
        ;;

    pull)
        echo "Remote is newer — pulling from gist $gist_id"
        gist_json=$(gh api "gists/$gist_id")
        pulled=0
        for f in "${LOCAL_PATHS[@]}"; do
            gist_name=$(gist_name_for "$f")
            content=$(echo "$gist_json" | jq -r --arg name "$gist_name" '.files[$name].content // empty')
            if [[ -n "$content" ]]; then
                target="$PROJECT_ROOT/$f"
                mkdir -p "$(dirname "$target")"
                printf '%s\n' "$content" > "$target"
                echo "  pulled $gist_name -> $f"
                pulled=$((pulled + 1))
            fi
        done
        echo "Pulled $pulled file(s)"
        ;;

    in-sync)
        echo "Already in sync."
        ;;
esac

echo "Gist: https://gist.github.com/$gist_id"
