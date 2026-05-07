"""
watcher.py — Cross-platform file-system watcher.
Uses the `watchdog` library to react to file creation/modification events
and feed them into WikiConverter.
"""

import logging
import threading
import time
from pathlib import Path
from typing import List

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .converter import WikiConverter

logger = logging.getLogger("wiki_ingestor.watcher")


class _Handler(FileSystemEventHandler):
    def __init__(self, converter: WikiConverter, debounce_seconds: float = 2.0):
        super().__init__()
        self._converter = converter
        self._debounce = debounce_seconds
        self._pending = {}
        self._lock = threading.Lock()

    def _schedule(self, path: str):
        """Debounce rapid events (e.g. large file being written in chunks)."""
        with self._lock:
            if path in self._pending:
                self._pending[path].cancel()
            timer = threading.Timer(self._debounce, self._process, args=(path,))
            self._pending[path] = timer
            timer.start()

    def _process(self, path: str):
        with self._lock:
            self._pending.pop(path, None)
        p = Path(path)
        if p.is_file():
            self._converter.convert(p)

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            logger.debug("Created: %s", event.src_path)
            self._schedule(event.src_path)

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            logger.debug("Modified: %s", event.src_path)
            self._schedule(event.src_path)

    def on_moved(self, event: FileSystemEvent):
        if not event.is_directory:
            logger.debug("Moved to %s", event.dest_path)
            self._schedule(event.dest_path)


class IngestorWatcher:
    """
    Watches one or more directories and converts new/changed files.

    Usage:
        watcher = IngestorWatcher(converter, watch_dirs=[Path("~/Documents")])
        watcher.start()          # non-blocking
        ...
        watcher.stop()
    """

    def __init__(
        self,
        converter: WikiConverter,
        watch_dirs: List[Path],
        recursive: bool = True,
        debounce_seconds: float = 2.0,
    ):
        self._converter = converter
        self._watch_dirs = [Path(d).expanduser().resolve() for d in watch_dirs]
        self._recursive = recursive
        self._debounce = debounce_seconds
        self._observer = None

    def start(self):
        handler = _Handler(self._converter, self._debounce)
        self._observer = Observer()
        for directory in self._watch_dirs:
            if not directory.exists():
                logger.warning("Watch directory does not exist, skipping: %s", directory)
                continue
            self._observer.schedule(handler, str(directory), recursive=self._recursive)
            logger.info("Watching: %s (recursive=%s)", directory, self._recursive)
        self._observer.start()

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()

    def run_forever(self):
        """Block the calling thread until KeyboardInterrupt or stop()."""
        self.start()
        try:
            while self._observer and self._observer.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            logger.info("Watcher stopped.")
