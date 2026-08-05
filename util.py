"""Small local delivery helpers for Mira's tmux terminal."""

from __future__ import annotations

import os
import subprocess
import time


DEFAULT_MIRA_TMUX_TARGET = 'mira-codex:0.0'


def send_to_mira(text: str, *, submit: bool = True, target: str | None = None) -> None:
    """Send literal text to the tmux pane inside Mira's visible terminal.

    ``submit`` uses the Codex editor's reliable submission sequence: two
    trailing spaces followed by two physical Return key events. Set it to
    ``False`` when a caller only wants to prefill the editor.
    """
    if not isinstance(text, str) or not text:
        raise ValueError('Mira tmux text must be a non-empty string')
    if '\0' in text:
        raise ValueError('Mira tmux text must not contain NUL bytes')

    tmux_target = target or os.environ.get('MIRA_TMUX_TARGET', DEFAULT_MIRA_TMUX_TARGET)
    payload = text + ('  ' if submit else '')
    subprocess.run(['tmux', 'send-keys', '-t', tmux_target, '-l', '--', payload], check=True)

    if submit:
        time.sleep(0.1)
        subprocess.run(['tmux', 'send-keys', '-t', tmux_target, 'Enter'], check=True)
        time.sleep(0.1)
        subprocess.run(['tmux', 'send-keys', '-t', tmux_target, 'Enter'], check=True)
