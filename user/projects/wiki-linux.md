---
title: Wiki-OS Project
created: 2026-04-30T21:55:31.832920+00:00
updated: 2026-04-30T21:55:31.832920+00:00
tags: [project, wiki-os]
cssclasses: [wiki-space]
---

# Wiki-OS Project


This page tracks the core Wiki-OS project that powers the local wiki layer.

## Paths

- Workspace root: `/home/sourov/Documents/wiki-linux`
- Repo root: `/home/sourov/Documents/wiki-linux/wiki-linux`

## Important Files

- `README.md`
- `ARCHITECTURE.md`
- `USER_GUIDE.md`
- `WIKI_SCHEMA.md`
- `AGENTS.md`
- `src/`
- `systemd/`

## Commands

```bash
cd /home/sourov/Documents/wiki-linux/wiki-linux
PYTHONPATH=. pytest tests/ -q
./bin/wiki bootstrap
systemctl --user status wiki-monitor.service --no-pager
```

## Notes

- This project remains user-space only.
- `/etc` stays canonical.
- `~/wiki-sources` stays immutable.
- The vault is the maintained artifact between the human and raw sources.
