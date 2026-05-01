"""
src/ingest.py — Handles ingestion of files into the wiki.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from src import archive, llm, indexer
from src.config import cfg

log = logging.getLogger("wiki.ingest")


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger to console."""
    log.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s] %(name)s: %(message)s"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)


def ingest_file(source_path: Path, wiki_root: Path, dry_run: bool = False) -> bool:
    """
    Generate a wiki page for a source file and write it to the wiki.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    page_data = llm.generate_wiki_page(source_path, wiki_root, timestamp)

    if not page_data:
        log.error("Failed to generate wiki page for %s", source_path)
        return False

    target_path = wiki_root / page_data["target_path"]

    if dry_run:
        log.info("[DRY RUN] Would write to %s", target_path)
        log.info("[DRY RUN] Content:\n%s", page_data["content"])
        return True

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(page_data["content"])
        log.info("Wrote wiki page to %s", target_path)
        try:
            from src import tasklog
            tasklog.append_log(f"ingest {source_path.name} → {page_data['target_path']}")
        except Exception:
            pass
        return True
    except OSError as e:
        log.error("Failed to write wiki page %s: %s", target_path, e)
        return False


def reprocess_file(source_path: Path, wiki_root: Path, dry_run: bool = False) -> bool:
    """
    Archive the existing wiki page and regenerate it from the source file.
    """
    # Find the existing wiki page by source path
    # This is a placeholder for a more robust search
    # For now, we assume a 1:1 mapping that we can find by walking the wiki
    found_page = None
    for md in wiki_root.rglob("*.md"):
        # A proper implementation would read frontmatter
        if md.name.startswith(source_path.stem):
            found_page = md
            break

    if found_page:
        if not dry_run:
            archive.archive_page(found_page)
        else:
            log.info("[DRY RUN] Would archive %s", found_page)

    return ingest_file(source_path, wiki_root, dry_run)


def main() -> None:
    """Entry point for the ingest script."""
    parser = argparse.ArgumentParser(description="Wiki-OS file ingestion")
    parser.add_argument("--reprocess", metavar="PATH", help="Reprocess a source file")
    parser.add_argument("--dry-run", action="store_true", help="Log actions but don't write files")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)

    wiki_root = Path(cfg.get("wiki", {}).get("root")).expanduser()

    if args.reprocess:
        source_path = Path(args.reprocess).resolve()
        if not source_path.is_file():
            log.error("Source file not found: %s", source_path)
            sys.exit(1)
        reprocess_file(source_path, wiki_root, args.dry_run)
    else:
        print("Usage: python -m src.ingest --reprocess <path>")
        sys.exit(1)


if __name__ == "__main__":
    main()
