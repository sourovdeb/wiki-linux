"""
src/lint.py — Linter for the wiki.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from src.config import cfg

log = logging.getLogger("wiki.lint")

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def check_links(wiki_root: Path) -> list[tuple[Path, str]]:
    """
    Find all broken wikilinks in the wiki.
    Returns a list of (path, broken_link) tuples.
    """
    broken_links = []
    all_pages = {str(p.relative_to(wiki_root).with_suffix("")) for p in wiki_root.rglob("*.md")}

    for md_file in wiki_root.rglob("*.md"):
        try:
            content = md_file.read_text()
            for match in WIKILINK_RE.finditer(content):
                link_target = match.group(1)
                # Normalize link: no extension, no leading/trailing whitespace
                normalized_target = link_target.strip()
                if normalized_target not in all_pages:
                    broken_links.append((md_file, link_target))
        except OSError as e:
            log.warning("Could not read %s: %s", md_file, e)

    return broken_links
