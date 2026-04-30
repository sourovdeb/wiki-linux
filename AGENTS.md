# AGENTS.md — Instructions for OpenAI Codex

## Project Summary

Wiki-OS is a daemon system for Arch Linux that creates and maintains a
Markdown-based personal knowledge base (`~/wiki`) with real-time file monitoring
and a local LLM. It mirrors selected system configuration files from `/etc` into
human-readable wiki pages, and provides a `wiki` shell command as the user's
single entry point. All processing is offline. Nothing requires internet access
after initial package installation.

Before writing any code, read `README.md` in full. It explains every
architectural decision and why the approach taken is correct.

---

## Project Layout

```
wiki-os/
├── AGENTS.md                ← you are here
├── CLAUDE.md                ← same instructions for Claude Code
├── README.md                ← human doc, read this first
├── config.json              ← default configuration (schema + defaults)
├── install.sh               ← idempotent installer
├── bin/wiki                 ← bash CLI dispatcher
├── src/
│   ├── config.py            ← config loader
│   ├── monitor.py           ← inotify daemon (daemon entry point)
│   ├── llm.py               ← Ollama API module
│   ├── indexer.py           ← wiki index generator
│   ├── search.py            ← ripgrep + RAG search
│   └── sync.py              ← git auto-commit
├── systemd/
│   ├── wiki-monitor.service
│   ├── wiki-sync.service
│   └── wiki-sync.timer
└── templates/
    ├── system_config.md
    └── new_page.md
```

---

## Dependencies

Python runtime: `ollama`, `inotify_simple`, `pyyaml`, `jinja2`.
System tools: `ollama`, `ripgrep`, `git`, `glow`, `md-tui` (AUR).

No other dependencies. Do not introduce new ones without strong justification.

---

## Constraints the Codex Agent Must Respect

**Filesystem safety**: The daemon only writes inside `~/wiki` (the configured
`WIKI_ROOT`). Every LLM-provided `target_path` must be validated with
`Path(WIKI_ROOT / target_path).resolve().is_relative_to(WIKI_ROOT)` before any
file write. Paths that escape `WIKI_ROOT` are rejected and logged. This is a
security invariant — never relax it.

**No root, no fanotify**: The daemon runs as a normal user via `systemctl
--user`. Use `inotify_simple` for file monitoring. Do not use fanotify,
pyinotify, or watchdog.

**No subprocess Ollama**: All LLM interaction goes through the `ollama` Python
library talking to `localhost:11434`. Never call `subprocess.run(["ollama",
...])`.

**Self-write suppression**: After writing any file to `WIKI_ROOT`, record the
path and timestamp in a deque. Ignore inotify events for that path for
`DEBOUNCE_SECONDS` (default 5) to prevent the daemon from re-processing its own
output.

**LLM output validation**: Always use `format="json"` in `ollama.generate()`.
Parse the response with a try/except around `json.loads`. Verify required keys
(`target_path`, `content`) before using them. If validation fails, log the error
and skip the file — do not write partial output.

**Content truncation**: Read at most `config["ollama"]["context_limit_bytes"]`
bytes of any source file. Log a warning if truncation occurs.

---

## Code Style

Python 3.11+. `from __future__ import annotations` in every module. `pathlib.Path`
for all filesystem operations. `logging` module with logger name `wiki.<module>`.
Functions that can fail return `bool` or `Optional[T]`, they do not raise into
the event loop. All configurable values come from `src/config.py` — no hardcoded
paths, model names, or timeouts in other modules.

Shell scripts are POSIX bash. `set -euo pipefail` at the top of every script.
Prefer `command -v` for dependency checks. Prefer `[[ ]]` for conditionals.

---

## Testing

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest
pytest tests/
```

Unit tests mock `ollama.generate` and `inotify_simple.INotify`. Tests do not
require a live Ollama instance or Arch Linux. Place test files in `tests/` with
the prefix `test_`.

For integration testing with a live Ollama:
```bash
WIKI_OS_CONFIG=./config.json python3 -m src.monitor --dry-run --once
```

---

## Implementation Priorities

If implementing from this spec, build in this order to be able to test each
layer incrementally. First `src/config.py`, because every other module depends
on it. Then `src/llm.py`, testable in isolation with a mock file. Then
`src/monitor.py`, the core daemon. Then `src/indexer.py` and `src/search.py`,
which are optional from the daemon's perspective but required for the `wiki ask`
and `wiki search` commands. Finally `bin/wiki` and `install.sh`, which assume
all the Python modules are working.

The systemd units are simple templates; write them last and keep them minimal.
