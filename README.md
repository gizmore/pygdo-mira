# pygdo-mira
Project-facing Mira context and helpers for the PyGDO chatbot system.


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
