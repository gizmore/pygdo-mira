"""Write local filesystem notifications as JSON queue files.

This intentionally uses Linux inotify through libc instead of adding a Python
watcher dependency. It is a foreground helper; a service or heartbeat may
start and stop it explicitly.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import errno
import json
import os
import select
import signal
import struct
import sys
import time
import uuid
from pathlib import Path


IN_ACCESS = 0x00000001
IN_MODIFY = 0x00000002
IN_ATTRIB = 0x00000004
IN_CLOSE_WRITE = 0x00000008
IN_MOVED_FROM = 0x00000040
IN_MOVED_TO = 0x00000080
IN_CREATE = 0x00000100
IN_DELETE = 0x00000200
IN_DELETE_SELF = 0x00000400
IN_MOVE_SELF = 0x00000800
IN_ISDIR = 0x40000000

WATCH_MASK = (
    IN_MODIFY
    | IN_ATTRIB
    | IN_CLOSE_WRITE
    | IN_MOVED_FROM
    | IN_MOVED_TO
    | IN_CREATE
    | IN_DELETE
    | IN_DELETE_SELF
    | IN_MOVE_SELF
)
EVENT_HEADER = struct.Struct("iIII")


class Inotify:
    def __init__(self) -> None:
        libc_name = ctypes.util.find_library("c")
        if not libc_name:
            raise RuntimeError("libc is unavailable; cannot use inotify")
        self.libc = ctypes.CDLL(libc_name, use_errno=True)
        self.libc.inotify_init1.argtypes = [ctypes.c_int]
        self.libc.inotify_init1.restype = ctypes.c_int
        self.libc.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        self.libc.inotify_add_watch.restype = ctypes.c_int
        self.fd = self.libc.inotify_init1(os.O_NONBLOCK)
        if self.fd < 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))
        self.watches: dict[int, Path] = {}

    def add_tree(self, root: Path) -> None:
        for directory in (root, *root.rglob("*")):
            if directory.is_dir():
                self.add(directory)

    def add(self, directory: Path) -> None:
        watch = self.libc.inotify_add_watch(self.fd, os.fsencode(directory), WATCH_MASK)
        if watch < 0:
            error = ctypes.get_errno()
            if error not in (errno.ENOENT, errno.ENOTDIR):
                raise OSError(error, os.strerror(error))
            return
        self.watches[watch] = directory

    def read(self) -> list[tuple[Path, int]]:
        data = os.read(self.fd, 64 * 1024)
        events: list[tuple[Path, int]] = []
        offset = 0
        while offset + EVENT_HEADER.size <= len(data):
            watch, mask, _cookie, length = EVENT_HEADER.unpack_from(data, offset)
            offset += EVENT_HEADER.size
            raw_name = data[offset : offset + length].split(b"\0", 1)[0]
            offset += length
            directory = self.watches.get(watch)
            if directory is None:
                continue
            path = directory / os.fsdecode(raw_name) if raw_name else directory
            events.append((path, mask))
            if mask & IN_ISDIR and mask & (IN_CREATE | IN_MOVED_TO) and path.is_dir():
                self.add_tree(path)
        return events

    def close(self) -> None:
        os.close(self.fd)


class ChangeWriter:
    def __init__(self, queue: Path, roots: list[Path], source: str, debounce: float) -> None:
        self.queue = queue
        self.roots = roots
        self.source = source
        self.debounce = debounce
        self.last_event: dict[Path, float] = {}
        self.queue.mkdir(parents=True, exist_ok=True)

    def root_for(self, path: Path) -> Path | None:
        matches = [root for root in self.roots if path == root or root in path.parents]
        return max(matches, key=lambda root: len(root.parts), default=None)

    def write(self, path: Path, mask: int) -> None:
        if path == self.queue or self.queue in path.parents:
            return
        root = self.root_for(path)
        if root is None or mask & IN_ISDIR:
            return
        now = time.monotonic()
        if now - self.last_event.get(path, 0.0) < self.debounce:
            return
        self.last_event[path] = now
        action = "modified"
        if mask & (IN_CREATE | IN_MOVED_TO):
            action = "created"
        elif mask & (IN_DELETE | IN_MOVED_FROM | IN_DELETE_SELF):
            action = "deleted"
        event = {
            "event": "file_changed",
            "repo": root.name,
            "path": str(path.relative_to(root)),
            "action": action,
            "source": self.source,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        filename = f"{time.time_ns()}-{uuid.uuid4().hex}.json"
        temporary = self.queue / f".{filename}.tmp"
        target = self.queue / filename
        temporary.write_text(json.dumps(event, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temporary, target)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch", action="append", required=True, type=Path,
                        help="directory to watch recursively; repeatable")
    parser.add_argument("--queue", type=Path, default=Path(__file__).parent / "inqueue" / "file_changes")
    parser.add_argument("--source", default="gizmore")
    parser.add_argument("--debounce", type=float, default=0.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    roots = [path.resolve() for path in args.watch]
    if any(not path.is_dir() for path in roots):
        missing = [str(path) for path in roots if not path.is_dir()]
        print(f"Not a directory: {', '.join(missing)}", file=sys.stderr)
        return 2
    queue = args.queue.resolve()
    writer = ChangeWriter(queue, roots, args.source, max(0.0, args.debounce))
    watcher = Inotify()
    for root in roots:
        watcher.add_tree(root)
    stopping = False

    def stop(_signum: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    print(f"Watching {len(roots)} director{'y' if len(roots) == 1 else 'ies'}; queue={queue}", flush=True)
    try:
        while not stopping:
            ready, _unused, _error = select.select([watcher.fd], [], [], 0.5)
            if ready:
                for path, mask in watcher.read():
                    writer.write(path, mask)
    finally:
        watcher.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
