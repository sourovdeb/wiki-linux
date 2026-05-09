"""
title: Brainstorm
author: wiki-linux
version: 1.0.0
description: Wiki-grounded brainstorming. Pulls related notes from ~/wiki via ripgrep, then asks Ollama for ideas.
required_open_webui_version: 0.4.0
requirements:
licence: MIT
"""

import json
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        wiki_root: str = Field(
            default=str(Path.home() / "wiki"),
            description="Wiki vault to ground ideas in.",
        )
        ollama_base: str = Field(
            default="http://127.0.0.1:11434", description="Ollama HTTP endpoint."
        )
        model: str = Field(
            default="mistral",
            description="Generation model. Larger/creative models work better here.",
        )
        max_context_snippets: int = Field(
            default=8, description="How many wiki snippets to feed the model as grounding."
        )
        rg_timeout_s: int = Field(default=8, description="ripgrep timeout.")
        llm_timeout_s: int = Field(default=120, description="Ollama generate timeout.")

    def __init__(self):
        self.valves = self.Valves()

    def _gather_context(self, topic: str) -> list:
        wiki_root = Path(self.valves.wiki_root).expanduser().resolve()
        if not wiki_root.is_dir() or shutil.which("rg") is None:
            return []
        # Pick the 2 most distinctive words as the rg query so we don't over-restrict.
        words = [w for w in topic.split() if len(w) > 3][:2] or topic.split()[:2]
        query = " ".join(words) if words else topic
        cmd = [
            "rg", "--json", "--ignore-case", "--type", "md",
            "--max-count=2", "--context=1",
            "--", query, str(wiki_root),
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=self.valves.rg_timeout_s)
        except subprocess.TimeoutExpired:
            return []
        snippets = []
        for line in r.stdout.splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "match":
                continue
            data = obj["data"]
            rel = data["path"]["text"].replace(str(wiki_root) + "/", "")
            ln = data["line_number"]
            text = data["lines"]["text"].strip()
            snippets.append(f"[{rel}:{ln}] {text}")
            if len(snippets) >= self.valves.max_context_snippets:
                break
        return snippets

    async def brainstorm(
        self,
        topic: str,
        constraints: Optional[str] = None,
        n_ideas: int = 10,
    ) -> str:
        """
        Generate brainstorming ideas grounded in the local wiki.

        :param topic: What to brainstorm about.
        :param constraints: Optional constraints (e.g. "local-first, no cloud, weekend project").
        :param n_ideas: Target number of ideas (default 10).
        :return: Markdown — wiki snippets used + numbered idea list from Ollama.
        """
        if not topic.strip():
            return "Error: empty topic."
        n = max(3, min(int(n_ideas), 30))

        snippets = self._gather_context(topic)
        ctx_block = "\n".join(snippets) if snippets else "(no wiki snippets matched)"

        prompt = (
            f"You are brainstorming for a local-first wiki-linux user.\n"
            f"Topic: {topic}\n"
            f"Constraints: {constraints or 'none'}\n\n"
            f"Wiki context (cite as [file.md:line] when an idea was inspired by one):\n"
            f"{ctx_block}\n\n"
            f"Produce {n} distinct ideas. Each idea: one short line, no preamble. "
            f"Number them 1..{n}. Bias toward novelty AND feasibility on Linux + Ollama. "
            f"After the list, add one wildcard idea on a line starting with 'Wildcard:'."
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
            with urllib.request.urlopen(req, timeout=self.valves.llm_timeout_s) as r:
                resp = json.loads(r.read())
            ideas = resp.get("response", "").strip() or "_(empty response)_"
        except Exception as e:
            return f"Error: Ollama generate failed: {e}"

        out = [f"### Brainstorm — {topic}", ""]
        if constraints:
            out += [f"_Constraints: {constraints}_", ""]
        if snippets:
            out += ["**Wiki context used:**"]
            out += [f"- {s}" for s in snippets]
            out += [""]
        else:
            out += ["_No wiki snippets matched — ideas are unground._", ""]
        out += ["**Ideas:**", ideas]
        return "\n".join(out)
