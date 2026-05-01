# AGENTS.md — Wiki-Linux Agent Instructions

> This file is read by OpenAI Codex, Claude Code, and any other agent
> working on this repository. Read it before touching any file.
>
> The master "idea file" is **WIKI_AGENT.md** — copy it into any LLM
> agent to bootstrap a new installation. This file (AGENTS.md) is the
> project-specific schema that a running agent uses during ongoing work.

---

## What This Project Is

A personal wiki-native knowledge layer for Arch Linux (and other
systems). It adds `~/wiki/` — a Git-tracked directory of Markdown files
— on top of a stock OS. The OS itself is never modified. `/etc` stays
where it is. The wiki mirrors and documents it.

Reference: Andrej Karpathy's `llm-wiki.md`
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

## Repository Layout

```
wiki-linux/
├── WIKI_AGENT.md            ← master idea file (copy into any LLM agent)
├── AGENTS.md                ← you are here (Codex / agent schema)
├── CLAUDE.md                ← same schema for Claude Code
├── LINUX_AGENT_TASKS.md     ← concrete Arch/Debian setup steps
├── WINDOWS_AGENT_TASKS.md   ← Windows 10/11 setup steps (safe version)
├── SUPPORT_POPUP.md         ← wiki-notify helper (all platforms)
├── CODESPACES_AGENT.md      ← cloud / GitHub Codespaces agent tasks
├── README.md                ← human documentation
├── config.json              ← default configuration
├── install.sh               ← idempotent installer (Arch/Debian)
├── requirements.txt         ← Python dependencies
├── bin/
│   └── wiki                 ← bash CLI dispatcher
├── src/
│   ├── __init__.py
│   ├── config.py            ← loads config.json, expands paths
│   ├── monitor.py           ← inotify daemon (main daemon entry point)
│   ├── llm.py               ← Ollama API wrapper, JSON output
│   ├── indexer.py           ← rebuilds _meta/index.md and recent.md
│   ├── search.py            ← ripgrep + RAG search
│   └── sync.py              ← git auto-commit and push
├── systemd/
│   ├── wiki-monitor.service ← user-level service for monitor.py
│   ├── wiki-sync.service    ← one-shot git commit service
│   └── wiki-sync.timer      ← fires wiki-sync.service every 5 min
└── templates/
    ├── system_config.md     ← Jinja2 template for /etc mirror pages
    └── new_page.md          ← Jinja2 template for new user pages
```

---

## Non-Negotiable Invariants

1. **Never write outside `~/wiki` (WIKI_ROOT)**. Every LLM-provided
   `target_path` must be validated before writing:
   `Path(WIKI_ROOT / path).resolve().is_relative_to(WIKI_ROOT)`

2. **Never write to `/etc`, `/usr`, `/var`, or any system path**.
   Data flows one way: source file → wiki page. Never the reverse.

3. **Suppress self-writes**. After writing to WIKI_ROOT, record the
   path in a deque with a timestamp. Skip inotify events for that path
   for `DEBOUNCE_SECONDS` (default 5).

4. **No root, no fanotify**. Use `inotify_simple`. The daemon runs as
   the login user via `systemctl --user`.

5. **No subprocess Ollama**. Use the `ollama` Python client only.
   All LLM calls go to `localhost:11434`.

6. **force JSON**. Use `format="json"` in `ollama.generate()`. Wrap
   `json.loads()` in try/except. Skip on parse failure, never write
   partial output.

7. **Confirm before destructive operations**. Uninstall, delete, move,
   rename — pause and get explicit user confirmation.

---

## Dependencies

Python: `ollama>=0.3`, `inotify_simple>=1.3`, `pyyaml>=6.0`, `jinja2>=3.1`

System (Arch): `git`, `ripgrep`, `glow`, `ollama`, `obsidian`
System (Debian): `git`, `ripgrep`, then Obsidian via flatpak

Do not add new Python dependencies without a concrete reason.
Do not use: `fanotify`, `pyinotify`, `watchdog`, `requests` (ollama client covers HTTP).

---

## Code Style

- Python 3.11+, `from __future__ import annotations` in every module
- `pathlib.Path` everywhere, never `os.path`
- `logging` module, logger name `wiki.<module>`
- Functions that can fail return `bool` or `Optional[T]`, never raise into event loops
- All configurable values from `src/config.py`, nothing hardcoded
- Shell: `set -euo pipefail`, `[[ ]]` conditionals, `command -v` for checks

---

## Build Order (if implementing from scratch)

`config.py` → `llm.py` → `monitor.py` → `indexer.py` → `search.py`
→ `bin/wiki` → `install.sh` → systemd units

---

## Testing

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest
pytest tests/
# Integration test (requires Ollama running):
WIKI_OS_CONFIG=./config.json python3 -m src.monitor --dry-run --once
```
