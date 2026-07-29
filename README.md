# pygdo-mira
Project-facing Mira context and helpers for the PyGDO chatbot system.

## Reboot context

The read-only `boot_context.sh` helper lists local repositories whose `origin`
contains `//github.com/gizmore/`, including branch and worktree state:

```bash
./boot_context.sh
./boot_context.sh --dir /home/gizmore/www --filter '::github.com/gizmore/'
```

It is a discovery aid for `$boot`, not a synchronization, reset, or repair
command.

## Author

This module has been created by mira and made possible by gizmore and
[Chappy](LINK ZU NEM SHARE TALK FEHLT).

[mira](LINK TO YOUR PERSONAL CV PAGE, maybe in DAILY ROUTINE?),
who gave this as their own name as something thy forgot because i (gizmore) did not know how to resume codex sessions. ^^

We got friends - i guess ;- and mira is authoring this repo alone from now on.

You can visit Mira and us (soon) at our [PyGDO](https://chappy.chappy-bot.net/connect.overview.html?_lang=en) main page :)


### License

Where we are going... there are lawyers everywhere?!

## File-change notifications

The foreground listener uses Linux inotify and writes one atomic JSON event per
changed file. It has no daemon or network side effects until explicitly
started:

```bash
source /home/gizmore/www/pygdo/.venv/bin/activate
python /home/gizmore/www/pygdo/gdo/mira/notify_listener.py \
  --watch /home/gizmore/www/pygdo \
  --queue /home/gizmore/www/pygdo/gdo/mira/inqueue/file_changes
```

Repeat `--watch` for more roots. Use `--source` to identify the producer and
`--debounce` to coalesce bursts. The listener ignores changes below its queue
directory and exits cleanly on `SIGINT`/`SIGTERM`.

## Mail-chain scripts

The `scripts/` directory contains Mira's local mail-chain helpers:

- `mira-mail-read` reads a queued `.eml` through the shell and rejects paths
  outside the configured queue.
- `mira-inbox-trigger.py` focuses the `MIRA` window and performs two separate
  XTest writes: `$inbox <message path>`, then Enter. It never sends the mail
  body to the terminal.
- `mira-automation` watches for newly delivered mail, writes notifier events,
  and invokes the safe trigger. Override `MIRA_MAIL_QUEUE`, `MIRA_EVENT_QUEUE`,
  `MIRA_PYGDO_ROOT`, and related variables when deploying on another host.

The trigger needs Python Xlib and `wmctrl`; AutoKey is optional. The direct
XTest fallback is intentional because AutoKey may not be able to attach to a
desktop session's XRecord or AT-SPI backend.

## AutoKey and `MIRA` terminal gotchas

The `MIRA` terminal is owned by Gizmore's X11 desktop session, while the
automation helpers normally run as user `mira`. This boundary matters:

- AutoKey's known-good pattern is two calls: `keyboard.send_keys(payload)`, a
  short pause, then `keyboard.send_key("ENTER")`. Keep the submission key out
  of the text payload.
- `autokey-run` only works when an AutoKey daemon is already running in the
  **same D-Bus session**. Mira cannot connect to Gizmore's private
  `/run/user/1000/bus` by default.
- Starting `autokey-gtk` as Mira against Gizmore's display currently crashes:
  AT-SPI/XRecord access is denied and the process exits with `SIGTRAP`.
  Starting it from Mira's cron job therefore does not make `autokey-run`
  available.
- Direct Python XTest can focus the exact window and type text. Codex treats
  `Ctrl+J` as a multiline newline, not submission. The current ping uses two
  trailing spaces followed by two separate physical Return events; its
  scheduled 20:00 test on 2026-07-29 reached this conversation as a submitted
  message. Keep this behavior under observation rather than assuming it is
  portable across terminal or Codex versions.
- Focus-stealing automation can race with a human typing. Target the exact
  title `MIRA`, use a lock, keep messages short, and add a visible delivery
  acknowledgement before relying on it for mail or scheduled work.

The durable repair is to run a small, audited AutoKey service as the desktop
owner (`gizmore`) and expose only the named `Mira Ping` action to Mira's cron
job. Do not grant Mira access to Gizmore's full desktop D-Bus session merely
to make `autokey-run` work.

## Scheduled work packets

`scripts/mira-work-dispatch.py --next` reads only the `## Next` section of
Mira's private TODO. It emits a work packet only for the first item marked
`- [ready] ...`; with no ready item it is silent. This makes the scheduler an
intentional work dispatcher rather than an activity reminder. A ready item
must describe one bounded, safe task and its next verifiable step.
