"""
tests/test_llm.py — Tests for src/llm.py

Focuses on the security invariant: target_path must resolve inside WIKI_ROOT.
Mocks use attribute-style access matching ollama >= 0.4.0 GenerateResponse.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def wiki_root(tmp_path: Path) -> Path:
    root = tmp_path / "wiki"
    root.mkdir()
    return root


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    src = tmp_path / "fake.conf"
    src.write_text("[main]\nkey = value\n")
    return src


def _make_response(payload: dict):
    """The real client returns a dict, not an object."""
    return {"response": json.dumps(payload)}


def _make_bad_response(text: str):
    """Simulate malformed (non-JSON) LLM output."""
    return {"response": text}


def test_valid_path_accepted(monkeypatch, wiki_root, source_file):
    from src import llm
    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})
    mock_client = MagicMock()
    mock_client.generate.return_value = _make_response({
        "target_path": "system/config/fake.conf.md",
        "title": "Fake Config",
        "content": "---\ntitle: Fake\n---\n# Fake",
        "links": [],
    })
    monkeypatch.setattr(llm, "_get_client", lambda: mock_client)

    result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")
    assert result is not None
    assert result["target_path"] == "system/config/fake.conf.md"


def test_path_escape_rejected(monkeypatch, wiki_root, source_file):
    from src import llm
    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})
    mock_client = MagicMock()
    mock_client.generate.return_value = _make_response({
        "target_path": "../../etc/passwd.md",
        "title": "Pwned",
        "content": "evil",
        "links": [],
    })
    monkeypatch.setattr(llm, "_get_client", lambda: mock_client)

    result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")
    assert result is None, "Path escape was not rejected!"


def test_absolute_path_rejected(monkeypatch, wiki_root, source_file):
    from src import llm
    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})
    mock_client = MagicMock()
    mock_client.generate.return_value = _make_response({
        "target_path": "/etc/shadow.md",
        "title": "Pwned",
        "content": "evil",
        "links": [],
    })
    monkeypatch.setattr(llm, "_get_client", lambda: mock_client)

    result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")
    assert result is None


def test_malformed_json_returns_none(monkeypatch, wiki_root, source_file):
    from src import llm
    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})
    mock_client = MagicMock()
    mock_client.generate.return_value = _make_bad_response("not valid json {{{")
    monkeypatch.setattr(llm, "_get_client", lambda: mock_client)

    result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")
    assert result is None


def test_missing_required_keys_returns_none(monkeypatch, wiki_root, source_file):
    from src import llm
    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})
    mock_client = MagicMock()
    mock_client.generate.return_value = _make_response({"title": "no path"})
    monkeypatch.setattr(llm, "_get_client", lambda: mock_client)

    result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")
    assert result is None


def test_non_md_extension_appended(monkeypatch, wiki_root, source_file):
    from src import llm
    monkeypatch.setattr(llm, "cfg", {"ollama": {"context_limit_bytes": 8000}})
    mock_client = MagicMock()
    mock_client.generate.return_value = _make_response({
        "target_path": "system/config/no-extension",
        "content": "page body",
        "title": "test",
        "links": [],
    })
    monkeypatch.setattr(llm, "_get_client", lambda: mock_client)

    result = llm.generate_wiki_page(source_file, wiki_root, "2026-05-01T00:00:00Z")
    assert result is not None
    assert result["target_path"] == "system/config/no-extension.md"
