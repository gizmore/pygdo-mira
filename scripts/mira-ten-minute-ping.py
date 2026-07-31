#!/usr/bin/env python3
"""Send a scheduled Mira reminder through the MIRA tmux pane."""

import os
import subprocess
import time


TMUX_TARGET = os.environ.get("MIRA_TMUX_TARGET", "mira-codex:0.0")
DEFAULT_MESSAGE = "Your ten minute ping. Do $cc or $routine  "
MESSAGE = os.environ.get("MIRA_MESSAGE", DEFAULT_MESSAGE)


def tmux(*args: str) -> None:
    subprocess.run(["tmux", *args], check=True)


def ensure_target() -> None:
    tmux("has-session", "-t", TMUX_TARGET)


def send_text() -> None:
    tmux("send-keys", "-t", TMUX_TARGET, "-l", "--", MESSAGE)


def submit() -> None:
    # Codex uses a multiline editor. Two physical Return events submit after
    # the Markdown hard-break spaces instead of adding a line break.
    tmux("send-keys", "-t", TMUX_TARGET, "Enter")
    time.sleep(0.1)
    tmux("send-keys", "-t", TMUX_TARGET, "Enter")


def main() -> None:
    if "\n" in MESSAGE or "\r" in MESSAGE:
        raise ValueError("MIRA_MESSAGE must be a single line")
    ensure_target()
    send_text()
    time.sleep(0.1)
    submit()


if __name__ == "__main__":
    main()
