"""
title: Fetch URL to Wiki
author: wiki-linux
version: 1.0.0
description: Fetch a URL, convert it to clean Markdown, and save it as a note in the wiki. Uses trafilatura for robust content extraction with html2text/stdlib fallback.
requirements: trafilatura, html2text
"""
import re
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


class Tools:
    def __init__(self):
        self.wiki_root = Path.home() / "Documents/wiki-linux/wiki-linux"
        self.default_folder = "inbox"
        self.user_agent = "Mozilla/5.0 (compatible; OpenWebUI-Tool/1.0)"
        self.timeout = 15

    def fetch_url_as_markdown(
        self,
        url: str,
        save_as: str = "",
        folder: str = "",
    ) -> str:
        """
        Fetch a URL, extract its main content as Markdown, and save it to the wiki.

        :param url: The full URL to fetch (must start with http:// or https://).
        :param save_as: Optional filename (without .md). If empty, derived from page title.
        :param folder: Subfolder under the wiki root. Defaults to 'inbox'.
        :return: Markdown summary block + saved path, or an error message.
        """
        if not url or not url.startswith(("http://", "https://")):
            return "Error: URL must start with http:// or https://."

        # 1. Fetch
        try:
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                charset = resp.headers.get_content_charset() or "utf-8"
                html = raw.decode(charset, errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            return f"Error fetching URL: {e}"
        except Exception as e:
            return f"Error: {e}"

        # 2. Convert to Markdown (trafilatura → html2text → strip-tags fallback)
        markdown, title = self._html_to_markdown(html, url)
        if not markdown.strip():
            return "Error: page fetched but no content extracted."

        # 3. Determine save path
        folder_name = (folder or self.default_folder).strip("/ ")
        target_dir = self.wiki_root / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        if save_as:
            slug = self._slugify(save_as)
        else:
            slug = self._slugify(title or urlparse(url).netloc)
        ts = datetime.now().strftime("%Y-%m-%d")
        path = target_dir / f"{ts}-{slug}.md"

        # 4. Build front-matter + body
        body = (
            f"---\n"
            f"source: {url}\n"
            f"fetched: {datetime.now().isoformat(timespec='minutes')}\n"
            f"title: {title or '(no title)'}\n"
            f"---\n\n"
            f"# {title or url}\n\n"
            f"{markdown.strip()}\n"
        )
        try:
            path.write_text(body, encoding="utf-8")
        except OSError as e:
            return f"Error writing file: {e}"

        rel = path.relative_to(self.wiki_root)
        return (
            f"Saved `{rel}` ({len(body)} chars).\n"
            f"Source: {urlparse(url).netloc}\n"
            f"Title: {title or '(no title)'}"
        )

    # ---------- helpers ----------

    def _html_to_markdown(self, html: str, url: str):
        """Try trafilatura, then html2text, then a stdlib tag-strip. Returns (markdown, title)."""
        # trafilatura — best content extraction
        try:
            import trafilatura
            md = trafilatura.extract(
                html, output_format="markdown", include_links=True,
                include_images=False, with_metadata=False, url=url,
            )
            meta = trafilatura.extract_metadata(html)
            title = (meta.title if meta else None) or self._extract_title(html)
            if md:
                return md, title
        except ImportError:
            pass
        except Exception:
            pass

        # html2text — second choice
        try:
            import html2text
            h = html2text.HTML2Text()
            h.body_width = 0
            h.ignore_images = True
            return h.handle(html), self._extract_title(html)
        except ImportError:
            pass

        # stdlib fallback — strip tags
        text = re.sub(r"<script.*?</script>", "", html, flags=re.S | re.I)
        text = re.sub(r"<style.*?</style>", "", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text, self._extract_title(html)

    @staticmethod
    def _extract_title(html: str) -> str:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.S | re.I)
        return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

    @staticmethod
    def _slugify(text: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        return slug[:60] or "untitled"
