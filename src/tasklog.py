"""
src/tasklog.py — Append-only operation log for Wiki-Linux.

Every significant wiki action (ingest, archive, lint) appends a one-line
timestamped record to ~/wiki/_meta/log.md so the user has an audit trail
they can read in Obsidian or any Markdown viewer.

Design choices:
- One line per event (ISO 8601 UTC + message). Simple to `tail -f`.
- Never raises — if the write fails, we log the error and return.
- Calls monitor.record_self_write() so the inotify loop ignores the write.
- Also exposes write_task_note() for 'wiki task "<title>" "<body>"' (Phase 6).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from src.config import cfg

log = logging.getLogger("wiki.tasklog")


def _wiki_root() -> Path:
    return Path(cfg.get("wiki", {}).get("root", "~/wiki")).expanduser()


def _log_path(wiki_root: Path | None = None) -> Path:
    root = wiki_root or _wiki_root()
    return root / cfg.get("wiki", {}).get("dirs", {}).get("meta", "_meta") / "log.md"


def append_log(message: str, wiki_root: Path | None = None) -> None:
    """Append one timestamped line to ~/wiki/_meta/log.md.

    Format: '<ISO 8601 UTC>  <message>\\n'
    Creates _meta/log.md (and _meta/) if absent. Never raises.
    """
    try:
        target = _log_path(wiki_root)
        target.parent.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"{ts}  {message}\n"

        # Suppress self-write so monitor doesn't re-process this file.
        try:
            from src import monitor as _monitor  # late import to avoid cycles
            _monitor.record_self_write(target)
        except Exception:
            pass  # monitor may not be running; that's fine

        with target.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError as exc:
        log.error("tasklog: failed to append to log.md: %s", exc)


def write_task_note(
    title: str,
    body: str,
    tags: list[str] | None = None,
    wiki_root: Path | None = None,
) -> Path | None:
    """Create ~/wiki/_meta/tasks/<slug>.md with frontmatter + body.

    Returns the new path or None on failure.
    """
    root = wiki_root or _wiki_root()
    tasks_dir = root / "_meta" / "tasks"

    slug = (
        title.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .strip("-")
    )
    # Keep slug filesystem-safe
    slug = "".join(c if c.isalnum() or c == "-" else "" for c in slug)[:80]

    ts = datetime.now(timezone.utc)
    iso = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
    date = ts.strftime("%Y-%m-%d")
    target = tasks_dir / f"{date}-{slug}.md"

    try:
        tasks_dir.mkdir(parents=True, exist_ok=True)

        tag_str = ", ".join(tags or ["task"])
        content = (
            f"---\ntitle: {title}\ncreated: {iso}\ntags: [{tag_str}]\n---\n\n"
            f"# {title}\n\n{body}\n"
        )

        try:
            from src import monitor as _monitor
            _monitor.record_self_write(target)
        except Exception:
            pass

        target.write_text(content, encoding="utf-8")
        append_log(f"task note created: {target.name}", wiki_root)
        return target
    except OSError as exc:
        log.error("tasklog: failed to write task note %s: %s", target, exc)
        return None
