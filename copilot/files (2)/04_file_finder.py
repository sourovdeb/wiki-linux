"""
title: File Finder
author: wiki-linux
version: 1.1.0
description: Search files by glob under ~/wiki (default) or any home subdir. Read-only.
required_open_webui_version: 0.4.0
requirements:
licence: MIT
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


_TEXTY = {".md", ".txt", ".rst", ".py", ".js", ".ts", ".json", ".yml", ".yaml",
          ".toml", ".ini", ".cfg", ".sh", ".csv", ".log", ".html", ".xml"}


def _human(n: int) -> str:
    f = float(n)
    for unit in ("B", "K", "M", "G", "T"):
        if f < 1024:
            return f"{f:.0f}{unit}" if unit == "B" else f"{f:.1f}{unit}"
        f /= 1024
    return f"{f:.1f}P"


class Tools:
    class Valves(BaseModel):
        default_root: str = Field(
            default=str(Path.home() / "wiki"),
            description="Default root when none is supplied.",
        )
        max_results: int = Field(default=50, description="Cap on returned matches.")
        max_depth: int = Field(default=8, description="Max directory depth.")
        head_bytes: int = Field(
            default=2000, description="Bytes to read for the largest text file preview."
        )
        skip_dirs: str = Field(
            default=".git,node_modules,.venv,venv,__pycache__,.cache,target,dist,build,_archive",
            description="Comma-separated dir names to skip.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def find_files(
        self,
        pattern: str,
        root: Optional[str] = None,
        with_preview: bool = True,
    ) -> str:
        """
        Find files matching a glob pattern under a root directory inside the user's home.

        :param pattern: Glob pattern, e.g. "*.md" or "*notes*.txt".
        :param root: Directory to search. Defaults to the configured default_root. Must be inside $HOME.
        :param with_preview: If True, preview the largest text match.
        :return: Markdown table of matches plus optional preview.
        """
        home = Path.home().resolve()
        base = Path(root).expanduser().resolve() if root else Path(self.valves.default_root).expanduser().resolve()
        try:
            base.relative_to(home)
        except ValueError:
            return f"Error: root `{base}` is outside home `{home}`."

        if not base.is_dir():
            return f"Error: not a directory: {base}"
        if not pattern or "/" in pattern or ".." in pattern:
            return "Error: pattern must be a simple glob (no `/` or `..`)."

        skip = {s.strip() for s in self.valves.skip_dirs.split(",") if s.strip()}
        matches = []

        for dirpath, dirnames, filenames in os.walk(base):
            depth = len(Path(dirpath).relative_to(base).parts)
            if depth > self.valves.max_depth:
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if d not in skip]
            for f in filenames:
                if Path(f).match(pattern):
                    p = Path(dirpath) / f
                    try:
                        st = p.stat()
                    except OSError:
                        continue
                    matches.append((p, st.st_size, st.st_mtime))
                    if len(matches) >= self.valves.max_results:
                        break
            if len(matches) >= self.valves.max_results:
                break

        if not matches:
            return f"No matches for `{pattern}` under `{base}`."

        matches.sort(key=lambda t: t[1], reverse=True)
        rows = ["| Path | Size | Modified |", "|---|---|---|"]
        for p, sz, mt in matches:
            rel = p.relative_to(base)
            ts = datetime.fromtimestamp(mt).strftime("%Y-%m-%d %H:%M")
            rows.append(f"| `{rel}` | {_human(sz)} | {ts} |")

        out = [f"### {len(matches)} match(es) for `{pattern}` under `{base}`", "", *rows]

        if with_preview:
            largest = matches[0][0]
            if largest.suffix.lower() in _TEXTY:
                try:
                    text = largest.read_text(
                        encoding="utf-8", errors="replace"
                    )[: self.valves.head_bytes]
                    out += ["", f"### Preview — `{largest.relative_to(base)}`",
                            "```", text, "```"]
                except Exception as e:
                    out += ["", f"_Preview failed: {e}_"]
            else:
                out += ["", f"_Largest match is binary ({largest.suffix}); no preview._"]

        return "\n".join(out)
