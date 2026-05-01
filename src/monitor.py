"""
src/monitor.py — Core inotify daemon for Wiki-Linux.

This is the daemon's main event loop. It watches ~/wiki, ~/notes, and the
/etc allowlist with inotify, and for each relevant file change calls llm.py
to generate or update the corresponding wiki page.

Two correctness details are worth understanding before reading the code:

1. SELF-WRITE SUPPRESSION: When the daemon writes a new wiki page, inotify
   detects that write and fires an event. Without suppression, the daemon
   would reprocess the page it just wrote, which would trigger another write,
   and so on forever. The fix is a deque of (timestamp, path) pairs. Any
   event whose path appears in the deque within DEBOUNCE_SECONDS is silently
   dropped.

2. RECURSIVE WATCHING: inotify watches are per-directory, not recursive. To
   watch a whole tree, we must add a watch for every existing subdirectory at
   startup, and then add new watches dynamically as new subdirectories are
   created (IN_CREATE with IN_ISDIR flag). We store a wd→Path mapping for
   every active watch so we can reconstruct the full path from an event.
"""
from __future__ import annotations

import argparse
import logging
import logging.handlers
import signal
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import inotify_simple
from inotify_simple import flags as iflags

from src.config import cfg
from src import llm, indexer

log = logging.getLogger("wiki.monitor")

def setup_logging(log_path: Path | None = None, level: int = logging.INFO) -> None:
    """Configure root logger to console and optionally a rotating file."""
    log.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s] %(name)s: %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

# Events we care about: CLOSE_WRITE fires when a write FD is closed (safer
# than IN_MODIFY which fires mid-write). CREATE catches new files. MOVED_TO
# catches files renamed into a watched directory (common with atomic writes).
WATCH_FLAGS = (
    iflags.CLOSE_WRITE
    | iflags.CREATE
    | iflags.MOVED_TO
    | iflags.DELETE
)

# We also need CREATE|IN_ISDIR to detect new subdirectories so we can add
# watches for them dynamically.
DIR_CREATE_FLAG = iflags.CREATE | iflags.ISDIR

# How many seconds to ignore events for a path after we ourselves wrote it.
DEBOUNCE_SECONDS: float = float(cfg.get("monitor", {}).get("debounce_seconds", 5))

# Maximum entries in the self-write deque. 512 is ample for any normal wiki.
DEQUE_MAXLEN = 512

# Paths to record as self-writes so the monitor can skip them.
_self_writes: deque[tuple[float, str]] = deque(maxlen=DEQUE_MAXLEN)


def record_self_write(path: Path) -> None:
    """
    Mark a path as recently written by the daemon.
    Called by any code that writes to WIKI_ROOT so the event loop skips it.
    """
    _self_writes.append((time.monotonic(), str(path.resolve())))


def _is_self_written(path: Path) -> bool:
    """Return True if this path was written by the daemon within DEBOUNCE_SECONDS."""
    now = time.monotonic()
    resolved = str(path.resolve())
    return any(
        now - ts < DEBOUNCE_SECONDS and p == resolved
        for ts, p in _self_writes
    )


def _should_process(path: Path) -> bool:
    """Return True if this file change should trigger an LLM update."""
    # Filter by extension.
    extensions = cfg.get("monitor", {}).get("extensions", [".md", ".conf", ".txt"])
    if path.suffix not in extensions:
        return False

    # Skip ignored directory names in the path.
    ignore_dirs = set(cfg.get("monitor", {}).get("ignore_dirs", [".git", "_tmp"]))
    if ignore_dirs.intersection(set(path.parts)):
        return False

    return True


def _add_watch(inotify: inotify_simple.INotify, path: Path, wd_map: dict) -> None:
    """Add a single inotify watch and record the wd→Path mapping."""
    try:
        wd = inotify.add_watch(str(path), WATCH_FLAGS | iflags.ISDIR)
        wd_map[wd] = path
        log.debug("Watching %s (wd=%d)", path, wd)
    except OSError as e:
        log.warning("Cannot watch %s: %s", path, e)


def _watch_recursive(inotify: inotify_simple.INotify, root: Path, wd_map: dict) -> None:
    """
    Add inotify watches for root and every readable subdirectory beneath it.
    Directories in ignore_dirs are skipped, as are directories the daemon
    cannot read (e.g. root-owned subdirs of /etc).
    """
    ignore = set(cfg.get("monitor", {}).get("ignore_dirs", [".git", "_tmp"]))
    _add_watch(inotify, root, wd_map)
    for subdir in sorted(root.rglob("*/")):
        if ignore.intersection(set(subdir.parts)):
            continue
        if not subdir.is_dir():
            continue
        _add_watch(inotify, subdir, wd_map)


def _watch_etc_allowlist(inotify: inotify_simple.INotify, wd_map: dict) -> None:
    """
    Add read-only inotify watches for individual files and directories in the
    /etc allowlist. We never write to these paths; they are observed only.
    """
    for raw in cfg.get("monitor", {}).get("etc_allowlist", []):
        p = Path(raw)
        if not p.exists():
            log.info("Allowlist path does not exist, skipping: %s", p)
            continue
        if p.is_dir():
            _watch_recursive(inotify, p, wd_map)
        else:
            # Watch the parent directory so we get events when the file is
            # atomically replaced (the standard pattern for config editors).
            parent = p.parent
            if parent not in wd_map.values():
                _add_watch(inotify, parent, wd_map)


def _process_event(event: inotify_simple.Event, wd_map: dict, wiki_root: Path) -> None:
    """
    Handle a single inotify event: reconstruct the full path, apply filters,
    call the LLM, write the wiki page, and rebuild the index.
    """
    parent_dir = wd_map.get(event.wd)
    if parent_dir is None:
        return  # Stale watch descriptor — can happen after removals.

    # Reconstruct the full path. event.name is the filename within the directory.
    name = event.name  # str, decoded by inotify_simple
    if not name:
        return
    full_path = parent_dir / name

    # Skip if a directory was created (we handle that separately for new watches).
    if event.mask & iflags.ISDIR:
        return

    if not _should_process(full_path):
        return

    if _is_self_written(full_path):
        log.debug("Skipping self-written path: %s", full_path)
        return

    log.info("Processing change: %s", full_path)

    timestamp = datetime.now(timezone.utc).isoformat()
    page = llm.generate_wiki_page(full_path, wiki_root, timestamp)
    if page is None:
        log.warning("LLM returned no page for %s", full_path)
        return

    target = wiki_root / page["target_path"]
    target.parent.mkdir(parents=True, exist_ok=True)

    # Record before writing so the subsequent inotify event is suppressed.
    record_self_write(target)
    target.write_text(page["content"])
    log.info("Wrote wiki page: %s", target)

    # Rebuild the wiki index so _meta/index.md stays current.
    indexer.rebuild(wiki_root)


def run(dry_run: bool = False, once: bool = False) -> None:
    """
    Main event loop. Blocks until SIGTERM or SIGINT.

    dry_run: log events but do not call the LLM or write files.
    once:    process one event and return (for integration testing).
    """
    wiki_root = Path(cfg["wiki"]["root"])
    wiki_root.mkdir(parents=True, exist_ok=True)

    # Build initial directory structure so the wiki has a home.
    for subdir in cfg["wiki"]["dirs"].values():
        (wiki_root / subdir).mkdir(parents=True, exist_ok=True)

    inotify = inotify_simple.INotify()
    wd_map: dict[int, Path] = {}

    # Watch configured directories recursively.
    for raw_dir in cfg.get("monitor", {}).get("watch_dirs", []):
        d = Path(raw_dir)
        if d.exists():
            _watch_recursive(inotify, d, wd_map)
        else:
            log.info("Watch dir does not exist yet, will create: %s", d)
            d.mkdir(parents=True, exist_ok=True)
            _watch_recursive(inotify, d, wd_map)

    # Watch /etc paths (read-only, observation only).
    _watch_etc_allowlist(inotify, wd_map)

    log.info("Wiki-Linux monitor started. Watching %d paths.", len(wd_map))

    # Build an initial index on startup so _meta/ is populated immediately.
    indexer.rebuild(wiki_root)

    shutdown = False

    def _handle_signal(sig, _frame):
        nonlocal shutdown
        log.info("Signal %s received, shutting down.", sig)
        shutdown = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    while not shutdown:
        # Read with a 1-second timeout so we remain responsive to signals.
        events = inotify.read(timeout=1000)

        for event in events:
            # If a new directory was created inside a watched tree, add a watch
            # for it so we don't miss files created in it immediately after.
            if event.mask & iflags.ISDIR and event.mask & iflags.CREATE:
                parent = wd_map.get(event.wd)
                if parent:
                    new_dir = parent / event.name
                    if new_dir.is_dir():
                        _add_watch(inotify, new_dir, wd_map)

            if dry_run:
                log.info("[dry-run] Event: wd=%d name=%s mask=%s",
                         event.wd, event.name, iflags.from_mask(event.mask))
                continue

            _process_event(event, wd_map, wiki_root)

            if once:
                return

    inotify.close()
    log.info("Wiki-Linux monitor stopped.")


def main() -> None:
    """Entry point for the daemon."""
    parser = argparse.ArgumentParser(description="Wiki-Linux inotify monitor daemon")
    parser.add_argument("--dry-run", action="store_true", help="Log actions but don't write files")
    parser.add_argument("--once", action="store_true", help="Run one event loop pass and exit")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    log_file = Path(cfg.get("monitor", {}).get("log_file", "")).expanduser()
    setup_logging(log_file, log_level)

    log.info("--- Wiki-Linux monitor starting up ---")
    log.info("Config: %s", cfg.get("config_path"))
    log.info("Wiki root: %s", cfg.get("wiki", {}).get("root"))

    run(dry_run=args.dry_run, once=args.once)


if __name__ == "__main__":
    main()
