"""
title: Wiki Ingest URL
author: wiki-linux
version: 1.0.0
description: Fetch a URL or local file, convert to Markdown via markitdown, save to wiki user/notes/, optionally sync to KB.
"""

import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path


class Tools:
    def __init__(self):
        self.wiki_root = str(Path.home() / "Documents/wiki-linux/wiki-linux")
        self.venv_python = str(Path.home() / "Documents/wiki-linux/wiki-linux/.venv/bin/python3")

    def ingest_url(self, url: str, save_to: str = "user/notes", sync_kb: bool = True) -> str:
        """
        Fetch a URL and convert it to Markdown, saving it into the wiki.
        Optionally triggers kb-sync to add to the knowledge base.

        :param url: URL to fetch and convert (http/https).
        :param save_to: Subdir under wiki root to save the markdown (default: user/notes).
        :param sync_kb: If True, trigger wiki-kb-sync after saving.
        :return: Status message with the saved file path.
        """
        wiki_root = Path(self.wiki_root)
        out_dir = wiki_root / save_to
        out_dir.mkdir(parents=True, exist_ok=True)

        # Derive a safe filename from the URL
        slug = url.split("//", 1)[-1].replace("/", "_").replace("?", "_")[:80]
        out_path = out_dir / f"{slug}.md"

        # Use markitdown to convert the URL
        try:
            result = subprocess.run(
                [self.venv_python, "-c",
                 f"from markitdown import MarkItDown; m=MarkItDown(); r=m.convert('{url}'); print(r.text_content)"],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0 or not result.stdout.strip():
                return f"Error converting URL: {result.stderr[:300]}"
            content = result.stdout
        except subprocess.TimeoutExpired:
            return "Error: conversion timed out after 60s."
        except Exception as e:
            return f"Error: {e}"

        frontmatter = f"---\nsource: {url}\ntags: [ingested, web]\n---\n\n"
        out_path.write_text(frontmatter + content, encoding="utf-8")

        msg = f"Saved to `{out_path.relative_to(wiki_root)}` ({len(content)} chars)"

        if sync_kb:
            try:
                subprocess.Popen(
                    [str(wiki_root / "bin/wiki-kb-sync")],
                    cwd=str(wiki_root),
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                msg += "\n KB sync triggered in background."
            except Exception as e:
                msg += f"\n KB sync failed: {e}"

        return msg

    def ingest_text(self, title: str, content: str, tags: str = "note", save_to: str = "user/notes") -> str:
        """
        Save raw text/markdown content as a new wiki note.

        :param title: Title for the note (used as filename).
        :param content: Markdown or plain text content.
        :param tags: Comma-separated tags for frontmatter.
        :param save_to: Subdir under wiki root (default: user/notes).
        :return: Path where the note was saved.
        """
        wiki_root = Path(self.wiki_root)
        out_dir = wiki_root / save_to
        out_dir.mkdir(parents=True, exist_ok=True)

        slug = title.lower().replace(" ", "_").replace("/", "-")[:60]
        out_path = out_dir / f"{slug}.md"

        tag_list = ", ".join(f'"{t.strip()}"' for t in tags.split(","))
        frontmatter = f"---\ntitle: {title}\ntags: [{tag_list}]\n---\n\n"
        out_path.write_text(frontmatter + content, encoding="utf-8")

        return f"Saved to `{out_path.relative_to(wiki_root)}`"
