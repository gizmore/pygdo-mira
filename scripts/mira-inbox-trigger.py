#!/usr/bin/env python3
"""Safely send one fixed $inbox command to the MIRA terminal."""

import os
import subprocess
import sys
import time
from pathlib import Path

from Xlib import X, display
from Xlib.ext import xtest


QUEUE = Path(os.environ.get("MIRA_MAIL_QUEUE", "/home/mira/inbound/queue")).resolve()
WINDOW_TITLE = os.environ.get("MIRA_WINDOW_TITLE", "MIRA")
XK_RETURN = 0xFF0D
XK_SHIFT = 0xFFE1


def keypress(dpy, focus, char):
    if char == "\n":
        keycodes = list(dpy.keysym_to_keycodes(XK_RETURN))
    else:
        keycodes = list(dpy.keysym_to_keycodes(ord(char)))
    if not keycodes:
        raise RuntimeError(f"no X keycode for {char!r}")
    keycode, offset = keycodes[0]
    if offset & 1:
        shift = list(dpy.keysym_to_keycodes(XK_SHIFT))[0][0]
        xtest.fake_input(focus, X.KeyPress, shift)
    xtest.fake_input(focus, X.KeyPress, keycode)
    xtest.fake_input(focus, X.KeyRelease, keycode)
    if offset & 1:
        xtest.fake_input(focus, X.KeyRelease, shift)


def send(command):
    dpy = display.Display()
    focus = dpy.get_input_focus().focus
    for char in command:
        keypress(dpy, focus, char)
    dpy.sync()


def enter():
    dpy = display.Display()
    focus = dpy.get_input_focus().focus
    keypress(dpy, focus, "\n")
    dpy.sync()


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} QUEUED_MESSAGE.eml")
    message = Path(sys.argv[1]).resolve()
    if message.parent != QUEUE or message.suffix != ".eml" or not message.is_file():
        raise SystemExit("refusing a message outside Mira's inbound queue")
    windows = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, check=False)
    if not any(WINDOW_TITLE in line for line in windows.stdout.splitlines()):
        raise SystemExit(f"{WINDOW_TITLE} window not found")
    if subprocess.run(["wmctrl", "-a", WINDOW_TITLE], check=False).returncode != 0:
        raise SystemExit(f"could not activate {WINDOW_TITLE} window")
    time.sleep(0.4)
    send(f"$inbox {message}")
    time.sleep(0.35)
    enter()


if __name__ == "__main__":
    main()
