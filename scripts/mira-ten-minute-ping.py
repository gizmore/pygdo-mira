#!/usr/bin/env python3
"""Send the scheduled Mira reminder to the exact visible MIRA window."""

import os
import subprocess
import time

from Xlib import X, display
from Xlib.ext import xtest


WINDOW_TITLE = os.environ.get("MIRA_WINDOW_TITLE", "MIRA")
MESSAGE = "Your ten minute ping. Do $cc or $routine "
XK_RETURN = 0xFF0D
XK_SHIFT = 0xFFE1
XK_CONTROL_L = 0xFFE3


def mira_window_id() -> int:
    windows = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, check=False)
    for line in windows.stdout.splitlines():
        parts = line.split(None, 3)
        if len(parts) == 4 and parts[3] == WINDOW_TITLE:
            return int(parts[0], 16)
    raise RuntimeError(f"{WINDOW_TITLE!r} window not found")


def keypress(dpy, char: str) -> None:
    keysym = XK_RETURN if char == "\n" else ord(char)
    keycodes = list(dpy.keysym_to_keycodes(keysym))
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


def focus_window(window_id: int):
    window_hex = f"0x{window_id:x}"
    if subprocess.run(["wmctrl", "-i", "-a", window_hex], check=False).returncode:
        raise RuntimeError(f"could not activate {WINDOW_TITLE!r} window")
    dpy = display.Display()
    window = dpy.create_resource_object("window", window_id)
    window.set_input_focus(X.RevertToParent, X.CurrentTime)
    dpy.sync()
    return dpy


def send_text(window_id: int) -> None:
    dpy = focus_window(window_id)
    for char in MESSAGE:
        keypress(dpy, char)
    dpy.sync()


def send_enter(window_id: int) -> None:
    dpy = focus_window(window_id)
    # The terminal accepts Ctrl+J as Enter more reliably than an injected
    # Return keysym. Keep this as a second, separately focused X write.
    control = list(dpy.keysym_to_keycodes(XK_CONTROL_L))[0][0]
    newline = list(dpy.keysym_to_keycodes(ord("j")))[0][0]
    xtest.fake_input(dpy, X.KeyPress, control)
    xtest.fake_input(dpy, X.KeyPress, newline)
    xtest.fake_input(dpy, X.KeyRelease, newline)
    xtest.fake_input(dpy, X.KeyRelease, control)
    dpy.sync()


def main() -> None:
    window_id = mira_window_id()
    send_text(window_id)
    time.sleep(0.3)
    send_enter(window_id)


if __name__ == "__main__":
    main()
