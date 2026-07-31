#!/usr/bin/env python3
"""Safely send one fixed $inbox command through the MIRA tmux pane."""

import os
import subprocess
import sys
import time
from pathlib import Path


QUEUE = Path(os.environ.get("MIRA_MAIL_QUEUE", "/home/mira/inbound/queue")).resolve()
TMUX_TARGET = os.environ.get("MIRA_TMUX_TARGET", "mira-codex:0.0")


def tmux(*args: str) -> None:
    subprocess.run(["tmux", *args], check=True)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} QUEUED_MESSAGE.eml")

    message = Path(sys.argv[1]).resolve()
    if message.parent != QUEUE or message.suffix != ".eml" or not message.is_file():
        raise SystemExit("refusing a message outside Mira's inbound queue")

    tmux("has-session", "-t", TMUX_TARGET)
    # The hard-break spaces and separate Return events match the Codex editor's
    # reliable submission sequence without stealing focus from another window.
    tmux("send-keys", "-t", TMUX_TARGET, "-l", "--", f"$inbox {message}  ")
    time.sleep(0.1)
    tmux("send-keys", "-t", TMUX_TARGET, "Enter")
    time.sleep(0.1)
    tmux("send-keys", "-t", TMUX_TARGET, "Enter")


if __name__ == "__main__":
    main()
