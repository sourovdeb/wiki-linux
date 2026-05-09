"""
title: Reminder
author: wiki-linux
version: 2.0.0
description: Add, list, and check-due reminders. The "automatic" loop is a systemd timer calling check_due.
required_open_webui_version: 0.4.0
requirements: python-dateutil
licence: MIT
"""

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        reminders_file: str = Field(
            default="/home/sourov/Documents/wiki-linux/wiki-linux/_meta/reminders.jsonl",
            description="JSON-lines file where reminders are appended.",
        )
        notify: bool = Field(
            default=True,
            description="If True and notify-send is available, fire a desktop notification on due.",
        )
        notify_title: str = Field(
            default="Wiki Reminder",
            description="Notification title used by notify-send.",
        )

    def __init__(self):
        self.valves = self.Valves()

    # ---------- internal helpers ----------

    def _path(self) -> Path:
        p = Path(self.valves.reminders_file).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.touch()
        return p

    def _load(self) -> list:
        out = []
        for line in self._path().read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    def _save_all(self, records: list) -> None:
        self._path().write_text(
            "\n".join(json.dumps(r) for r in records) + ("\n" if records else ""),
            encoding="utf-8",
        )

    # ---------- public methods ----------

    async def add_reminder(self, message: str, when: str) -> str:
        """
        Add a reminder.

        :param message: What to remind about (1 line).
        :param when: Natural-language or ISO-8601 time, e.g. "tomorrow 9am", "2026-05-09T15:00".
        :return: Confirmation with parsed ISO time and storage path.
        """
        if not message.strip():
            return "Error: empty message."
        if not when.strip():
            return "Error: empty when."

        try:
            from dateutil import parser as dtp
            due = dtp.parse(when, fuzzy=True)
        except Exception as e:
            return f"Error: could not parse time `{when}`: {e}"
        if due.tzinfo is None:
            due = due.astimezone()
        if due < datetime.now(due.tzinfo):
            return f"Error: time is in the past ({due.isoformat()})."

        record = {
            "id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f"),
            "created": datetime.now(timezone.utc).isoformat(),
            "due": due.isoformat(),
            "message": message.strip(),
            "fired": False,
        }
        with self._path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return f"Reminder saved.\n- Due: `{due.isoformat()}`\n- Message: {record['message']}\n- Id: `{record['id']}`"

    async def list_reminders(self, include_fired: bool = False) -> str:
        """
        List reminders.

        :param include_fired: If True, include reminders that have already fired.
        :return: Markdown table of pending (and optionally fired) reminders.
        """
        records = self._load()
        if not records:
            return "No reminders."
        rows = ["| Id | Due | Status | Message |", "|---|---|---|---|"]
        now = datetime.now(timezone.utc).astimezone()
        kept = 0
        for r in sorted(records, key=lambda x: x.get("due", "")):
            fired = r.get("fired", False)
            if fired and not include_fired:
                continue
            try:
                from dateutil import parser as dtp
                due = dtp.parse(r["due"])
            except Exception:
                due = None
            status = "fired" if fired else ("DUE" if due and due <= now else "pending")
            rows.append(f"| `{r.get('id','?')}` | {r.get('due','?')} | {status} | {r.get('message','').replace('|','\\|')} |")
            kept += 1
        if kept == 0:
            return "No pending reminders."
        return "\n".join(rows)

    async def check_due(self, mark_fired: bool = True) -> str:
        """
        Return reminders that are due now and (optionally) mark them fired + send a desktop notification.
        Designed to be called periodically (e.g. by a systemd user timer) to act as the automatic loop.

        :param mark_fired: If True, persist fired=true and skip on next call.
        :return: Markdown list of reminders that fired this call, or "No due reminders."
        """
        records = self._load()
        if not records:
            return "No due reminders."

        from dateutil import parser as dtp
        now = datetime.now(timezone.utc).astimezone()
        fired_now = []
        changed = False

        for r in records:
            if r.get("fired"):
                continue
            try:
                due = dtp.parse(r["due"])
            except Exception:
                continue
            if due <= now:
                fired_now.append(r)
                if mark_fired:
                    r["fired"] = True
                    r["fired_at"] = now.isoformat()
                    changed = True
                if self.valves.notify and shutil.which("notify-send"):
                    try:
                        subprocess.run(
                            ["notify-send", self.valves.notify_title, r.get("message", "")],
                            timeout=4,
                        )
                    except Exception:
                        pass

        if changed:
            self._save_all(records)

        if not fired_now:
            return "No due reminders."

        out = [f"### {len(fired_now)} reminder(s) fired", ""]
        for r in fired_now:
            out.append(f"- `{r.get('id','?')}` — {r.get('due','?')} — {r.get('message','')}")
        return "\n".join(out)
