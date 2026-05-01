"""
tests/test_tasklog.py — Tests for src/tasklog.py
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src import tasklog
from src.config import cfg


@pytest.fixture
def wiki_root(tmp_path: Path) -> Path:
    root = tmp_path / "wiki"
    root.mkdir()
    cfg["wiki"] = {"root": str(root), "dirs": {"meta": "_meta"}}
    return root


def test_append_log_creates_file(wiki_root: Path):
    tasklog.append_log("test event", wiki_root)
    log_file = wiki_root / "_meta" / "log.md"
    assert log_file.exists()
    content = log_file.read_text()
    assert "test event" in content
    # ISO timestamp present
    assert "T" in content and "Z" in content


def test_append_log_multiple_entries(wiki_root: Path):
    tasklog.append_log("first event", wiki_root)
    tasklog.append_log("second event", wiki_root)
    log_file = wiki_root / "_meta" / "log.md"
    lines = [l for l in log_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 2
    assert "first event" in lines[0]
    assert "second event" in lines[1]


def test_write_task_note(wiki_root: Path):
    path = tasklog.write_task_note("My Task", "body text", ["task", "test"], wiki_root)
    assert path is not None
    assert path.exists()
    content = path.read_text()
    assert "My Task" in content
    assert "body text" in content
    assert "task" in content
    # verify log was also appended
    log_file = wiki_root / "_meta" / "log.md"
    assert log_file.exists()
