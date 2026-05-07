"""
llm_helper.py — Ollama SLM integration for email personalisation and post rewriting.
Uses the same pattern as src/llm.py in wiki-linux.
"""

import asyncio
import json
import logging
import urllib.request
from pathlib import Path

log = logging.getLogger("llm_helper")
OLLAMA_BASE = "http://127.0.0.1:11434"
DEFAULT_MODEL = "mistral:latest"


def _ollama_generate_sync(prompt: str, model: str = DEFAULT_MODEL, system: str = "") -> str:
    """Synchronous Ollama call."""
    body = {"model": model, "prompt": prompt, "stream": False}
    if system:
        body["system"] = system
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result.get("response", "").strip()
    except Exception as e:
        log.error("Ollama error: %s", e)
        return ""


async def personalise_email_body(template: str, recipient: str, model: str = DEFAULT_MODEL) -> str:
    """
    Use Ollama to personalise an email body template for a specific recipient.
    Runs in a thread to avoid blocking the async event loop.
    """
    system = (
        "You are a professional email writer. "
        "Personalise the given email template slightly for the recipient. "
        "Keep the same length and tone. Return only the email body text, no subject line."
    )
    prompt = f"Recipient: {recipient}\n\nTemplate:\n{template}\n\nPersonalised version:"
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _ollama_generate_sync, prompt, model, system)
    return result or template  # Fall back to original template if LLM fails


async def rewrite_with_ollama(content: str, style: str = "professional social media post", model: str = DEFAULT_MODEL) -> str:
    """Rewrite content in a given style."""
    system = f"You are a professional content writer. Rewrite the given text as a {style}. Keep key facts. Return only the rewritten text."
    prompt = f"Original:\n{content}\n\nRewritten:"
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _ollama_generate_sync, prompt, model, system)
    return result or content


async def analyse_recordings(recordings: list[dict], model: str = DEFAULT_MODEL) -> str:
    """
    Feed activity recordings to Ollama to extract better selectors and patterns.
    Returns insights as formatted text.
    """
    if not recordings:
        return "No recordings provided."

    # Build a summary of the most common actions per platform
    summary_lines = []
    by_platform: dict[str, list] = {}
    for rec in recordings:
        p = rec.get("platform", "unknown")
        by_platform.setdefault(p, []).extend(rec.get("actions", []))

    for platform, actions in by_platform.items():
        clicks = [a for a in actions if a["type"] == "click"]
        inputs = [a for a in actions if a["type"] == "input"]
        summary_lines.append(
            f"Platform: {platform}\n"
            f"  Total actions: {len(actions)}\n"
            f"  Clicks: {len(clicks)}\n"
            f"  Inputs: {len(inputs)}\n"
            f"  Most clicked selectors: {[c['selector'] for c in clicks[:5]]}\n"
            f"  Input fields: {[i['selector'] for i in inputs[:3]]}"
        )

    prompt = (
        "Analyse these browser activity recordings and suggest:\n"
        "1. The most reliable CSS selectors to use for automation\n"
        "2. The typical flow sequence for each platform (compose, fill, send)\n"
        "3. Any patterns that suggest how the UI might have changed\n\n"
        "Recordings summary:\n" + "\n".join(summary_lines)
    )

    system = "You are a Playwright automation expert. Be specific and practical."
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _ollama_generate_sync, prompt, model, system)
