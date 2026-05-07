"""
title: Wiki Search
author: wiki-linux
version: 1.0.0
description: Search the local wiki using ripgrep full-text search with optional RAG answer via Ollama.
"""

import subprocess
import json
from pathlib import Path


class Tools:
    def __init__(self):
        self.wiki_root = str(Path.home() / "Documents/wiki-linux/wiki-linux")
        self.ollama_base = "http://127.0.0.1:11434"
        self.model = "mistral:latest"

    def search_wiki(self, query: str, answer_with_llm: bool = False) -> str:
        """
        Search the wiki for a query. Returns matching snippets from markdown files.
        Optionally uses Ollama to synthesise an answer from the top results.

        :param query: The search query.
        :param answer_with_llm: If True, feed results to Ollama for a synthesised answer.
        :return: Search results as formatted markdown.
        """
        cmd = [
            "rg", "--json", "--ignore-case",
            "--context=2", "--type", "md",
            "--max-count=3",
            query, self.wiki_root
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "Error: ripgrep not available or timed out."

        snippets = []
        for line in result.stdout.splitlines():
            try:
                obj = json.loads(line)
                if obj.get("type") == "match":
                    data = obj["data"]
                    path = data["path"]["text"]
                    line_num = data["line_number"]
                    text = data["lines"]["text"].strip()
                    # Make path relative
                    rel = path.replace(self.wiki_root + "/", "")
                    snippets.append(f"**{rel}:{line_num}** — {text}")
            except Exception:
                continue

        if not snippets:
            return f"No results found for: `{query}`"

        output = f"### Wiki search: `{query}`\n\n" + "\n\n".join(snippets[:10])

        if answer_with_llm and snippets:
            context = "\n".join(snippets[:6])
            prompt = f"Based on these wiki notes, answer concisely: {query}\n\nContext:\n{context}"
            try:
                import urllib.request
                payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
                req = urllib.request.Request(
                    f"{self.ollama_base}/api/generate",
                    data=payload, headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    ans = json.loads(resp.read())
                    output += f"\n\n---\n**Ollama answer:** {ans.get('response','')}"
            except Exception as e:
                output += f"\n\n_(LLM answer failed: {e})_"

        return output

    def get_wiki_stats(self) -> str:
        """
        Return stats about the wiki: file counts, library size, KB sync status.

        :return: Stats as markdown.
        """
        root = Path(self.wiki_root)
        md_count = len(list(root.rglob("*.md")))
        library = root / "user/library"
        lib_count = len(list(library.glob("*.md"))) if library.exists() else 0

        ledger_path = Path.home() / ".local/share/wiki-linux/kb-sync-ledger.json"
        synced = 0
        if ledger_path.exists():
            try:
                synced = len(json.loads(ledger_path.read_text()))
            except Exception:
                pass

        return (
            f"### Wiki Stats\n"
            f"- Total MD files: **{md_count}**\n"
            f"- Library (converted): **{lib_count}**\n"
            f"- KB synced to OpenWebUI: **{synced}**\n"
            f"- Wiki root: `{self.wiki_root}`"
        )
