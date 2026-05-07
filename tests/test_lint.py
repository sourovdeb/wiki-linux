"""
tests/test_lint.py — Tests for src/lint.py
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src import lint


@pytest.fixture
def wiki_root(tmp_path: Path) -> Path:
    root = tmp_path / "wiki"
    root.mkdir()
    return root


def test_check_links(wiki_root: Path):
    (wiki_root / "page1.md").write_text("Link to [[page2]].")
    (wiki_root / "page2.md").write_text("Link to [[page3]].")
    (wiki_root / "page3.md").write_text("Link to [[page1]].")

    broken = lint.check_links(wiki_root)
    assert len(broken) == 0


def test_broken_links(wiki_root: Path):
    (wiki_root / "page1.md").write_text("Link to [[page2]].")
    (wiki_root / "page2.md").write_text("Link to [[nonexistent]].")

    broken = lint.check_links(wiki_root)
    assert len(broken) == 1
    assert broken[0][0].name == "page2.md"
    assert broken[0][1] == "nonexistent"
