"""
src/fix.py — Local troubleshooting assistant for Wiki-OS.

Builds a small retrieval context from configured documentation roots and asks the
local LLM for practical remediation steps grounded in those snippets.
"""
from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from src.config import cfg
from src import llm

log = logging.getLogger("wiki.fix")


def _doc_roots() -> list[Path]:
    roots = [Path(p).expanduser().resolve() for p in cfg.get("fix", {}).get("doc_roots", [])]
    return [p for p in roots if p.exists()]


def _collect_snippets(query: str) -> list[dict]:
    max_snippets = int(cfg.get("fix", {}).get("max_snippets", 8))
    snippet_bytes = int(cfg.get("fix", {}).get("snippet_bytes", 2000))

    snippets: list[dict] = []
    for root in _doc_roots():
        cmd = [
            "rg",
            "--json",
            "--ignore-case",
            query,
            str(root),
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            log.warning("ripgrep failed for %s: %s", root, e)
            continue

        for line in result.stdout.splitlines():
            if len(snippets) >= max_snippets:
                return snippets
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "match":
                continue

            data = obj.get("data", {})
            text = data.get("lines", {}).get("text", "")
            if not text:
                continue

            snippets.append(
                {
                    "file": data.get("path", {}).get("text", "unknown"),
                    "line": data.get("line_number", 0),
                    "text": text[:snippet_bytes].rstrip(),
                }
            )

    return snippets


def suggest_fix(problem: str) -> str:
    snippets = _collect_snippets(problem)
    if not snippets:
        return "No relevant local snippets found. Try a broader query or verify doc roots in config.json."

    question = (
        "You are a Linux troubleshooting assistant. Use only the snippets provided. "
        "Give a short diagnosis, then ordered remediation steps, then verification commands. "
        f"Problem: {problem}"
    )
    return llm.answer_question(question, snippets)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python3 -m src.fix '<problem description>'")
        raise SystemExit(1)

    print(suggest_fix(" ".join(sys.argv[1:])))
