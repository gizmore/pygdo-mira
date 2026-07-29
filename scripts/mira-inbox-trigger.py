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


def keypress(dpy, char):
    if char == "\n":
        keycodes = list(dpy.keysym_to_keycodes(XK_RETURN))
    else:
        keycodes = list(dpy.keysym_to_keycodes(ord(char)))
    if not keycodes:
        raise RuntimeError(f"no X keycode for {char!r}")
    keycode, offset = keycodes[0]
    if offset & 1:
        shift = list(dpy.keysym_to_keycodes(XK_SHIFT))[0][0]
        xtest.fake_input(dpy, X.KeyPress, shift)
    xtest.fake_input(dpy, X.KeyPress, keycode)
    xtest.fake_input(dpy, X.KeyRelease, keycode)
    if offset & 1:
        xtest.fake_input(dpy, X.KeyRelease, shift)


def focus_window(window_id):
    dpy = display.Display()
    window = dpy.create_resource_object("window", window_id)
    dpy.set_input_focus(window, X.RevertToParent, X.CurrentTime)
    dpy.sync()
    return dpy


def send(window_id, command):
    dpy = focus_window(window_id)
    for char in command:
        keypress(dpy, char)
    dpy.sync()


def enter(window_id):
    dpy = focus_window(window_id)
    keypress(dpy, "\n")
    dpy.sync()


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} QUEUED_MESSAGE.eml")
    message = Path(sys.argv[1]).resolve()
    if message.parent != QUEUE or message.suffix != ".eml" or not message.is_file():
        raise SystemExit("refusing a message outside Mira's inbound queue")
    windows = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, check=False)
    window_id = next(
        (int(line.split(None, 1)[0], 16) for line in windows.stdout.splitlines()
         if WINDOW_TITLE in line),
        None,
    )
    if window_id is None:
        raise SystemExit(f"{WINDOW_TITLE} window not found")
    window_hex = f"0x{window_id:x}"
    if subprocess.run(["wmctrl", "-i", "-a", window_hex], check=False).returncode != 0:
        raise SystemExit(f"could not activate {WINDOW_TITLE} window")
    time.sleep(0.08)
    send(window_id, f"$inbox {message}")
    time.sleep(0.08)
    enter(window_id)


if __name__ == "__main__":
    main()
