---
title: Last Session Recap
slug: recap
description: Read latest reports in _meta/reports/ and recap the previous session.
---

Call `session_report` with `since_hours = {{since}}` (default 24). It returns the most recent diagnostic / boot-check / audit reports.

Then produce:
1. **Last activity** — one sentence: when, what, outcome.
2. **State now** — bullets on services, ports, model count, git pending, anything failing.
3. **Deltas** — what changed vs the prior report (if more than one is returned).
4. **Action queue** — up to 3 concrete next steps. If everything is green, say so.

If no reports exist, say so plainly and suggest running `WIKI-TOOLS/handoff/15-wiki-linux-diagnostic.sh`.

SINCE_HOURS (optional, default 24): {{since}}
