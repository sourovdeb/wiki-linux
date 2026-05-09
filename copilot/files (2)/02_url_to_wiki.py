"""
title: URL to Wiki
author: wiki-linux
version: 1.1.0
description: Fetch HTTP(S) URL, convert to Markdown, save under ~/wiki/converted/ for wiki_ingestor pickup.
required_open_webui_version: 0.4.0
requirements: httpx, trafilatura, markdownify
licence: MIT
"""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, Field


def _slugify(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
    s = re.sub(r"[-\s]+", "-", s)
    return s[:80] or "untitled"


class Tools:
    class Valves(BaseModel):
        wiki_root: str = Field(
            default=str(Path.home() / "wiki"),
            description="Absolute path to the wiki vault.",
        )
        subdir: str = Field(
            default="converted",
            description="Subdirectory under wiki_root (default matches wiki_ingestor watch folder).",
        )
        timeout_s: int = Field(default=20, description="HTTP timeout in seconds.")
        max_bytes: int = Field(default=2_000_000, description="Refuse pages larger than this.")
        user_agent: str = Field(
            default="Mozilla/5.0 (wiki-linux url_to_wiki)",
            description="HTTP User-Agent.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def fetch_to_wiki(
        self,
        url: str,
        slug: Optional[str] = None,
        overwrite: bool = False,
    ) -> str:
        """
        Fetch a web page and save it as Markdown in the wiki for wiki_ingestor.

        :param url: Full http:// or https:// URL.
        :param slug: Optional filename without .md (else derived from page title).
        :param overwrite: If False, refuse to overwrite an existing file.
        :return: Status message including saved path and a short preview.
        """
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return "Error: URL must be http or https."

        try:
            async with httpx.AsyncClient(
                timeout=self.valves.timeout_s,
                headers={"User-Agent": self.valves.user_agent},
                follow_redirects=True,
            ) as client:
                r = await client.get(url)
                r.raise_for_status()
                if len(r.content) > self.valves.max_bytes:
                    return f"Error: page too large ({len(r.content)} bytes)."
                html = r.text
        except Exception as e:
            return f"Error fetching URL: {e}"

        title = url
        body_md = ""
        try:
            import trafilatura
            extracted = trafilatura.extract(
                html, output_format="markdown", include_links=True, include_images=False
            )
            meta = trafilatura.extract_metadata(html)
            if meta and meta.title:
                title = meta.title
            if extracted:
                body_md = extracted
        except Exception:
            pass

        if not body_md:
            try:
                from markdownify import markdownify
                body_md = markdownify(html, heading_style="ATX")
            except Exception as e:
                return f"Error: no extractor available ({e}). Install trafilatura or markdownify."

        wiki_root = Path(self.valves.wiki_root).expanduser().resolve()
        target_dir = (wiki_root / self.valves.subdir).resolve()
        try:
            target_dir.relative_to(wiki_root)
        except ValueError:
            return "Error: subdir escapes wiki_root."
        target_dir.mkdir(parents=True, exist_ok=True)

        name = _slugify(slug) if slug else _slugify(title)
        path = target_dir / f"{name}.md"
        if path.exists() and not overwrite:
            return f"Error: file exists at {path}. Pass overwrite=True to replace."

        from datetime import datetime, timezone
        front = (
            f"---\n"
            f'title: "{title}"\n'
            f'url: "{url}"\n'
            f'date: "{datetime.now(timezone.utc).isoformat()}"\n'
            f'source: "openwebui-url_to_wiki"\n'
            f"tags: [web-capture, openwebui]\n"
            f"---\n\n"
            f"# {title}\n\n"
            f"_Source: <{url}>_\n\n"
        )
        path.write_text(front + body_md, encoding="utf-8")

        preview = (body_md[:400] + "…") if len(body_md) > 400 else body_md
        return f"Saved: {path}\n\n--- preview ---\n{preview}"
