"""
src/indexer.py — Wiki index generator for Wiki-Linux.

Rebuilds _meta/index.md and _meta/recent.md by walking the wiki tree
and reading YAML frontmatter from each page. Called by the monitor after
every LLM write and at daemon startup.

The index is intentionally stored as Markdown so it opens in Obsidian,
mdt, and every other wiki viewer without special handling.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import yaml

from src.config import cfg

log = logging.getLogger("wiki.indexer")

# Number of recently-changed pages shown in _meta/recent.md.
RECENT_COUNT = 20


def _read_frontmatter(path: Path) -> dict:
    """
    Extract YAML frontmatter from a Markdown file.
    Returns an empty dict if the file has no frontmatter or cannot be parsed.
    """
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return {}

    if not text.startswith("---"):
        return {}

    # Find the closing --- line.
    end = text.find("\n---", 3)
    if end == -1:
        return {}

    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}


def _page_title(path: Path, frontmatter: dict) -> str:
    """Return the best available title for a page."""
    return (
        frontmatter.get("title")
        or path.stem.replace("-", " ").replace("_", " ").title()
    )


def rebuild(wiki_root: Path) -> None:
    """
    Walk wiki_root, collect metadata from each .md file, and write
    _meta/index.md and _meta/recent.md. Files under _meta/ and _tmp/ are
    excluded from the index to avoid self-referential loops.
    """
    if not wiki_root.is_dir():
        log.error("Wiki root '%s' not found, cannot build index.", wiki_root)
        return

    meta_dir = wiki_root / cfg["wiki"]["dirs"].get("meta", "_meta")
    tmp_dir  = wiki_root / cfg["wiki"]["dirs"].get("tmp",  "_tmp")
    meta_dir.mkdir(parents=True, exist_ok=True)

    pages = []
    for md in sorted(wiki_root.rglob("*.md")):
        # Skip pages inside _meta and _tmp.
        try:
            md.relative_to(meta_dir)
            continue
        except ValueError:
            pass
        try:
            md.relative_to(tmp_dir)
            continue
        except ValueError:
            pass

        fm = _read_frontmatter(md)
        rel = md.relative_to(wiki_root)
        pages.append({
            "path":    str(rel),
            "title":   _page_title(md, fm),
            "updated": fm.get("updated", ""),
            "tags":    fm.get("tags", []),
            "source":  fm.get("source", ""),
        })

    _write_index(meta_dir / "index.md", pages, wiki_root)
    _write_recent(meta_dir / "recent.md", pages)
    log.info("Index rebuilt: %d pages.", len(pages))


def _write_index(target: Path, pages: list[dict], wiki_root: Path) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Group pages by their top-level directory.
    groups: dict[str, list[dict]] = {}
    for p in pages:
        top = Path(p["path"]).parts[0] if len(Path(p["path"]).parts) > 1 else "root"
        groups.setdefault(top, []).append(p)

    lines = [
        "---",
        "title: Wiki Index",
        f"updated: {now}",
        "---",
        "",
        f"# Wiki Index",
        "",
        f"*{len(pages)} pages — last rebuilt {now}*",
        "",
    ]

    for group, group_pages in sorted(groups.items()):
        lines.append(f"## {group.replace('_', ' ').title()}")
        lines.append("")
        for p in sorted(group_pages, key=lambda x: x["title"]):
            wiki_path = p["path"].replace(".md", "")
            tag_str = "  " + " ".join(f"`{t}`" for t in p["tags"]) if p["tags"] else ""
            lines.append(f"- [[{wiki_path}|{p['title']}]]{tag_str}")
        lines.append("")

    target.write_text("\n".join(lines))


def _write_recent(target: Path, pages: list[dict]) -> None:
    # Sort by 'updated' descending; pages without timestamps go to the bottom.
    dated = sorted(
        [p for p in pages if p["updated"]],
        key=lambda x: x["updated"],
        reverse=True,
    )
    undated = [p for p in pages if not p["updated"]]
    ordered = (dated + undated)[:RECENT_COUNT]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "---",
        "title: Recently Changed",
        f"updated: {now}",
        "---",
        "",
        "# Recently Changed",
        "",
    ]
    for p in ordered:
        wiki_path = p["path"].replace(".md", "")
        updated = p["updated"] or "unknown"
        lines.append(f"- [[{wiki_path}|{p['title']}]] — {updated}")

    target.write_text("\n".join(lines))


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    rebuild(Path(cfg["wiki"]["root"]))
