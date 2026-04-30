"""
src/search.py — Ripgrep + RAG search for Wiki-OS.

Plain ripgrep gives sub-second full-text search across the entire wiki and
handles the vast majority of "where did I write about X" lookups. The
answer_question() function adds one more step: it takes the top ripgrep
snippets and feeds them to the local LLM as context, enabling natural-language
Q&A that is grounded in actual wiki content rather than the model's training
data. Because the model only sees the retrieved snippets, it cannot hallucinate
content that is not in your wiki.

This pattern is called Retrieval-Augmented Generation (RAG). The retrieval
step is ripgrep; the generation step is Ollama.
"""
from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from src.config import cfg
from src import llm

log = logging.getLogger("wiki.search")


def search(query: str, wiki_root: Path | None = None) -> list[dict]:
    """
    Run ripgrep with the given query against the wiki root and return a list
    of snippet dicts. Each dict has keys: "file" (str), "line" (int), "text" (str).

    ripgrep is called with --json so output is structured and unambiguous.
    Context lines around each match are included so the LLM has enough
    surrounding text to answer questions accurately.
    """
    if wiki_root is None:
        wiki_root = Path(cfg["wiki"]["root"])

    max_snippets = cfg.get("search", {}).get("max_snippets", 10)
    context_lines = cfg.get("search", {}).get("snippet_context_lines", 2)

    cmd = [
        "rg",
        "--json",
        "--ignore-case",
        f"--context={context_lines}",
        "--type", "md",
        query,
        str(wiki_root),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log.error("ripgrep failed: %s", e)
        return []

    snippets = []
    current_match: dict | None = None

    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg_type = obj.get("type")

        if msg_type == "match":
            data = obj.get("data", {})
            path = data.get("path", {}).get("text", "unknown")
            line_no = data.get("line_number", 0)
            text = data.get("lines", {}).get("text", "").rstrip()
            snippets.append({
                "file": path,
                "line": line_no,
                "text": text,
            })

        elif msg_type == "context":
            # Append context lines to the most recent snippet's text.
            if snippets:
                ctx = obj.get("data", {}).get("lines", {}).get("text", "").rstrip()
                if ctx:
                    snippets[-1]["text"] += "\n" + ctx

        if len(snippets) >= max_snippets:
            break

    return snippets


def answer_question(question: str, wiki_root: Path | None = None) -> str:
    """
    Answer a natural-language question by searching the wiki with ripgrep
    and then asking the LLM to synthesize an answer from the found snippets.

    This is the backend for `wiki ask "<question>"`.
    """
    if wiki_root is None:
        wiki_root = Path(cfg["wiki"]["root"])

    # Use key words from the question as the ripgrep query.
    # A simple heuristic: take non-stopword words of length > 3.
    stopwords = {"what", "does", "this", "that", "with", "from", "have",
                 "will", "should", "about", "which", "where", "when", "how"}
    words = [w for w in question.lower().split()
             if len(w) > 3 and w not in stopwords]
    rg_query = " ".join(words[:5]) if words else question

    log.info("Searching wiki for: %s", rg_query)
    snippets = search(rg_query, wiki_root)
    log.info("Found %d snippets, passing to LLM.", len(snippets))

    return llm.answer_question(question, snippets)


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    if len(sys.argv) < 2:
        print("Usage: python3 -m src.search '<question>'")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    answer = answer_question(question)
    print(answer)
