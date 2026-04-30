---
title: Wiki Index
created: 2026-04-30T21:32:57.273856+00:00
updated: 2026-04-30T21:32:57.273856+00:00
tags: [home, index]
cssclasses: [wiki-index]
---

# Wiki Index


This vault is the working knowledge layer for this Arch Linux machine.

## Index

- [[system/README|System]]
- [[user/notes/README|Notes]]
- [[user/projects/README|Projects]]
- [[user/research/README|Research]]
- [[_meta/index|Index]]

## Machine

- [[system/overview|System overview]]
- [[system/config/pacman.conf|pacman.conf mirror]]
- [[system/config/fstab|fstab mirror]]
- [[_meta/recent|Recently changed]]

## Project

- [[user/projects/wiki-linux|Wiki-OS project]]

## Quick Commands

```bash
wiki bootstrap
wiki ask "What does my pacman.conf do?"
wiki fix "pacman keyring errors during update"
wiki search "gpu"
wiki reprocess /etc/pacman.conf
```

## Obsidian

- Vault path: `~/wiki`
- CSS snippet: `.obsidian/snippets/wiki-os-vault.css`
- Enable it once in Appearance -> CSS snippets

## Operating Model

- Real config files stay in `/etc`.
- This wiki documents them as markdown.
- The monitor updates mirrors when tracked files change.
- Git keeps the full history of your machine knowledge.
