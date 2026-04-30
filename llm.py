"""
src/llm.py — Ollama API wrapper for Wiki-OS.

All LLM interaction goes through this module. The Ollama Python client is used
exclusively; subprocess calls to the `ollama` binary are never made. Every call
uses format="json" so the model is instructed to return machine-parseable output
rather than prose, which makes the daemon's behaviour deterministic.

The SYSTEM_PROMPT is deliberately short. Small models (Mistral 7B, Llama 3.2 3B)
lose instruction-following quality as system prompts grow longer. Keep it tight.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import ollama

from src.config import cfg

log = logging.getLogger("wiki.llm")

# The schema the model must follow. Documented in the prompt so the model
# understands the purpose of each field, not just the names.
SYSTEM_PROMPT = """You are a personal wiki page generator for a technical Linux user.

Given a source file path and its contents, return a JSON object with exactly
these keys:
  "target_path": relative path under the wiki root, e.g. "system/config/pacman.conf.md"
  "title":       short human-readable page title
  "content":     complete Markdown page including YAML frontmatter (see format below)
  "links":       list of related wiki page paths this page should cross-link to

Markdown page format:
---
title: <title>
source: <absolute source path>
updated: <ISO 8601 timestamp>
tags: [system, config]
---

## What This File Does
<one paragraph factual explanation for a Linux user>

## Contents
```
<verbatim file contents>
```

## Related
<[[wikilink]] list, one per line>

Rules:
- Never invent paths or facts not present in the source file.
- target_path must be relative (no leading slash).
- target_path must end in .md.
- Never produce target_path outside system/ or user/ subtrees.
- Return only the JSON object. No preamble, no explanation."""


def generate_wiki_page(
    source_path: Path,
    wiki_root: Path,
    timestamp: str,
) -> dict | None:
    """
    Ask Ollama to generate a wiki page for the given source file.

    Returns a validated dict with keys target_path, title, content, links,
    or None if the LLM call or validation failed. The caller is responsible
    for the actual file write so that self-write suppression can be applied.
    """
    # --- Read and truncate source file ---
    limit = cfg.get("ollama", {}).get("context_limit_bytes", 8000)
    try:
        raw = source_path.read_text(errors="replace")
    except (OSError, PermissionError) as e:
        log.warning("Cannot read %s: %s", source_path, e)
        return None

    if len(raw) > limit:
        log.info("Truncating %s from %d to %d bytes", source_path, len(raw), limit)
        raw = raw[:limit] + "\n... [truncated]"

    # --- Build prompt ---
    prompt = (
        f"Source file: {source_path}\n"
        f"Timestamp: {timestamp}\n\n"
        f"Contents:\n{raw}"
    )

    # --- Call Ollama ---
    model = cfg.get("ollama", {}).get("model", "mistral")
    temperature = cfg.get("ollama", {}).get("temperature", 0.2)
    num_ctx = cfg.get("ollama", {}).get("num_ctx", 4096)
    timeout = cfg.get("ollama", {}).get("timeout_seconds", 30)

    try:
        response = ollama.generate(
            model=model,
            system=SYSTEM_PROMPT,
            prompt=prompt,
            format="json",
            options={"temperature": temperature, "num_ctx": num_ctx},
            stream=False,
        )
    except Exception as e:
        log.error("Ollama call failed for %s: %s", source_path, e)
        return None

    # --- Parse and validate response ---
    try:
        data = json.loads(response["response"])
    except (KeyError, json.JSONDecodeError) as e:
        log.warning("Malformed LLM response for %s: %s", source_path, e)
        return None

    # Validate required keys exist and have the right types.
    if not isinstance(data.get("target_path"), str):
        log.warning("LLM response missing valid target_path for %s", source_path)
        return None
    if not isinstance(data.get("content"), str):
        log.warning("LLM response missing valid content for %s", source_path)
        return None

    # Security: the target path must resolve inside wiki_root.
    try:
        resolved = (wiki_root / data["target_path"]).resolve()
        if not str(resolved).startswith(str(wiki_root.resolve())):
            log.error(
                "LLM returned path escape attempt: %s → %s",
                data["target_path"], resolved,
            )
            return None
    except Exception as e:
        log.error("Path resolution failed for %s: %s", data["target_path"], e)
        return None

    # Ensure the path ends in .md so we never write binary-named files.
    if not data["target_path"].endswith(".md"):
        data["target_path"] += ".md"

    # Default links to an empty list if the model omitted it.
    data.setdefault("links", [])
    data.setdefault("title", source_path.name)

    return data


def answer_question(question: str, snippets: list[dict]) -> str:
    """
    Answer a natural-language question using retrieved wiki snippets (RAG).

    snippets is a list of dicts: {"file": str, "text": str}.
    The model sees only these snippets and cannot hallucinate content
    that is not in the wiki.
    """
    if not snippets:
        return "No relevant content found in the wiki for that question."

    context_parts = []
    for s in snippets:
        context_parts.append(f"[{s['file']}]\n{s['text']}")
    context = "\n\n---\n\n".join(context_parts)

    system = (
        "You answer questions using only the provided wiki excerpts. "
        "Cite the source file in brackets after each fact. "
        "If the answer is not in the excerpts, say so clearly."
    )
    prompt = f"Question: {question}\n\nWiki excerpts:\n{context}"

    model = cfg.get("ollama", {}).get("model", "mistral")
    try:
        response = ollama.generate(
            model=model,
            system=system,
            prompt=prompt,
            stream=False,
        )
        return response.get("response", "No response from model.").strip()
    except Exception as e:
        log.error("Ollama RAG call failed: %s", e)
        return f"LLM error: {e}"
