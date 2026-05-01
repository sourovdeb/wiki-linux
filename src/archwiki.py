"""
src/archwiki.py — Arch Wiki fetcher and local cache for Wiki-Linux.

Fetches Arch Wiki pages via the MediaWiki REST API (no authentication
required, read-only). Stores the plain-text wikitext as a Markdown page
in ~/.cache/wiki-linux/archwiki/ so that src/fix.py can search it.

The module is deliberately dependency-free beyond the standard library.
It does NOT require requests; it uses urllib.request for the HTTP call.

Usage:
    python3 -m src.archwiki "systemd-resolved"
    python3 -m src.archwiki "Network configuration"

Design:
    - URL is built from the page title (spaces → underscores).
    - Response is wikitext (plain text), stored as-is in the cache.
    - A minimal Markdown wrapper is written alongside so Obsidian can
      display it with a frontmatter title and a link back to the original.
    - Cache dir: ~/.cache/wiki-linux/archwiki/<slug>.md
    - The function returns the cached file Path, or None on failure.
    - Never writes to ~/wiki/ directly; the cache feeds src/fix.py RAG.
"""
from __future__ import annotations

import logging
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from src.config import cfg

log = logging.getLogger("wiki.archwiki")

ARCH_WIKI_API = "https://wiki.archlinux.org/api/rest_v1/page/wiki/{title}"
USER_AGENT = "wiki-linux/1.0 (personal wiki cache; +https://github.com/sourovdeb/wiki-linux)"


def _slug(title: str) -> str:
    """Convert a page title to a safe filename stem."""
    return re.sub(r"[^\w\-]", "-", title.lower().strip()).strip("-")


def _cache_dir() -> Path:
    roots = cfg.get("fix", {}).get("doc_roots", [])
    for r in roots:
        p = Path(r).expanduser()
        if "archwiki" in str(p):
            p.mkdir(parents=True, exist_ok=True)
            return p
    # Fallback: ~/.cache/wiki-linux/archwiki
    fallback = Path.home() / ".cache" / "wiki-linux" / "archwiki"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def fetch_page(title: str) -> Path | None:
    """
    Fetch an Arch Wiki page by title and store it in the local cache.

    Returns the Path to the cached Markdown file on success, or None if
    the fetch fails (network error, 404, etc.).
    """
    api_url = ARCH_WIKI_API.format(title=urllib.parse.quote(title, safe=""))
    req = urllib.request.Request(
        api_url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/plain"},
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        log.warning("Arch Wiki returned HTTP %s for %r: %s", e.code, title, e)
        return None
    except (urllib.error.URLError, OSError) as e:
        log.warning("Arch Wiki fetch failed for %r: %s", title, e)
        return None

    if not body.strip():
        log.warning("Empty response for Arch Wiki page %r", title)
        return None

    cache_dir = _cache_dir()
    slug = _slug(title)
    target = cache_dir / f"{slug}.md"

    arch_url = f"https://wiki.archlinux.org/title/{urllib.parse.quote(title, safe='')}"
    content = (
        f"---\n"
        f"title: {title}\n"
        f"source: {arch_url}\n"
        f"tags: [archwiki, cached]\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"> Source: [{arch_url}]({arch_url})\n\n"
        f"{body.strip()}\n"
    )

    try:
        target.write_text(content, encoding="utf-8")
        log.info("Cached Arch Wiki page %r → %s", title, target)
        return target
    except OSError as e:
        log.error("Failed to write Arch Wiki cache for %r: %s", title, e)
        return None


def search_cache(query: str) -> list[Path]:
    """Return cached Arch Wiki pages whose filename contains the query slug."""
    cache_dir = _cache_dir()
    slug = _slug(query)
    return sorted(p for p in cache_dir.glob("*.md") if slug in p.stem)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    if len(sys.argv) < 2:
        print("Usage: python3 -m src.archwiki '<Arch Wiki page title>'")
        print("Example: python3 -m src.archwiki 'systemd-resolved'")
        sys.exit(1)

    title = " ".join(sys.argv[1:])
    path = fetch_page(title)
    if path:
        print(f"Cached: {path}")
        if "glow" in __import__("shutil").which("glow") or "":
            import subprocess
            subprocess.run(["glow", str(path)], check=False)
    else:
        print(f"Failed to fetch Arch Wiki page: {title!r}", file=sys.stderr)
        sys.exit(1)
