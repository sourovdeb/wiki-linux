"""
title: Journal & Hotlines
author: wiki-linux
version: 1.0.0
description: Append private journal entries to a separate journal directory (NOT under the public wiki), and look up crisis hotlines by region.
"""
import re
from datetime import datetime
from pathlib import Path


class Tools:
    def __init__(self):
        # Journal lives OUTSIDE the wiki to keep it private and not RAG-indexed.
        self.journal_root = Path.home() / "Documents/journal-private"
        # Crisis hotlines (deliberately conservative; verified mainstream lines).
        # Country codes are ISO 3166-1 alpha-2.
        self.hotlines = {
            "US": ["988 — Suicide & Crisis Lifeline (call or text)",
                   "Text HOME to 741741 — Crisis Text Line"],
            "CA": ["988 — Suicide Crisis Helpline (call or text)"],
            "UK": ["116 123 — Samaritans (free, 24/7)",
                   "Text SHOUT to 85258 — Shout Crisis Text Line"],
            "IE": ["116 123 — Samaritans Ireland"],
            "AU": ["13 11 14 — Lifeline Australia",
                   "1300 22 4636 — Beyond Blue"],
            "NZ": ["1737 — Need to Talk? (call or text)"],
            "FR": ["3114 — Numéro national de prévention du suicide",
                   "01 45 39 40 00 — SOS Amitié"],
            "DE": ["0800 111 0 111 — Telefonseelsorge"],
            "ES": ["024 — Línea de atención a la conducta suicida"],
            "IT": ["02 2327 2327 — Telefono Amico"],
            "NL": ["0800-0113 — 113 Zelfmoordpreventie"],
            "BE": ["1813 — Zelfmoordlijn / Centre de Prévention du Suicide"],
            "JP": ["0570-064-556 — Yorisoi Hotline"],
            "IN": ["9152987821 — iCall (Mon-Sat 8am-10pm)"],
            "ZA": ["0800 567 567 — SADAG Suicide Crisis Line"],
            "RE": ["3114 — Numéro national de prévention du suicide (France)",
                   "0262 90 43 00 — SOS Solitude Réunion"],
        }
        self.global_directory = "https://findahelpline.com"
        self.emergency_note = (
            "If you are in immediate danger, please call your local emergency "
            "number now (112 in EU/Réunion, 911 in US/CA, 999 in UK, 000 in AU)."
        )

    def add_journal_entry(
        self,
        text: str,
        mood: str = "",
        tags: str = "",
    ) -> str:
        """
        Append a journal entry to a private monthly file (NOT under the wiki).
        Each entry is timestamped. Files are organised by month: YYYY-MM.md.

        :param text: The journal entry text.
        :param mood: Optional one-word mood tag (e.g., 'tired', 'anxious', 'ok').
        :param tags: Optional comma-separated tags.
        :return: Confirmation with saved path, or an error.
        """
        if not text or not text.strip():
            return "Error: entry text is empty."

        self.journal_root.mkdir(parents=True, exist_ok=True)
        # Restrict permissions on the journal dir (best effort, POSIX)
        try:
            self.journal_root.chmod(0o700)
        except OSError:
            pass

        now = datetime.now()
        path = self.journal_root / f"{now.strftime('%Y-%m')}.md"

        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
        header_bits = [now.strftime("%Y-%m-%d %H:%M")]
        if mood:
            header_bits.append(f"mood: {mood.strip()}")
        if tag_list:
            header_bits.append(f"tags: {', '.join(tag_list)}")

        entry = (
            f"\n---\n"
            f"## {' — '.join(header_bits)}\n\n"
            f"{text.strip()}\n"
        )
        try:
            with path.open("a", encoding="utf-8") as f:
                f.write(entry)
            try:
                path.chmod(0o600)
            except OSError:
                pass
        except OSError as e:
            return f"Error saving entry: {e}"

        return f"Entry added to private journal ({path.name}, {len(text)} chars)."

    def get_hotlines(self, country_code: str = "") -> str:
        """
        Return mental-health crisis hotlines for a country code, plus the
        global directory and an emergency-services note. Always include the
        global fallback so the response is useful even if the country is unknown.

        :param country_code: ISO 3166-1 alpha-2 code (US, UK, AU, FR, RE, etc.). Empty = global only.
        :return: Markdown block of hotline numbers.
        """
        cc = (country_code or "").upper().strip()
        lines = []

        if cc and cc in self.hotlines:
            lines.append(f"**Crisis lines — {cc}:**")
            for h in self.hotlines[cc]:
                lines.append(f"- {h}")
            lines.append("")
        elif cc:
            lines.append(f"_No specific entry for `{cc}` in the local list._\n")

        lines.append("**Global directory:** " + self.global_directory)
        lines.append("")
        lines.append(self.emergency_note)
        return "\n".join(lines)
