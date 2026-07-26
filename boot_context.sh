#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/gizmore/www"
FILTER='//github.com/gizmore/'

usage() {
    printf 'Usage: %s [--dir <directory>] [--filter <origin-substring>]\n' "$(basename -- "$0")"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            ROOT_DIR="$(realpath -- "$2")"
            shift 2
            ;;
        --filter)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            FILTER="${2##::}"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage >&2
            exit 2
            ;;
    esac
done

[[ -d "$ROOT_DIR" ]] || { printf 'Not a directory: %s\n' "$ROOT_DIR" >&2; exit 2; }

found=0
while IFS= read -r -d '' git_dir; do
    repo="${git_dir%/.git}"
    origin="$(git -C "$repo" remote get-url origin 2>/dev/null || true)"
    [[ "$origin" == *"$FILTER"* ]] || continue
    found=$((found + 1))
    branch="$(git -C "$repo" symbolic-ref --short -q HEAD 2>/dev/null || printf 'detached')"
    status='clean'
    [[ -n "$(git -C "$repo" status --porcelain --untracked-files=no 2>/dev/null)" ]] && status='modified'
    printf '%s\t%s\t%s\t%s\n' "$repo" "$branch" "$status" "$origin"
done < <(
    find "$ROOT_DIR" \
        \( -name .git \( -type d -o -type f \) -prune -print0 \) -o \
        \( -type d -name .git -prune \)
)

printf 'Found %d matching repositories.\n' "$found" >&2
