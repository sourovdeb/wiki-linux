"""
tests/test_llm.py — Tests for src/llm.py

Focuses on the security invariant: target_path must resolve inside WIKI_ROOT.
A path-escape vulnerability would let a hallucinating model write outside
the wiki, which is the most important thing this code prevents.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def wiki_root(tmp_path: Path) -> Path:
    """Provide an isolated temporary wiki root for each test."""
    root = tmp_path / "wiki"
    root.mkdir()
    return root


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    """A small fake /etc/something file the LLM is supposedly summarising."""
    src = tmp_path / "fake.conf"
    src.write_text("[main]\nkey = value\n")
    return src


def _make_response(payload: dict) -> dict:
    """Build the dict shape ollama.generate() returns."""
    return {"response": json.dumps(payload)}


def test_valid_path_accepted(monkeypatch, wiki_root, source_file):
    """A target_path inside the wiki root should be accepted."""
    from src import llm

    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})

    fake = MagicMock(return_value=_make_response({
        "target_path": "system/config/fake.conf.md",
        "title": "Fake Config",
        "content": "---\ntitle: Fake\n---\n# Fake",
        "links": [],
    }))

    with patch("src.llm.ollama.generate", fake):
        result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")

    assert result is not None
    assert result["target_path"] == "system/config/fake.conf.md"


def test_path_escape_rejected(monkeypatch, wiki_root, source_file):
    """target_path with .. that escapes wiki_root must be rejected."""
    from src import llm

    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})

    fake = MagicMock(return_value=_make_response({
        "target_path": "../../etc/passwd.md",
        "title": "Pwned",
        "content": "evil",
        "links": [],
    }))

    with patch("src.llm.ollama.generate", fake):
        result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")

    assert result is None, "Path escape was not rejected — security invariant broken!"


def test_absolute_path_rejected(monkeypatch, wiki_root, source_file):
    """An absolute target_path must be rejected even if it points inside wiki_root."""
    from src import llm

    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})

    fake = MagicMock(return_value=_make_response({
        "target_path": "/etc/shadow.md",
        "title": "Pwned",
        "content": "evil",
        "links": [],
    }))

    with patch("src.llm.ollama.generate", fake):
        result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")

    assert result is None


def test_malformed_json_returns_none(monkeypatch, wiki_root, source_file):
    """If the LLM returns garbage instead of JSON, llm.generate_wiki_page returns None."""
    from src import llm

    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})

    fake = MagicMock(return_value={"response": "not valid json {{{"})

    with patch("src.llm.ollama.generate", fake):
        result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")

    assert result is None


def test_missing_required_keys_returns_none(monkeypatch, wiki_root, source_file):
    """If JSON is valid but missing target_path or content, return None."""
    from src import llm

    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})

    fake = MagicMock(return_value=_make_response({"title": "no path"}))

    with patch("src.llm.ollama.generate", fake):
        result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")

    assert result is None


def test_non_md_extension_appended(monkeypatch, wiki_root, source_file):
    """If the model returns target_path without .md, it should be appended."""
    from src import llm

    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})

    fake = MagicMock(return_value=_make_response({
        "target_path": "system/config/no-extension",
        "content": "page body",
        "title": "test",
    }))

    with patch("src.llm.ollama.generate", fake):
        result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")

    assert result is not None
    assert result["target_path"].endswith(".md")
