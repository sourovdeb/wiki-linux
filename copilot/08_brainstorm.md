---
title: Wiki-grounded Brainstorm
slug: brain
description: Brainstorm ideas grounded in your wiki notes.
---

Call `brainstorm` with the topic and constraints below. It will pull related context from `~/wiki` via wiki_search and return raw ideas.

Then refine the output to:
1. **10 ideas**, ranked by novelty × feasibility (1 = best). Each ≤ 1 line.
2. **Top 3 expanded**: 2 sentences each, naming the wiki note that inspired it (`[file.md]`) when applicable.
3. **Wildcard**: one deliberately weird idea outside the constraints.

If wiki context is thin (< 3 snippets), say so before listing.

TOPIC: {{topic}}
CONSTRAINTS (optional, e.g. "local-first, no cloud, weekend project"): {{constraints}}
N_IDEAS (optional, default 10): {{n}}
