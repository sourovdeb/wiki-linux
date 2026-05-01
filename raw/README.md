---
title: Raw Sources (Layer 1)
created: 2026-05-02
tags: [meta, raw, layer-1]
---

# Raw Sources — Layer 1

> **Drop original documents here.** PDFs, articles, papers, transcripts, plain
> text — anything you read or want the wiki to reason about.
>
> **The wiki maintainer never edits files in this folder.** They are immutable
> source-of-truth. The LLM reads them and writes synthesised pages into
> [system/](../system/), [user/](../user/), and [_meta/](../_meta/).

## How to use it

1. Drop a file in here (or use `wiki ingest <path>` from anywhere on disk).
2. The daemon picks it up, reads the first 8 KB, and writes a wiki page.
3. The wiki page links back to the file in `raw/` via a `source:` frontmatter
   field, so every claim in the wiki is traceable to its origin.

## What lives here

- One subfolder per topic, project, or source category is fine.
- Filenames: keep them descriptive. `2026-04-12-arch-fstab-explainer.pdf` is
  better than `paper.pdf`.
- Never move or rename a raw file by hand once it's been ingested — wiki pages
  cite it by path.

## Three-layer architecture (Karpathy)

```
LAYER 1 — RAW (this folder, immutable) ──┐
                                          │
LAYER 2 — WIKI (LLM-managed Markdown)  ◀──┘  reads → writes
            system/, user/, _meta/

LAYER 3 — SCHEMA (CLAUDE.md + AGENTS.md)
            tells the LLM HOW to maintain layer 2
```
