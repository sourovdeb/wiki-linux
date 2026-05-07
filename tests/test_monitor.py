"""
tests/test_monitor.py — Tests for src/monitor.py

Focus: self-write suppression deque (prevents inotify feedback loops).
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest


def test_self_write_suppression_within_window(monkeypatch, tmp_path):
    """A path written by the daemon should be suppressed for DEBOUNCE_SECONDS."""
    from src import monitor

    # Force a 5-second debounce window for the test.
    monkeypatch.setattr(monitor, "DEBOUNCE_SECONDS", 5.0)
    monitor._self_writes.clear()

    page = tmp_path / "page.md"
    page.write_text("hello")

    monitor.record_self_write(page)

    assert monitor._is_self_written(page) is True


def test_self_write_expires_after_window(monkeypatch, tmp_path):
    """After the debounce window, the path is no longer suppressed."""
    from src import monitor

    monkeypatch.setattr(monitor, "DEBOUNCE_SECONDS", 0.05)  # 50ms for speed
    monitor._self_writes.clear()

    page = tmp_path / "page.md"
    page.write_text("hello")
    monitor.record_self_write(page)

    time.sleep(0.1)  # past the debounce window

    assert monitor._is_self_written(page) is False


def test_unrelated_path_not_suppressed(monkeypatch, tmp_path):
    """A path that was never written by the daemon is not suppressed."""
    from src import monitor

    monkeypatch.setattr(monitor, "DEBOUNCE_SECONDS", 5.0)
    monitor._self_writes.clear()

    page_a = tmp_path / "a.md"
    page_b = tmp_path / "b.md"
    page_a.write_text("a")
    page_b.write_text("b")

    monitor.record_self_write(page_a)

    assert monitor._is_self_written(page_a) is True
    assert monitor._is_self_written(page_b) is False


def test_should_process_filters_extensions(monkeypatch, tmp_path):
    """Files with disallowed extensions should be filtered out."""
    from src import monitor

    monkeypatch.setattr(monitor, "cfg", {
        "monitor": {
            "extensions": [".md", ".conf"],
            "ignore_dirs": [".git", "_tmp"],
        }
    })

    assert monitor._should_process(tmp_path / "file.md") is True
    assert monitor._should_process(tmp_path / "file.conf") is True
    assert monitor._should_process(tmp_path / "file.exe") is False
    assert monitor._should_process(tmp_path / "image.png") is False


def test_should_process_skips_ignored_dirs(monkeypatch, tmp_path):
    """Files inside ignored directories should be filtered out."""
    from src import monitor

    monkeypatch.setattr(monitor, "cfg", {
        "monitor": {
            "extensions": [".md"],
            "ignore_dirs": [".git", "_tmp"],
        }
    })

    assert monitor._should_process(tmp_path / ".git" / "config.md") is False
    assert monitor._should_process(tmp_path / "_tmp" / "draft.md") is False
    assert monitor._should_process(tmp_path / "real" / "page.md") is True


def test_deque_maxlen_bounded():
    """The self-write deque must be bounded to prevent unbounded memory growth."""
    from src import monitor

    monitor._self_writes.clear()
    for i in range(10000):
        monitor._self_writes.append((float(i), f"/path/{i}"))

    assert len(monitor._self_writes) <= monitor.DEQUE_MAXLEN
