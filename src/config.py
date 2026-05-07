"""
src/config.py — Configuration loader for Wiki-Linux.

Loads config.json from the standard location, expands ~ in all path
values, and exposes a single `cfg` dict that every other module imports.

Usage in any other module:
    from src.config import cfg
    wiki_root = cfg["wiki"]["root"]  # already a resolved Path string
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# The canonical config location. Override with WIKI_OS_CONFIG env var,
# which is useful for testing without touching the real config.
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "wiki-linux" / "config.json"
FALLBACK_CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def _expand_paths(obj: object) -> object:
    """Recursively expand ~ in any string value inside a nested dict/list."""
    if isinstance(obj, str):
        # Only expand strings that look like paths (start with ~ or /)
        if obj.startswith("~") or obj.startswith("/"):
            return str(Path(obj).expanduser().resolve())
        return obj
    if isinstance(obj, dict):
        return {k: _expand_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_paths(v) for v in obj]
    return obj


def load(path: Path | None = None) -> dict:
    """Load and return the configuration dictionary with all paths expanded."""
    if path is None:
        env_path = os.environ.get("WIKI_OS_CONFIG")
        if env_path:
            path = Path(env_path)
        elif DEFAULT_CONFIG_PATH.exists():
            path = DEFAULT_CONFIG_PATH
        elif FALLBACK_CONFIG_PATH.exists():
            path = FALLBACK_CONFIG_PATH
        else:
            raise FileNotFoundError(
                f"No config.json found. Expected at {DEFAULT_CONFIG_PATH}. "
                "Run install.sh to set up the default config."
            )

    with open(path) as f:
        raw = json.load(f)

    # Expand all ~ references so callers always get absolute paths.
    expanded = _expand_paths(raw)

    # Also make the wiki root a Path-validated absolute string.
    wiki_root = Path(expanded["wiki"]["root"])
    expanded["wiki"]["root"] = str(wiki_root)

    return expanded


# Module-level singleton so callers do `from src.config import cfg`
# and get the already-loaded dict without triggering a re-read.
# load() is called once at import time.
try:
    cfg: dict = load()
except FileNotFoundError:
    # Graceful degradation: if config is not found (e.g. during testing
    # with no install), cfg is None and each module should handle that.
    cfg = {}
