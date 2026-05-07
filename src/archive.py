"""
src/archive.py — Page archival for Wiki-Linux.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from src.config import cfg

log = logging.getLogger("wiki.archive")


def archive_page(wiki_path: Path) -> Path | None:
    """
    Move a wiki page to the archive directory with a timestamp.
    Returns the new path if successful, None otherwise.
    """
    if not wiki_path.is_file():
        log.warning("Cannot archive non-existent file: %s", wiki_path)
        return None

    wiki_root = Path(cfg.get("wiki", {}).get("root")).expanduser()
    archive_dir = wiki_root / cfg.get("wiki", {}).get("dirs", {}).get("archive", "_archive")
    archive_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    new_name = f"{wiki_path.stem}-{timestamp}{wiki_path.suffix}"
    new_path = archive_dir / new_name

    try:
        wiki_path.rename(new_path)
        log.info("Archived %s to %s", wiki_path, new_path)
        try:
            from src import tasklog
            tasklog.append_log(f"archive {wiki_path.name} → _archive/{new_name}")
        except Exception:
            pass
        return new_path
    except OSError as e:
        log.error("Failed to archive %s: %s", wiki_path, e)
        return None
