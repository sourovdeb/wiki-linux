"""
src/sync.py — Git auto-commit for Wiki-OS.

Called by the wiki-sync.timer systemd unit every N minutes. Runs
`git add -A && git commit` inside WIKI_ROOT, then optionally pushes
if a remote is configured. Commit messages are auto-generated with a
timestamp and a short summary of changed files.

This module can also be called directly: `python3 -m src.sync`
"""
from __future__ import annotations

import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.config import cfg

log = logging.getLogger("wiki.sync")


def _run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _ensure_git_repo(wiki_root: Path) -> bool:
    """Initialise a git repo in wiki_root if one does not already exist."""
    if (wiki_root / ".git").exists():
        return True
    log.info("Initialising git repo in %s", wiki_root)
    rc, out, err = _run(["git", "init", "-b", cfg.get("git", {}).get("branch", "main")], wiki_root)
    if rc != 0:
        log.error("git init failed: %s", err)
        return False
    # Create a .gitignore that excludes the _tmp/ directory.
    gitignore = wiki_root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("_tmp/\n*.log\n")
    return True


def _changed_files(wiki_root: Path) -> list[str]:
    """Return a list of files that are staged or unstaged vs HEAD."""
    rc, out, err = _run(["git", "status", "--short"], wiki_root)
    if rc != 0 or not out:
        return []
    return [line[3:].strip() for line in out.splitlines() if line.strip()]


def commit(wiki_root: Path | None = None) -> bool:
    """
    Stage all changes in wiki_root and commit with an auto-generated message.
    Returns True if a commit was made, False if there was nothing to commit
    or if the commit failed.
    """
    if wiki_root is None:
        wiki_root = Path(cfg["wiki"]["root"])

    if not _ensure_git_repo(wiki_root):
        return False

    # Check whether there is anything to commit.
    changed = _changed_files(wiki_root)
    if not changed:
        log.debug("Nothing to commit in %s.", wiki_root)
        return False

    # Stage all changes.
    rc, out, err = _run(["git", "add", "-A"], wiki_root)
    if rc != 0:
        log.error("git add failed: %s", err)
        return False

    # Build a readable commit message.
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    file_summary = ", ".join(changed[:5])
    if len(changed) > 5:
        file_summary += f" (+{len(changed) - 5} more)"
    message = f"auto: {timestamp} — {file_summary}"

    rc, out, err = _run(["git", "commit", "-m", message], wiki_root)
    if rc != 0:
        log.error("git commit failed: %s", err)
        return False

    log.info("Committed %d files: %s", len(changed), message)
    return True


def push(wiki_root: Path | None = None) -> bool:
    """
    Push to the configured remote branch. A no-op if no remote is configured.
    """
    if wiki_root is None:
        wiki_root = Path(cfg["wiki"]["root"])

    remote = cfg.get("git", {}).get("remote", "")
    if not remote:
        log.debug("No git remote configured, skipping push.")
        return True

    branch = cfg.get("git", {}).get("branch", "main")
    rc, out, err = _run(["git", "push", remote, branch], wiki_root)
    if rc != 0:
        log.warning("git push failed (will retry next cycle): %s", err)
        return False

    log.info("Pushed to %s/%s.", remote, branch)
    return True


def sync(wiki_root: Path | None = None) -> None:
    """Commit and push — the full sync cycle called by the timer unit."""
    if wiki_root is None:
        wiki_root = Path(cfg["wiki"]["root"])
    committed = commit(wiki_root)
    if committed:
        push(wiki_root)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    sync()
