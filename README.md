---
title: Wiki Index
created: 2026-04-30T21:55:31.832329+00:00
updated: 2026-04-30T21:55:31.832329+00:00
tags: [home, index]
cssclasses: [wiki-index]
---

# Wiki Index


This vault is the maintained knowledge layer for the machine.

It follows the LLM Wiki pattern:

- raw sources stay immutable outside the wiki
- the wiki stores maintained summaries, mirrors, and analyses
- schema documents in the repo tell the LLM how to keep the wiki consistent

## Index

- [[sources/README|Sources]]
- [[system/README|System]]
- [[user/notes/README|Notes]]
- [[user/projects/README|Projects]]
- [[user/research/README|Research]]
- [[_meta/index|Index]]
- [[_meta/log|Activity log]]

## Operations

- `wiki ingest <file>`
- `wiki ask "question"`
- `wiki lint`
- `wiki search "term"`
- `wiki sync`

## Machine Layer

- [[system/overview|System overview]]
- [[system/config/pacman.conf|pacman.conf mirror]]
- [[system/config/fstab|fstab mirror]]
- [[_meta/recent|Recently changed]]

## Project Layer

- [[user/projects/wiki-linux|Wiki-OS project]]

## Quick Commands

```bash
wiki bootstrap
wiki ingest ~/wiki-sources/inbox/example.md
wiki ask "What does my pacman.conf do?"
wiki lint
wiki search "gpu"
wiki fix "pacman keyring errors during update"
```

## Viewers

- This vault can be browsed in Obsidian, terminal markdown tools, or any editor.
- The viewer is optional; the maintained markdown artifact is the core product.

## Operating Model

- Real config files stay in `/etc`.
- Raw sources stay in `~/wiki-sources`.
- This wiki stores the persistent synthesis and mirrors.
- The monitor updates mirrors when tracked files change.
- Ingest and query results can be filed back into the wiki.
- Git keeps the full history of machine knowledge.
