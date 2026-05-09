---
title: File Find + Summarise
slug: findfile
description: Find files under ~/wiki (or any home subdir), list with sizes, summarise the largest.
---

Use `file_finder` with the pattern and root below.

Output:
1. Markdown table of matches: relative path, size, modified date.
2. If the largest match is a text/markdown/code file, summarise it in ≤ 6 bullets. Otherwise note the type and stop.

The tool jails to `$HOME` already — confirm the boundary to the user if `root` is suspicious.

PATTERN: {{pattern}}
ROOT (optional, default ~/wiki): {{root}}
