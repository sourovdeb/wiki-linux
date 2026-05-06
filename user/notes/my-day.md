---
title: Dashboard
updated: 2026-05-05
tags: [dashboard, daily, quick-reference]
cssclasses: [wiki-space, wiki-dashboard]
---

# Dashboard

This note replaces the empty landing window. Keep it current.

## Todo List

- [ ] Review the previous session report before making changes.
- [ ] Keep Chromium and Chrome-related browser config.
- [ ] Keep Python dependencies, fonts, and essential system tools.
- [ ] Disable autoupdate.
- [ ] Remove everything else that is not on the allowlist.
- [ ] Use Open WebUI for local search and brainstorming.
- [ ] Add or refresh productivity widgets and shortcuts.

## Previous Session Report

Latest tracked work in this repo:
- Dashboard rebuilt from an empty landing note.
- Search/status launchers were restored so the XFCE widget menu is usable.
- Browser and cleanup widgets were added for Chromium, Firefox, Open WebUI, and service trimming.
- A dated session report was recorded for the next login.

Current session record:
- [[_meta/task-log/2026-05-05/220000-dashboard-update|Dashboard update session report]]

See:
- [[_meta/log|Activity log]]
- [[_meta/recent|Recent changes]]
- [[_meta/reports/README|Reports]]
- [[_meta/task-log/2026-04-30/215849-bootstrap|Bootstrap task]]
- [[_meta/task-log/2026-04-30/215602-ingest|Ingest task]]
- [[_meta/task-log/2026-04-30/215603-lint|Lint task]]
- [[_meta/task-log/2026-04-30/215604-doctor|Doctor task]]

## Open WebUI / Ollama

- Open WebUI: http://127.0.0.1:8080
- Launcher: [[WIKI-TOOLS/OLLAMA-CHAT.desktop|Ollama Chat (Open WebUI)]]
- Chromium AI: [[WIKI-TOOLS/7-CHROMIUM-AI.desktop|Chromium AI]]
- Firefox AI: [[WIKI-TOOLS/8-FIREFOX-AI.desktop|Firefox AI]]
- Search box: [[WIKI-TOOLS/1-SEARCH-BOX.desktop|Wiki Search and Ask]]
- When you need local AI, search the wiki first, then ask Ollama.

## How This System Works

The flow is simple:

```text
raw files -> wiki-monitor -> wiki pages -> Obsidian / Open WebUI / git
```

- Raw files land in watched folders and are documented into the wiki.
- `wiki-monitor` watches the system and writes wiki pages.
- Obsidian is the main file browser for the vault.
- Open WebUI is the main chat surface for local LLM use.
- Git sync keeps the vault versioned.

## External AI Access

Folders an external AI (Cline, Claude, Copilot, etc.) **may read**:

| Folder | Purpose |
|---|---|
| `~/wiki/` | Full vault — notes, system docs, projects |
| `~/wiki/raw/` | Layer 1 raw files |
| `~/wiki/system/` | Readable /etc mirrors |
| `~/Documents/wiki-linux/wiki-linux/` | Project source, scripts, launchers |
| `~/.cline/.env` | Shared tool bindings (WIKI_ROOT, OLLAMA_BASE_URL) |

Folders external AI **must not write to**:
- `/etc` — system config, read-only
- `~/wiki/_meta/` — auto-generated, do not edit
- `~/.config/wiki-linux/config.json` — immutable (chmod 444)

AI write is allowed only inside `~/wiki/user/` and `~/wiki/sources/`.

## Keep / Remove Policy

Keep:
- Chromium and Chrome browser integration
- browser-related files in this repo
- Python dependencies
- fonts
- essential system tools
- wiki tooling, Ollama, Obsidian, and Whisper

Remove or disable:
- autoupdate
- everything else that is not required

One-click cleanup:
- [[WIKI-TOOLS/6-TRIM-SERVICES.desktop|Trim Services]] — disable packagekit/tracker after confirmation
- [[WIKI-TOOLS/10-CLEANUP-POLICY.desktop|Cleanup Policy]] — full keep/remove audit: shows keep list, review candidates, disables autoupdate services

Cleanup script: `WIKI-TOOLS/handoff/10-cleanup-keep-policy.sh`

## Productivity Widgets

| # | Launcher | Action |
|---|---|---|
| 1 | [[WIKI-TOOLS/1-SEARCH-BOX.desktop|Search / Ask]] | Search wiki or ask Ollama |
| 2 | [[WIKI-TOOLS/2-NEW-NOTE.desktop|New Note]] | Create a new wiki note |
| 3 | [[WIKI-TOOLS/3-OPEN-WIKI.desktop|Open Wiki]] | Open vault in Obsidian |
| 4 | [[WIKI-TOOLS/4-STATUS.desktop|Status]] | Daemon + git + Ollama status |
| 5 | [[WIKI-TOOLS/5-LINT.desktop|Lint]] | Check broken links |
| 6 | [[WIKI-TOOLS/6-TRIM-SERVICES.desktop|Trim Services]] | Disable clutter services |
| 7 | [[WIKI-TOOLS/7-CHROMIUM-AI.desktop|Chromium AI]] | Open WebUI in Chromium |
| 8 | [[WIKI-TOOLS/8-FIREFOX-AI.desktop|Firefox AI]] | Open WebUI in Firefox |
| 9 | [[WIKI-TOOLS/9-DASHBOARD.desktop|Dashboard Note]] | This page |
| 10 | [[WIKI-TOOLS/10-CLEANUP-POLICY.desktop|Cleanup Policy]] | Keep/remove policy enforcer |
| — | [[WIKI-TOOLS/OLLAMA-CHAT.desktop|Open WebUI]] | Direct Open WebUI launcher |
| — | [[WIKI-TOOLS/RECORD-AUDIO.desktop|Record Audio]] | Whisper audio transcription |

**Keyboard shortcut**: `Super+Space` → wiki search/ask dialog

## Desktop Theme

Current: **Fedora-style Adwaita**
- GTK theme: `Adwaita` (dark or light via XFCE Appearance)
- Icons: `Adwaita`
- Font: `Cantarell 11` (Fedora default)
- Window buttons: close / minimize / maximize (left-to-right)
- Compositing: enabled (shadows, transparency)
- Cursor: `Adwaita`

To change variant: XFCE Settings → Appearance → Style → `Adwaita-dark`

## Quick Links

- [[system/overview|System overview]]
- [[GUIDE|User guide]]
- [[HOW-TO-USE-DAILY|Daily workflow]]
- [[ARCH-SYSTEM-RULES|System rules]]
- [[_meta/session/2026-05-05|Session report 2026-05-05]]
