"""
title: Session Report
author: wiki-linux
version: 1.0.0
description: Read recent diagnostic / boot-check / audit reports from _meta/reports/ and recap the previous session.
required_open_webui_version: 0.4.0
requirements:
licence: MIT
"""

import json
import re
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        reports_dir: str = Field(
            default=str(Path.home() / "Documents/wiki-linux/wiki-linux/_meta/reports"),
            description="Directory containing report markdown files.",
        )
        max_reports: int = Field(default=5, description="Cap on returned reports.")
        max_chars_per_report: int = Field(
            default=4000, description="Truncate each report body to this many chars."
        )
        ollama_base: str = Field(
            default="http://127.0.0.1:11434", description="Ollama HTTP endpoint."
        )
        model: str = Field(
            default="llama3.2:3b",
            description="Model used when synthesise=True.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def get_session_report(
        self,
        since_hours: int = 24,
        synthesise: bool = False,
    ) -> str:
        """
        Return the most recent reports written within the last `since_hours`.

        :param since_hours: Time window in hours (default 24).
        :param synthesise: If True, ask Ollama for a one-paragraph recap across the reports.
        :return: Markdown sections, one per report (newest first), plus optional recap.
        """
        rdir = Path(self.valves.reports_dir).expanduser().resolve()
        if not rdir.is_dir():
            return f"Error: reports_dir not found: {rdir}"

        cutoff = time.time() - max(1, since_hours) * 3600
        files = []
        for p in rdir.glob("*.md"):
            try:
                mt = p.stat().st_mtime
            except OSError:
                continue
            if mt >= cutoff:
                files.append((p, mt))

        if not files:
            return f"No reports in `{rdir}` within the last {since_hours}h."

        files.sort(key=lambda t: t[1], reverse=True)
        files = files[: self.valves.max_reports]

        bodies = []
        out = [f"### {len(files)} report(s) in last {since_hours}h", ""]
        for p, mt in files:
            ts = datetime.fromtimestamp(mt, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                out.append(f"#### `{p.name}` — {ts}\n_(read error: {e})_")
                continue
            if len(text) > self.valves.max_chars_per_report:
                text = text[: self.valves.max_chars_per_report] + "\n…(truncated)"
            bodies.append((p.name, ts, text))
            out.append(f"#### `{p.name}` — {ts}\n\n{text}")

        if synthesise and bodies:
            joined = "\n\n---\n\n".join(
                f"# {n} ({ts})\n{t}" for n, ts, t in bodies
            )
            prompt = (
                "You are recapping the previous wiki-linux session. "
                "Given these reports (newest first), produce a 4-bullet recap: "
                "(1) what ran, (2) state now, (3) deltas vs prior report, (4) next step. "
                "Be specific. Cite report filenames inline.\n\n" + joined
            )
            try:
                payload = json.dumps(
                    {"model": self.valves.model, "prompt": prompt, "stream": False}
                ).encode()
                req = urllib.request.Request(
                    f"{self.valves.ollama_base}/api/generate",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=90) as r:
                    resp = json.loads(r.read())
                out += ["", "### Recap", resp.get("response", "").strip()]
            except Exception as e:
                out += ["", f"_LLM recap failed: {e}_"]

        return "\n\n".join(out)
