#!/usr/bin/env bash
set -u

usage() {
    printf 'Usage: %s --dir <directory> [--dir <directory> ...] [--fix --owner gizmore|mira]\n' "$(basename -- "$0")" >&2
}

fix=0
owner=''
directories=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir)
            [[ $# -ge 2 ]] || { usage; exit 2; }
            directories+=("$(realpath -- "$2")")
            shift 2
            ;;
        --fix)
            fix=1
            shift
            ;;
        --owner)
            [[ $# -ge 2 ]] || { usage; exit 2; }
            owner="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage
            exit 2
            ;;
    esac
done

if [[ ${#directories[@]} -eq 0 ]] || { (( fix )) && [[ "$owner" != gizmore && "$owner" != mira ]]; }; then
    usage
    exit 2
fi
for directory in "${directories[@]}"; do
    [[ -d "$directory" ]] || { printf 'Not a directory: %s\n' "$directory" >&2; exit 2; }
done

violations=0
checked=0
while IFS=$'\t' read -r -d '' kind user group mode path; do
    checked=$((checked + 1))
    if [[ "$kind" == d ]]; then
        expected=770
    else
        mode_num=$((8#$mode))
        if (( mode_num & 0111 )); then
            expected=770
        else
            expected=660
        fi
    fi

    if [[ ("$user" != gizmore && "$user" != mira) || "$group" != gizmore || "$mode" != "$expected" ]]; then
        violations=$((violations + 1))
        printf 'MISMATCH user=%s group=%s mode=%s expected=%s:%s %s\n' \
            "$user" "$group" "$mode" "${owner:-gizmore}" gizmore "$path"
        if (( fix )); then
            chown "${owner}:gizmore" -- "$path" || continue
            chmod "$expected" -- "$path" || continue
            printf 'FIXED %s\n' "$path"
        fi
    fi
done < <(
    for directory in "${directories[@]}"; do
        find -P "$directory" \( -type d -o -type f \) \
            -printf '%y\t%u\t%g\t%m\t%p\0'
    done
)

printf 'Checked %d paths; %d permission mismatches%s\n' \
    "$checked" "$violations" "$([[ $fix -eq 1 ]] && printf ' (fix attempted)' || true)"
(( violations == 0 ))
