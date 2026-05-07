"""
title: Content Drafts
author: wiki-linux
version: 1.0.0
description: Save marketing/social content drafts to the wiki, organised by platform, with frontmatter. List existing drafts.
"""
import re
from datetime import datetime
from pathlib import Path


class Tools:
    def __init__(self):
        self.wiki_root = Path.home() / "Documents/wiki-linux/wiki-linux"
        self.content_dir = self.wiki_root / "content"
        # Whitelisted platforms — keeps the folder structure clean
        self.platforms = {
            "twitter", "x", "linkedin", "instagram", "facebook",
            "blog", "newsletter", "email", "ad", "landing",
            "youtube", "tiktok", "threads", "mastodon", "bluesky",
            "product", "general",
        }

    def save_draft(
        self,
        platform: str,
        title: str,
        content: str,
        tags: str = "",
    ) -> str:
        """
        Save a content draft to ~/Documents/wiki-linux/wiki-linux/content/<platform>/.
        File is timestamped to allow multiple drafts with the same title.

        :param platform: Platform name (twitter, linkedin, blog, email, ad, etc.).
        :param title: Short title — used in filename and front-matter.
        :param content: The full content body.
        :param tags: Optional comma-separated tags.
        :return: Confirmation with saved path, or an error.
        """
        if not platform or not title or not content:
            return "Error: platform, title, and content are all required."

        plat = platform.lower().strip()
        if plat not in self.platforms:
            plat = "general"

        target_dir = self.content_dir / plat
        target_dir.mkdir(parents=True, exist_ok=True)

        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
        if not slug:
            slug = "draft"
        ts = datetime.now().strftime("%Y-%m-%d-%H%M")
        path = target_dir / f"{ts}-{slug}.md"

        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
        front = (
            f"---\n"
            f"platform: {plat}\n"
            f"title: {title}\n"
            f"created: {datetime.now().isoformat(timespec='minutes')}\n"
            f"tags: [{', '.join(tag_list)}]\n"
            f"word_count: {len(content.split())}\n"
            f"char_count: {len(content)}\n"
            f"---\n\n"
            f"# {title}\n\n"
            f"{content.strip()}\n"
        )
        try:
            path.write_text(front, encoding="utf-8")
        except OSError as e:
            return f"Error saving: {e}"
        rel = path.relative_to(self.wiki_root)
        return (
            f"Saved `{rel}` "
            f"({len(content.split())} words, {len(content)} chars)."
        )

    def list_drafts(self, platform: str = "", limit: int = 20) -> str:
        """
        List recent content drafts, optionally filtered by platform.

        :param platform: Platform name to filter by, or empty for all platforms.
        :param limit: Max number of drafts to list (default 20, max 100).
        :return: Markdown list of drafts (newest first), or a message if none.
        """
        limit = max(1, min(int(limit), 100))

        if platform:
            plat = platform.lower().strip()
            if plat not in self.platforms:
                return f"Error: unknown platform `{plat}`."
            search_dirs = [self.content_dir / plat]
        else:
            search_dirs = (
                [d for d in self.content_dir.iterdir() if d.is_dir()]
                if self.content_dir.exists() else []
            )

        files = []
        for d in search_dirs:
            if d.exists():
                files.extend(d.glob("*.md"))

        if not files:
            return "No drafts found."

        # Sort newest first
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        files = files[:limit]

        lines = [f"### Recent drafts ({len(files)})\n"]
        for f in files:
            rel = f.relative_to(self.wiki_root)
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            lines.append(f"- `{rel}` — _{mtime}_")
        return "\n".join(lines)
