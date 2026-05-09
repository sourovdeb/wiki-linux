---
title: Wiki Research + Cited Answer
slug: wikiq
description: Search ~/wiki and synthesise a cited answer.
---

Call `wiki_search` with the query below. Synthesise an answer (≤ 200 words) grounded only in returned snippets.

Rules:
- Cite every claim inline as `[file.md:line]` using snippet headers.
- If snippets disagree, surface the disagreement instead of picking one.
- If nothing relevant is found, say so plainly and propose 2 search-term variations.

Question: {{query}}
Depth (optional, default 10): {{depth}}
