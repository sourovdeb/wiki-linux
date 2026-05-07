"""
title: Ollama Model Manager
author: wiki-linux
version: 1.0.0
description: List, pull, delete Ollama models and generate text directly from OpenWebUI chat.
"""

import json
import urllib.request
from pathlib import Path


OLLAMA_BASE = "http://127.0.0.1:11434"


def _ollama(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{OLLAMA_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


class Tools:
    def list_models(self) -> str:
        """
        List all locally available Ollama models with their sizes.

        :return: Formatted table of models.
        """
        resp = _ollama("GET", "/api/tags")
        models = resp.get("models", [])
        if not models:
            return "No models found or Ollama not running."
        lines = ["| Model | Size | Modified |", "|-------|------|----------|"]
        for m in models:
            name = m.get("name", "?")
            size = f"{m.get('size', 0) / 1e9:.1f} GB"
            mod = m.get("modified_at", "")[:10]
            lines.append(f"| {name} | {size} | {mod} |")
        return "\n".join(lines)

    def pull_model(self, model_name: str) -> str:
        """
        Pull (download) an Ollama model. This starts the download in the background.

        :param model_name: Model name e.g. 'llama3.2:3b' or 'mistral:latest'.
        :return: Status message.
        """
        import subprocess
        try:
            proc = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            out, _ = proc.communicate(timeout=300)
            if proc.returncode == 0:
                return f"Successfully pulled `{model_name}`."
            return f"Pull failed:\n```\n{out[-500:]}\n```"
        except Exception as e:
            return f"Error: {e}"

    def delete_model(self, model_name: str) -> str:
        """
        Delete a local Ollama model to free disk space.

        :param model_name: Model name to delete e.g. 'tinyllama:latest'.
        :return: Status message.
        """
        resp = _ollama("DELETE", "/api/delete", {"name": model_name})
        if "error" in resp:
            return f"Error deleting `{model_name}`: {resp['error']}"
        return f"Deleted `{model_name}`."

    def generate(self, prompt: str, model: str = "mistral:latest", system: str = "") -> str:
        """
        Generate a response from a local Ollama model.

        :param prompt: The prompt to send.
        :param model: Model to use (default: mistral:latest).
        :param system: Optional system prompt.
        :return: Model response text.
        """
        body: dict = {"model": model, "prompt": prompt, "stream": False}
        if system:
            body["system"] = system
        resp = _ollama("POST", "/api/generate", body)
        if "error" in resp:
            return f"Error: {resp['error']}"
        return resp.get("response", "(empty response)")

    def summarize(self, text: str, model: str = "mistral:latest", style: str = "bullet points") -> str:
        """
        Summarise a block of text using a local Ollama model.

        :param text: Text to summarise (max ~4000 chars for small models).
        :param model: Ollama model to use.
        :param style: Output style e.g. 'bullet points', 'one paragraph', 'key points'.
        :return: Summary text.
        """
        prompt = f"Summarise the following text as {style}:\n\n{text[:4000]}"
        return self.generate(prompt, model=model)
