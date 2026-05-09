# KDE Design Prep

This document prepares the repo for the next design phase, including KDE-oriented work and any follow-up desktop layout changes.

## Purpose

Before making visual or desktop-flow changes, read the existing system documentation in this order:

1. [Start Here](../WIKI-TOOLS/START-HERE.md)
2. [Daily Guide](../WIKI-TOOLS/DAILY-GUIDE.md)
3. [System Space](../system/README.md)
4. [System Architecture](SYSTEM-ARCHITECTURE.md)
5. [Maintenance Guide](../MAINTENANCE-GUIDE.md)
6. [Tiny Maintenance Rules](../MAINTENANCE-RULES-TINY.md)
7. [Simple Maintenance Rules](../MAINTENANCE-RULES-SIMPLE.md)
8. [Cline Handoff](../WIKI-TOOLS/CLINE-HANDOFF.md)

## What to Learn First

- What the wiki root is and what should stay read-only.
- Which services are already active.
- How the wiki monitor, sync timer, and maintenance timer work.
- Which files are safe to touch and which files are off limits.
- Where the OpenWebUI, Ollama, and wiki pages fit into the workflow.

## Safe Design Constraints

- Keep the wiki-first model intact.
- Prefer user-space changes over system-wide changes.
- Do not write to `/etc`, `/usr`, or other system paths.
- Do not add background services unless they are tiny and necessary.
- Keep the desktop fast, readable, and easy to recover.
- Keep cleanup deterministic and reversible.

## KDE-Oriented Checklist

When preparing KDE design work, verify these points first:

- [ ] Disk space is healthy with `df -h /`
- [ ] `wiki-system-maintenance.timer` is active
- [ ] `wiki-monitor` is active
- [ ] `wiki-sync.timer` is active
- [ ] OpenWebUI is running only if needed
- [ ] Ollama model set is as small as possible
- [ ] No duplicate cache or archive files are left behind

## Recommended Read Path for an Agent

1. Read the system overview.
2. Read the maintenance rules.
3. Read the architecture doc.
4. Check the active services.
5. Only then propose any KDE-specific layout or UI work.

## Current Status

- Maintenance timer: active
- Disk headroom: adequate
- OpenWebUI: running
- System docs: organized

## Short Version

Read the docs first, check the services, keep the system safe, and only then start KDE/design work.
