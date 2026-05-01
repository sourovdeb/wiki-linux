"""
tests/test_config.py — Tests for src/config.py

Focus: path expansion (~/) and graceful handling of missing config files.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_expand_home_paths(tmp_path):
    """All path-like strings in config should have ~ expanded."""
    from src import config

    cfg_data = {
        "wiki": {"root": "~/wiki"},
        "monitor": {"watch_dirs": ["~/notes", "/etc"]},
        "logging": {"file": "~/wiki/_meta/log"},
    }
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps(cfg_data))

    loaded = config.load(cfg_file)

    assert "~" not in loaded["wiki"]["root"]
    assert loaded["wiki"]["root"].endswith("/wiki")
    assert all("~" not in p for p in loaded["monitor"]["watch_dirs"])


def test_non_path_strings_untouched(tmp_path):
    """Strings that aren't paths (e.g. model names) should not be expanded."""
    from src import config

    cfg_data = {
        "wiki": {"root": "~/wiki"},
        "ollama": {"model": "mistral", "base_url": "http://localhost:11434"},
    }
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps(cfg_data))

    loaded = config.load(cfg_file)

    assert loaded["ollama"]["model"] == "mistral"
    assert loaded["ollama"]["base_url"] == "http://localhost:11434"


def test_missing_file_raises(tmp_path):
    """Loading a non-existent config file should raise FileNotFoundError."""
    from src import config

    with pytest.raises(FileNotFoundError):
        config.load(tmp_path / "does_not_exist.json")


def test_lists_recursed(tmp_path):
    """Path expansion should recurse into nested lists."""
    from src import config

    cfg_data = {
        "wiki": {"root": "~/wiki"},
        "monitor": {
            "etc_allowlist": ["/etc/pacman.conf", "/etc/fstab"],
            "watch_dirs": ["~/notes", "~/projects"],
        }
    }
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps(cfg_data))

    loaded = config.load(cfg_file)

    for path in loaded["monitor"]["watch_dirs"]:
        assert path.startswith("/")  # resolved absolute
    for path in loaded["monitor"]["etc_allowlist"]:
        assert path.startswith("/")
