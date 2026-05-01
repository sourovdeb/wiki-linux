# GitHub Copilot Instructions — wiki-linux

> Full agent schema: [AGENTS.md](../AGENTS.md) | Philosophy: [WIKI_AGENT.md](../WIKI_AGENT.md) | Acceptance criteria: [EXPECTATIONS.md](../EXPECTATIONS.md)

## What This Project Is

A Python daemon that watches system config files with inotify and uses a local
Ollama LLM to maintain `~/wiki/` — a Git-tracked Markdown knowledge base. The
OS is never modified; data flows one way: source file → wiki page.

## Build & Test

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/                          # no Ollama required; ollama.generate is mocked
WIKI_OS_CONFIG=./config.json python3 -m src.monitor --dry-run --once  # integration
```

## Module Map

| Module | Role |
|---|---|
| `src/config.py` | Loads `config.json`, expands `~` paths. Import `from src.config import cfg`. |
| `src/monitor.py` | inotify event loop. Entry point for the daemon. |
| `src/llm.py` | Ollama wrapper. All LLM calls go here. |
| `src/indexer.py` | Rebuilds `_meta/index.md` and `_meta/recent.md`. |
| `src/search.py` | ripgrep + RAG search. |
| `src/sync.py` | Git auto-commit and push. |
| `src/ingest.py` | Ingests source files into wiki pages. |
| `src/archive.py` | Moves pages to `_archive/` with timestamp. |
| `src/fix.py` | RAG-grounded troubleshooting assistant. |
| `src/lint.py` | Broken wikilink checker. |
| `src/tasklog.py` | Append-only audit log (`_meta/log.md`). |
| `src/agent/ingest.py` | Auto-organiser for messy home directories (Codespaces). |
| `bin/wiki` | Bash CLI dispatcher for all subcommands. |

## Hard Invariants (never violate)

1. **Never write outside `~/wiki` (WIKI_ROOT).** Validate every LLM `target_path`:
   `Path(WIKI_ROOT / path).resolve().is_relative_to(WIKI_ROOT)`
2. **Never write to `/etc`, `/usr`, `/var`.** Source → wiki, never reverse.
3. **Suppress self-writes.** Call `monitor.record_self_write(path)` after every
   write to WIKI_ROOT so the inotify loop doesn't reprocess it.
4. **No root, no fanotify.** Use `inotify_simple`. Daemon runs via `systemctl --user`.
5. **No subprocess Ollama.** Use the `ollama` Python client only (`localhost:11434`).
6. **Force JSON.** `format="json"` in every `ollama.generate()` call. Wrap
   `json.loads()` in try/except; skip on failure, never write partial output.

## Code Conventions

- Python 3.11+, `from __future__ import annotations` in every module
- `pathlib.Path` everywhere — never `os.path`
- Logger name pattern: `wiki.<module>` (e.g. `wiki.monitor`, `wiki.llm`)
- Functions that touch FS or call LLM return `bool` or `Optional[T]` — never raise into event loops
- All config values from `src/config.py` — nothing hardcoded
- Shell scripts: `set -euo pipefail`, `[[ ]]` tests, `command -v` for dependency checks

## Adding a New `wiki` Subcommand

1. Add a `case` branch to `bin/wiki`.
2. If backend logic is needed, add `src/<module>.py` following the conventions above.
3. Add unit tests in `tests/test_<module>.py` with mocked Ollama calls.

## What Not to Add

- No web server, REST API, or GUI framework in the daemon
- No SQLite or any database (wiki content is Markdown files only)
- No new Python dependencies without a concrete reason
- Do not use: `fanatify`, `pyinotify`, `watchdog`, `requests`
