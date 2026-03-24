#!/usr/bin/env bash
# config-sync: Sync project config files to/from a single GitHub gist.
#
# Usage: config-sync.sh [--name NAME] [--root DIR] [--private] [FILE...]
#
# Options:
#   --name NAME   Gist name prefix (default: basename of root dir)
#   --root DIR    Root directory for relative paths (default: git root or cwd)
#   --private     Create the gist as secret instead of public
#   FILE...       Files to sync, relative to root
#
# Gist naming:   "<name> config-sync"
# Gist filenames: <name>+<path> with + as dir separator
# Sync rule:     whichever side was modified more recently wins.

set -euo pipefail

# --- Parse arguments ---

custom_name=""
custom_root=""
custom_files=()
gist_public="true"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name) custom_name="$2"; shift 2 ;;
        --root) custom_root="$2"; shift 2 ;;
        --private) gist_public="false"; shift ;;
        *) custom_files+=("$1"); shift ;;
    esac
done

PROJECT_ROOT="${custom_root:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
PROJECT_NAME="${custom_name:-$(basename "$PROJECT_ROOT")}"
GIST_DESC="${PROJECT_NAME} config-sync"

if (( ${#custom_files[@]} == 0 )); then
    echo "No files specified."
    exit 1
fi

LOCAL_PATHS=("${custom_files[@]}")

# Convert a local path to a gist-safe filename using + as directory separator.
# .claude/CLAUDE.md     -> zlib-ng+.claude+CLAUDE.md
# .vscode/settings.json -> zlib-ng+.vscode+settings.json
gist_name_for() {
    local p="$1"
    p="${p#./}"
    p=$(echo "$p" | sed 's|/|+|g')
    echo "${PROJECT_NAME}+${p}"
}

README_NAME="!${PROJECT_NAME}-config-sync.md"

# Generate the readme content listing tracked files and their gist names.
generate_readme() {
    local body="# ${PROJECT_NAME} config-sync"$'\n\n'
    body+="Configuration files synced by [config-sync](https://github.com/nmoinvaz/speedy-gonzales)."$'\n\n'
    body+="| Local path | Gist filename |"$'\n'
    body+="| --- | --- |"$'\n'
    for f in "${LOCAL_PATHS[@]}"; do
        body+="| \`$f\` | \`$(gist_name_for "$f")\` |"$'\n'
    done
    echo "$body"
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

# --- Find existing gist ---

gist_id=""
gist_line=$(gh gist list --limit 100 2>/dev/null | grep -F "$GIST_DESC" || true)
if [[ -n "$gist_line" ]]; then
    gist_id=$(echo "$gist_line" | awk '{print $1}' | head -1)
fi

if (( ${#local_files[@]} == 0 )) && [[ -z "$gist_id" ]]; then
    echo "No tracked config files found in $PROJECT_ROOT and no remote gist exists."
    exit 0
fi

# --- Determine direction ---

if [[ -z "$gist_id" ]]; then
    direction="create"
elif (( ${#local_files[@]} == 0 )); then
    direction="pull"
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
        api_args=(-X POST -f "description=$GIST_DESC" -f "public=$gist_public")
        api_args+=(-f "files[$README_NAME][content]=$(generate_readme)")
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
                content=$(cat "$PROJECT_ROOT/$f")
                gh api "gists/$gist_id" -X PATCH -f "files[$gist_name][content]=$content" --silent
            fi
            echo "  pushed $f -> $gist_name"
            pushed=$((pushed + 1))
        done
        gh api "gists/$gist_id" -X PATCH -f "files[$README_NAME][content]=$(generate_readme)" --silent
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
