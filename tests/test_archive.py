"""
tests/test_archive.py — Tests for src/archive.py
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src import archive
from src.config import cfg


@pytest.fixture
def wiki_root(tmp_path: Path) -> Path:
    root = tmp_path / "wiki"
    root.mkdir()
    cfg["wiki"] = {"root": str(root), "dirs": {"archive": "_archive"}}
    return root


def test_archive_page(wiki_root: Path):
    page = wiki_root / "test.md"
    page.write_text("content")

    archived_path = archive.archive_page(page)
    assert archived_path is not None
    assert archived_path.parent.name == "_archive"
    assert archived_path.name.startswith("test-")
    assert archived_path.name.endswith(".md")
    assert not page.exists()
    assert archived_path.read_text() == "content"


def test_archive_nonexistent_page(wiki_root: Path):
    page = wiki_root / "nonexistent.md"
    archived_path = archive.archive_page(page)
    assert archived_path is None
