"""
converter.py — MarkItDown wrapper for wiki-linux integration.
Converts any supported file → Markdown with YAML frontmatter,
then deposits the result into the wiki output directory.
"""

import hashlib
import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from markitdown import MarkItDown

logger = logging.getLogger("wiki_ingestor.converter")

# ---------------------------------------------------------------------------
# Supported extensions (mirrors MarkItDown's actual converter registry)
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {
    # Office
    ".docx", ".xlsx", ".xls", ".pptx", ".ppt",
    # PDF
    ".pdf",
    # Web / data
    ".html", ".htm", ".csv", ".json", ".xml",
    # Text / code (pass-through with structure)
    ".txt", ".md", ".rst",
    # Media (requires llm_client for images, speech_recognition for audio)
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
    ".mp3", ".wav", ".m4a", ".ogg",
    # Archives
    ".zip",
    # E-book
    ".epub",
}


# ---------------------------------------------------------------------------
# Ledger — SQLite file to track what has already been converted
# ---------------------------------------------------------------------------
class ConversionLedger:
    """Persists sha256 → output_path so files are not re-converted unless changed."""

    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversions (
                source_path TEXT PRIMARY KEY,
                sha256      TEXT NOT NULL,
                output_path TEXT NOT NULL,
                converted_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def is_changed(self, source_path: str, current_sha: str) -> bool:
        """Returns True if the file has never been converted or its hash changed."""
        row = self.conn.execute(
            "SELECT sha256 FROM conversions WHERE source_path = ?",
            (source_path,),
        ).fetchone()
        return row is None or row[0] != current_sha

    def record(self, source_path: str, sha256: str, output_path: str):
        self.conn.execute(
            """
            INSERT INTO conversions (source_path, sha256, output_path, converted_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source_path) DO UPDATE SET
                sha256 = excluded.sha256,
                output_path = excluded.output_path,
                converted_at = excluded.converted_at
            """,
            (source_path, sha256, output_path, datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _frontmatter(source: Path, title: str) -> str:
    return (
        "---\n"
        f'title: "{title}"\n'
        f'source: "{source.resolve()}"\n'
        f'source_type: "{source.suffix.lstrip(".")}"\n'
        f'converted_at: "{datetime.now(timezone.utc).isoformat()}"\n'
        f'tags: [wiki-ingestor, auto-converted]\n'
        "---\n\n"
    )


def _safe_stem(path: Path) -> str:
    """Produce a filesystem-safe slug from the file stem."""
    import re
    stem = path.stem
    stem = re.sub(r"[^\w\-]", "_", stem)
    return stem[:80]  # cap length


# ---------------------------------------------------------------------------
# Core converter
# ---------------------------------------------------------------------------
class WikiConverter:
    """
    Converts a source file to Markdown and writes it to output_dir,
    mirroring the relative sub-directory structure of the watched root.
    """

    def __init__(
        self,
        output_dir: Path,
        ledger: ConversionLedger,
        watch_root: Optional[Path] = None,
        llm_client=None,
        llm_model: Optional[str] = None,
    ):
        self.output_dir = Path(output_dir)
        self.ledger = ledger
        self.watch_root = Path(watch_root) if watch_root else None
        self.md = MarkItDown(
            llm_client=llm_client,
            llm_model=llm_model,
        )

    def is_supported(self, path: Path) -> bool:
        return path.suffix.lower() in SUPPORTED_EXTENSIONS

    def convert(self, source: Path) -> Optional[Path]:
        """
        Convert *source* → Markdown in output_dir.
        Returns the output path on success, None if skipped or failed.
        """
        source = Path(source).resolve()

        if not source.exists():
            logger.warning("Source not found, skipping: %s", source)
            return None

        if not self.is_supported(source):
            logger.debug("Unsupported extension %s — skipping %s", source.suffix, source)
            return None

        sha = _sha256(source)
        if not self.ledger.is_changed(str(source), sha):
            logger.debug("Unchanged, skipping: %s", source.name)
            return None

        # Determine output path (mirror directory structure under output_dir)
        if self.watch_root and source.is_relative_to(self.watch_root):
            rel = source.relative_to(self.watch_root)
        else:
            rel = Path(source.name)

        output_path = (self.output_dir / rel).with_suffix(".md")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # If input is already .md, just copy with frontmatter
        if source.suffix.lower() == ".md":
            raw = source.read_text(encoding="utf-8", errors="replace")
            if not raw.startswith("---"):
                raw = _frontmatter(source, source.stem) + raw
            output_path.write_text(raw, encoding="utf-8")
        else:
            try:
                result = self.md.convert(str(source))
                body = result.text_content or ""
            except Exception as exc:
                logger.error("MarkItDown failed on %s: %s", source, exc)
                return None

            title = _safe_stem(source).replace("_", " ")
            content = _frontmatter(source, title) + body
            output_path.write_text(content, encoding="utf-8")

        self.ledger.record(str(source), sha, str(output_path))
        logger.info("Converted → %s", output_path)
        return output_path
