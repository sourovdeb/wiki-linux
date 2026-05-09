"""
title: Web Search (DuckDuckGo)
author: wiki-linux
version: 1.0.0
description: Free web search via DuckDuckGo HTML endpoint. Returns title/URL/snippet.
required_open_webui_version: 0.4.0
requirements: httpx, selectolax
licence: MIT
"""

from typing import Optional
import httpx
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        timeout_s: int = Field(default=15, description="HTTP timeout.")
        max_results: int = Field(default=8, description="Cap on returned hits.")
        region: str = Field(default="wt-wt", description="DDG region code, e.g. us-en, uk-en, wt-wt.")
        user_agent: str = Field(
            default="Mozilla/5.0 (wiki-linux web_search)",
            description="HTTP User-Agent.",
        )
        wiki_root: str = Field(
            default="/home/sourov/Documents/wiki-linux/wiki-linux",  # Updated path
            description="Absolute path to the wiki vault.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def search(self, query: str, max_results: Optional[int] = None) -> str:
        """
        Web-search the query and return ranked results.

        :param query: Search terms.
        :param max_results: Override valve cap (clamped to valve max).
        :return: Markdown list of `title — url\\nsnippet`.
        """
        if not query.strip():
            return "Error: empty query."
        n = min(max_results or self.valves.max_results, self.valves.max_results)

        url = "https://html.duckduckgo.com/html/"
        try:
            async with httpx.AsyncClient(
                timeout=self.valves.timeout_s,
                headers={"User-Agent": self.valves.user_agent},
                follow_redirects=True,
            ) as client:
                r = await client.post(url, data={"q": query, "kl": self.valves.region})
                r.raise_for_status()
                html = r.text
        except Exception as e:
            return f"Error: search request failed: {e}"

        try:
            from selectolax.parser import HTMLParser
        except ImportError:
            return "Error: selectolax not installed."

        tree = HTMLParser(html)
        hits = []
        for node in tree.css("div.result"):
            a = node.css_first("a.result__a")
            sn = node.css_first("a.result__snippet") or node.css_first(".result__snippet")
            if not a:
                continue
            title = a.text(strip=True)
            href = a.attributes.get("href", "")
            snippet = sn.text(strip=True) if sn else ""
            if title and href:
                hits.append((title, href, snippet))
            if len(hits) >= n:
                break

        if not hits:
            return f"No results for: `{query}`."

        out = [f"### Results for `{query}`", ""]
        for i, (t, u, s) in enumerate(hits, 1):
            out.append(f"{i}. **{t}** — {u}\n   {s}")
        return "\n".join(out)
