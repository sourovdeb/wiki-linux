"""
tests/test_ingest.py — Tests for src/ingest.py
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src import ingest
from src.config import cfg


@pytest.fixture
def wiki_root(tmp_path: Path) -> Path:
    root = tmp_path / "wiki"
    root.mkdir()
    (root / "_archive").mkdir()
    cfg["wiki"] = {"root": str(root), "dirs": {"archive": "_archive"}}
    return root


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    src = tmp_path / "fake.conf"
    src.write_text("[main]\nkey = value\n")
    return src


@patch("src.llm.generate_wiki_page")
def test_ingest_file(mock_generate: MagicMock, wiki_root: Path, source_file: Path):
    mock_generate.return_value = {
        "target_path": "system/fake.conf.md",
        "content": "test content",
    }
    result = ingest.ingest_file(source_file, wiki_root)
    assert result is True
    target = wiki_root / "system/fake.conf.md"
    assert target.read_text() == "test content"


@patch("src.archive.archive_page")
@patch("src.llm.generate_wiki_page")
def test_reprocess_file(mock_generate: MagicMock, mock_archive: MagicMock, wiki_root: Path, source_file: Path):
    # Create a dummy page to be archived
    page_to_archive = wiki_root / "system"
    page_to_archive.mkdir()
    (page_to_archive / "fake.conf.md").write_text("old content")

    mock_generate.return_value = {
        "target_path": "system/fake.conf.md",
        "content": "new content",
    }
    result = ingest.reprocess_file(source_file, wiki_root)

    assert result is True
    mock_archive.assert_called_once()
    target = wiki_root / "system/fake.conf.md"
    assert target.read_text() == "new content"
