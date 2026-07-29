#!/usr/bin/env python3
"""Select one explicitly ready Mira task for the scheduled MIRA wake-up."""

import argparse
import re
from pathlib import Path


TODO = Path("/home/mira/.pygdo/TODO.md")
READY = re.compile(r"^- \[ready\] (.+)$")


def next_ready_task(todo: Path) -> str | None:
    in_next = False
    for line in todo.read_text(encoding="utf-8").splitlines():
        if line == "## Next":
            in_next = True
            continue
        if in_next and line.startswith("## "):
            break
        if in_next and (match := READY.match(line)):
            return match.group(1)
    return None


def work_packet(task: str) -> str:
    return f"Work packet: {task} Work one bounded safe slice, verify it, then update TODO or report the blocker.  "


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--todo", type=Path, default=TODO)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--next", action="store_true", help="print one scheduled work packet")
    args = parser.parse_args()

    if not args.todo.is_file():
        raise SystemExit(f"missing TODO file: {args.todo}")
    task = next_ready_task(args.todo)
    if args.check:
        print(f"ready task: {task}" if task else "ready task: none")
    if args.next and task:
        print(work_packet(task))


if __name__ == "__main__":
    main()
