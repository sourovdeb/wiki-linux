"""
title: Linux Sysinfo
author: wiki-linux
version: 1.0.0
description: Read-only Linux system snapshot. Whitelist-only commands; no shell, no sudo.
required_open_webui_version: 0.4.0
requirements:
licence: MIT
"""

import shutil
import subprocess
from pydantic import BaseModel, Field


_WHITELIST = {
    "disk":     ["df", "-hT", "-x", "tmpfs", "-x", "devtmpfs"],
    "memory":   ["free", "-h"],
    "load":     ["uptime"],
    "top_proc": ["ps", "-eo", "pid,user,%cpu,%mem,comm", "--sort=-%cpu"],
    "failed":   ["systemctl", "--failed", "--no-pager"],
    "kernel":   ["uname", "-a"],
}


class Tools:
    class Valves(BaseModel):
        timeout_s: int = Field(default=8, description="Per-command timeout.")
        top_proc_limit: int = Field(default=10, description="Lines kept for top processes.")
        include_systemctl: bool = Field(
            default=True, description="Include `systemctl --failed`."
        )

    def __init__(self):
        self.valves = self.Valves()

    async def system_snapshot(self) -> str:
        """
        Run a fixed set of read-only diagnostics and return a Markdown summary.

        :return: Markdown sections for disk, memory, load, top processes, failed services, kernel.
        """
        out = []
        for label, argv in _WHITELIST.items():
            if label == "failed" and not self.valves.include_systemctl:
                continue
            if shutil.which(argv[0]) is None:
                out.append(f"### {label}\n_(`{argv[0]}` not found)_")
                continue
            try:
                r = subprocess.run(
                    argv, capture_output=True, text=True, timeout=self.valves.timeout_s
                )
                text = r.stdout.strip() or r.stderr.strip() or "(no output)"
            except subprocess.TimeoutExpired:
                text = "(timed out)"
            except Exception as e:
                text = f"(error: {e})"

            if label == "top_proc":
                lines = text.splitlines()
                text = "\n".join(lines[: self.valves.top_proc_limit + 1])

            out.append(f"### {label}\n```\n{text}\n```")

        return "\n\n".join(out)
