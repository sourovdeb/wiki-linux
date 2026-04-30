---
title: System Overview
created: 2026-04-30T21:58:48.661455+00:00
updated: 2026-04-30T21:58:48.661455+00:00
tags: [system, overview]
---

# System Overview


This page is the simplest high-level summary of the current machine setup.

## Core Paths

- Wiki root: `/home/sourov/wiki`
- Raw sources: `/home/sourov/wiki-sources`
- Config file: `~/.config/wiki-os/config.json`
- Model: `llama3.2:3b`

## Active Layout

- [[START-HERE|Start Here]]
- [[sources/README|Sources]]
- [[system/README|System space]]
- [[user/notes/README|Notes]]
- [[user/projects/README|Projects]]
- [[user/research/README|Research]]

## Watched Paths

- `/home/sourov/wiki`
- `/home/sourov/notes`
- `/home/sourov/Documents/wiki-linux`


## Commands

```bash
wiki status
wiki ingest ~/wiki-sources/inbox/example.md
wiki ask "What changed recently?"
wiki lint
wiki fix "wifi broken after update"
journalctl --user -u wiki-monitor -f
```
