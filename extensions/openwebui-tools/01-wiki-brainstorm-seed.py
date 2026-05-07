"""
title: Wiki Brainstorm Seed
author: wiki-linux
version: 1.0.0
description: Seed brainstorming with excerpts from existing wiki notes, and save generated idea lists back to the wiki.
"""
import subprocess
import json
import re
from datetime import datetime
from pathlib import Path


class Tools:
    def __init__(self):
        self.wiki_root = Path.home() / "Documents/wiki-linux/wiki-linux"
        self.brainstorm_dir = self.wiki_root / "brainstorms"

    def seed_from_wiki(self, topic: str, count: int = 3) -> str:
        """
        Find existing wiki notes related to a topic and return short excerpts
        as inspiration for brainstorming. Uses ripgrep across all .md files.

        :param topic: The brainstorming topic (any keywords).
        :param count: How many related excerpts to return (default 3, max 10).
        :return: Markdown-formatted excerpts, or a "no related notes" message.
        """
        if not topic or not topic.strip():
            return "Error: topic is empty."
        count = max(1, min(int(count), 10))

        cmd = [
            "rg", "--json", "--ignore-case",
            "--context=1", "--type", "md",
            "--max-count=2",
            topic.strip(), str(self.wiki_root),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "Error: ripgrep not available or timed out."

        excerpts = []
        seen_files = set()
        for line in result.stdout.splitlines():
            try:
                obj = json.loads(line)
                if obj.get("type") != "match":
                    continue
                data = obj["data"]
                path = data["path"]["text"]
                if path in seen_files:
                    continue
                seen_files.add(path)
                rel = path.replace(str(self.wiki_root) + "/", "")
                text = data["lines"]["text"].strip()
                excerpts.append(f"- **{rel}** — {text[:200]}")
                if len(excerpts) >= count:
                    break
            except (json.JSONDecodeError, KeyError):
                continue

        if not excerpts:
            return f"No related notes found for `{topic}`. Generate ideas from scratch."
        return f"### Related notes for `{topic}`\n\n" + "\n".join(excerpts)

    def save_idea_list(self, topic: str, ideas: str) -> str:
        """
        Save a brainstormed idea list as a new markdown note in the wiki.
        File is timestamped to avoid overwrites.

        :param topic: The brainstorming topic — used in filename and header.
        :param ideas: The full idea list as already-formatted markdown.
        :return: Confirmation with the saved path, or an error message.
        """
        if not topic or not ideas:
            return "Error: topic and ideas are both required."

        self.brainstorm_dir.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:60]
        ts = datetime.now().strftime("%Y-%m-%d-%H%M")
        path = self.brainstorm_dir / f"{ts}-{slug}.md"

        content = (
            f"# Brainstorm: {topic}\n\n"
            f"_Generated {datetime.now().isoformat(timespec='minutes')}_\n\n"
            f"{ideas.strip()}\n"
        )
        try:
            path.write_text(content, encoding="utf-8")
        except OSError as e:
            return f"Error saving: {e}"
        rel = path.relative_to(self.wiki_root)
        return f"Saved to `{rel}` ({len(content)} chars)."
