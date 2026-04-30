---
title: System Overview
created: 2026-04-30T21:36:53.093582+00:00
updated: 2026-04-30T21:36:53.093582+00:00
tags: [system, overview]
---

# System Overview


This page is the top-level operating snapshot for the current machine.

## Core Paths

- Wiki root: `/home/sourov/wiki`
- Config file: `~/.config/wiki-os/config.json`
- Model: `llama3.2:3b`

## Active Layout

- [[system/README|System space]]
- [[user/notes/README|Notes]]
- [[user/projects/README|Projects]]
- [[user/research/README|Research]]

## Watched Paths

- `/home/sourov/wiki`
- `/home/sourov/notes`
- `/home/sourov/wiki`
- `/home/sourov/Documents/wiki-linux`


## Commands

```bash
wiki status
wiki ask "What changed recently?"
wiki fix "wifi broken after update"
journalctl --user -u wiki-monitor -f
```
