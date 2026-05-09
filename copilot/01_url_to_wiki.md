---
title: URL → Wiki + Bullet Summary
slug: url2wiki
description: Fetch a URL, save clean Markdown to wiki/converted/ for wiki_ingestor, and bullet-summarise.
---

Use `url_to_wiki` to fetch the URL, convert it to clean Markdown, and save it under the wiki `converted/` directory so wiki_ingestor picks it up on its next cycle. Use `slug` if given, otherwise let the tool derive it from the page title.

After saving, output:
1. The full saved path.
2. A bullet summary of the main points (5–8 bullets, one line each).
3. Three follow-up questions worth investigating.

Refuse and say so if the URL is not http(s) or the fetch fails.

URL: {{url}}
SLUG (optional): {{slug}}
