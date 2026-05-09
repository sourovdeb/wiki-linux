"""
title: Wiki Search
author: wiki-linux
version: 1.2.0
description: Full-text search of ~/wiki via ripgrep, optional Ollama answer synthesis.
required_open_webui_version: 0.4.0
requirements:
licence: MIT
"""

import json
import shutil
import subprocess
import urllib.request
from pathlib import Path

from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        wiki_root: str = Field(
            default=str(Path.home() / "wiki"),
            description="Absolute path to the wiki vault.",
        )
        ollama_base: str = Field(
            default="http://127.0.0.1:11434",
            description="Ollama HTTP endpoint.",
        )
        model: str = Field(
            default="llama3.2:3b",
            description="Ollama model used when answer_with_llm=True.",
        )
        max_snippets: int = Field(default=10, description="Hard cap on snippets returned.")
        timeout_s: int = Field(default=10, description="ripgrep timeout in seconds.")

    def __init__(self):
        self.valves = self.Valves()

    async def search_wiki(self, query: str, answer_with_llm: bool = False) -> str:
        """
        Search ~/wiki for a query and return matching Markdown snippets.

        :param query: Plain-text search query (case-insensitive).
        :param answer_with_llm: If True, send top snippets to Ollama for a synthesised answer.
        :return: Markdown-formatted results, or an error string starting with "Error:".
        """
        wiki_root = Path(self.valves.wiki_root).expanduser().resolve()
        if not wiki_root.is_dir():
            return f"Error: wiki_root not found: {wiki_root}"
        if shutil.which("rg") is None:
            return "Error: ripgrep (`rg`) is not installed."
        if not query.strip():
            return "Error: empty query."

        cmd = [
            "rg", "--json", "--ignore-case",
            "--context=2", "--type", "md",
            "--max-count=3",
            "--", query, str(wiki_root),
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.valves.timeout_s
            )
        except subprocess.TimeoutExpired:
            return "Error: search timed out."

        snippets = []
        for line in result.stdout.splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "match":
                continue
            data = obj["data"]
            rel = data["path"]["text"].replace(str(wiki_root) + "/", "")
            line_num = data["line_number"]
            text = data["lines"]["text"].strip()
            snippets.append(f"**{rel}:{line_num}** — {text}")
            if len(snippets) >= self.valves.max_snippets:
                break

        if not snippets:
            return f"No results found for: `{query}`"

        out = [f"### Wiki search: `{query}`", ""] + snippets

        if answer_with_llm:
            context = "\n".join(snippets[:6])
            prompt = (
                f"Answer concisely using only these wiki notes. "
                f"Cite as [file.md:line].\n\nQuestion: {query}\n\nNotes:\n{context}"
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
                with urllib.request.urlopen(req, timeout=60) as r:
                    resp = json.loads(r.read())
                out += ["", "### Synthesised answer", resp.get("response", "").strip()]
            except Exception as e:
                out += ["", f"_LLM synthesis failed: {e}_"]

        return "\n\n".join(out)
