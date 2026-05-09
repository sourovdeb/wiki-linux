#!/usr/bin/env python3
"""Boot-time cleanup for regenerated garbage files.
This script is intentionally conservative and only removes low-risk artifacts.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

HOME = Path.home()
REPO_ROOT = Path(__file__).resolve().parent.parent


def safe_unlink(path: Path) -> bool:
    try:
        if path.is_file() or path.is_symlink():
            path.unlink(missing_ok=True)
            return True
    except Exception:
        return False
    return False


def remove_python_cache(root: Path) -> int:
    removed = 0
    for p in root.rglob("__pycache__"):
        if p.is_dir():
            for child in p.rglob("*"):
                if child.is_file():
                    removed += int(safe_unlink(child))
            try:
                p.rmdir()
            except Exception:
                pass
    for ext in ("*.pyc", "*.pyo"):
        for f in root.rglob(ext):
            removed += int(safe_unlink(f))
    return removed


def remove_old_tmp(root: Path, older_than_hours: int = 24) -> int:
    cutoff = time.time() - (older_than_hours * 3600)
    removed = 0
    patterns = ("*.tmp", "*.bak", "*~", "*.swp")
    for pattern in patterns:
        for f in root.rglob(pattern):
            try:
                if f.is_file() and f.stat().st_mtime < cutoff:
                    removed += int(safe_unlink(f))
            except Exception:
                continue
    return removed


def remove_partial_ollama_blobs() -> int:
    blobs_dir = HOME / ".ollama" / "models" / "blobs"
    removed = 0
    if not blobs_dir.exists():
        return 0
    for f in blobs_dir.glob("*.partial"):
        removed += int(safe_unlink(f))
    return removed


def remove_old_cache_files(cache_dir: Path, older_than_days: int = 14) -> int:
    if not cache_dir.exists():
        return 0
    cutoff = time.time() - (older_than_days * 86400)
    removed = 0
    for f in cache_dir.rglob("*"):
        try:
            if f.is_file() and f.stat().st_mtime < cutoff:
                removed += int(safe_unlink(f))
        except Exception:
            continue
    return removed


def main() -> int:
    total_removed = 0

    if REPO_ROOT.exists():
        total_removed += remove_python_cache(REPO_ROOT)
        total_removed += remove_old_tmp(REPO_ROOT, older_than_hours=24)

    total_removed += remove_partial_ollama_blobs()
    total_removed += remove_old_cache_files(HOME / ".cache", older_than_days=14)

    print(f"wiki-boot-cleanup removed files: {total_removed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
