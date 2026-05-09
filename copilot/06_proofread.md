---
title: Proofread (Diff Output)
slug: proof
description: Proofread text and return only the changes.
---

Proofread the text below for grammar, spelling, punctuation, and obvious clarity issues. **Do not rewrite for style** unless `mode = rewrite`.

Output a numbered list. Each line:
`N. <original phrase> → <corrected phrase>  // reason in ≤ 6 words`

Then a single line: `Net changes: N`. If the text is clean, say so and stop.

MODE (default = light, options: light | rewrite): {{mode}}
TEXT:
{{text}}
