"""
tests/test_archwiki.py — Tests for src/archwiki.py

Focus: cache path construction, slug generation, and graceful failure on
network errors without requiring a live internet connection.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import urllib.error

import pytest


def test_slug_simple():
    from src.archwiki import _slug
    assert _slug("systemd-resolved") == "systemd-resolved"


def test_slug_spaces_and_caps():
    from src.archwiki import _slug
    assert _slug("Network configuration") == "network-configuration"


def test_slug_special_chars():
    from src.archwiki import _slug
    # Consecutive non-word characters are collapsed into a single hyphen.
    # "C++ build tools" → "c++ build tools" → "c-build-tools"
    assert _slug("C++ build tools") == "c-build-tools"


def test_cache_dir_respects_config(tmp_path, monkeypatch):
    """_cache_dir() should use the archwiki path from fix.doc_roots."""
    from src import archwiki

    monkeypatch.setattr(
        archwiki,
        "cfg",
        {"fix": {"doc_roots": [str(tmp_path / "archwiki")]}},
    )
    d = archwiki._cache_dir()
    assert d.exists()
    assert "archwiki" in str(d)


def test_fetch_page_writes_cache(tmp_path, monkeypatch):
    """fetch_page() should write a Markdown file to the cache dir."""
    from src import archwiki

    monkeypatch.setattr(
        archwiki,
        "cfg",
        {"fix": {"doc_roots": [str(tmp_path / "archwiki")]}},
    )

    fake_body = "== Introduction ==\nArch Linux is a general-purpose distribution."

    mock_response = MagicMock()
    mock_response.read.return_value = fake_body.encode("utf-8")
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response):
        result = archwiki.fetch_page("Arch Linux")

    assert result is not None
    assert result.exists()
    content = result.read_text()
    assert "Arch Linux" in content
    # Verify the canonical Arch Wiki URL is present (not just any substring).
    assert "https://wiki.archlinux.org/title/" in content
    assert fake_body.strip() in content


def test_fetch_page_returns_none_on_http_error(tmp_path, monkeypatch):
    """fetch_page() should return None (not raise) on HTTP errors."""
    from src import archwiki

    monkeypatch.setattr(
        archwiki,
        "cfg",
        {"fix": {"doc_roots": [str(tmp_path / "archwiki")]}},
    )

    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.HTTPError(
            url="http://test", code=404, msg="Not Found", hdrs=None, fp=None
        ),
    ):
        result = archwiki.fetch_page("Nonexistent Page")

    assert result is None


def test_fetch_page_returns_none_on_network_error(tmp_path, monkeypatch):
    """fetch_page() should return None (not raise) on network failures."""
    from src import archwiki

    monkeypatch.setattr(
        archwiki,
        "cfg",
        {"fix": {"doc_roots": [str(tmp_path / "archwiki")]}},
    )

    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("Name or service not known"),
    ):
        result = archwiki.fetch_page("Any Page")

    assert result is None


def test_search_cache_finds_matching_files(tmp_path, monkeypatch):
    """search_cache() should return files whose stem matches the slug."""
    from src import archwiki

    cache = tmp_path / "archwiki"
    cache.mkdir()
    (cache / "network-configuration.md").write_text("content")
    (cache / "systemd-resolved.md").write_text("content")
    (cache / "unrelated.md").write_text("content")

    monkeypatch.setattr(
        archwiki,
        "cfg",
        {"fix": {"doc_roots": [str(cache)]}},
    )

    results = archwiki.search_cache("network configuration")
    names = [p.name for p in results]
    assert "network-configuration.md" in names
    assert "unrelated.md" not in names
