# CLAUDE.md — Instructions for Claude Code

## Project Identity

This is **Wiki-OS**, a Python-based daemon system that adds a wiki-native
knowledge layer on top of an Arch Linux installation. Read `README.md` first for
the full rationale. The short version: `~/wiki` is a Git-tracked directory of
Markdown files; a daemon watches system and user files with inotify and uses the
Ollama local LLM API to generate and maintain wiki pages; a shell script called
`wiki` ties everything together.

The project is deliberately minimal. When in doubt, prefer fewer lines over more.

---

## Repository Layout

```
wiki-os/
├── CLAUDE.md                ← you are here
├── AGENTS.md                ← same purpose, OpenAI Codex format
├── README.md                ← human documentation (what and why)
├── config.json              ← canonical default config (schema + defaults)
├── install.sh               ← idempotent install script (no sudo required)
├── bin/
│   └── wiki                 ← bash dispatcher, entry point for humans
├── src/
│   ├── __init__.py
│   ├── config.py            ← loads and validates config.json
│   ├── monitor.py           ← inotify daemon (main daemon entry point)
│   ├── llm.py               ← Ollama API wrapper, structured JSON output
│   ├── indexer.py           ← rebuilds _meta/index.md and _meta/recent.md
│   ├── search.py            ← ripgrep + LLM RAG search
│   └── sync.py              ← git auto-commit and push
├── systemd/
│   ├── wiki-monitor.service ← user-level service for monitor.py
│   ├── wiki-sync.service    ← one-shot git commit service
│   └── wiki-sync.timer      ← fires wiki-sync.service every 5 minutes
└── templates/
    ├── system_config.md     ← Jinja2 template for /etc mirror pages
    └── new_page.md          ← Jinja2 template for new user pages
```

---

## Environment and Dependencies

The target system is **Arch Linux** with Python 3.11+. All Python dependencies
are listed below. Do not add new dependencies without a clear reason; if something
is available in the standard library, prefer that.

Runtime Python packages (in `requirements.txt`):
- `ollama` — official Ollama Python client
- `inotify_simple` — thin, unprivileged inotify wrapper
- `pyyaml` — YAML frontmatter parsing
- `jinja2` — template rendering for page scaffolding

System packages (installed by `install.sh` via `pacman`):
- `ollama` — local LLM service
- `ripgrep` — fast full-text search
- `git` — version control
- `glow` — terminal markdown renderer
- `md-tui` — terminal markdown navigator (AUR: `md-tui-bin`)

Do not import `fanotify`, `pyinotify`, or `watchdog`. The project uses
`inotify_simple` exclusively.

Do not call `subprocess.run(["ollama", ...])`. All LLM calls go through the
`ollama` Python client to `http://localhost:11434`.

---

## Coding Conventions

**Language**: Python 3.11+, typed with `from __future__ import annotations`.
Use `pathlib.Path` everywhere; never `os.path`.

**Logging**: Use the stdlib `logging` module with the logger name `wiki.<module>`.
Never print to stdout in daemon code; use `logging.info/warning/error`.

**Error handling**: Functions that touch the filesystem or call the LLM return
`bool` or `Optional[T]` — never raise into a daemon event loop. Log the error
and return `False`/`None`.

**Configuration**: Every configurable value comes from `src/config.py`. No
module hardcodes a path, model name, or timeout. Import `from src.config import
cfg` after `config.py` has been initialised in the entry point.

**Self-write suppression**: Any function that writes to `~/wiki` must call
`monitor.record_self_write(path)` immediately after writing so the inotify loop
does not reprocess the file it just created.

**JSON from LLM**: Always use `format="json"` in `ollama.generate()` and wrap
`json.loads(response["response"])` in a try/except that logs and returns
`False` on failure. Validate that required keys exist before using the response.

**Tests**: Place tests in `tests/`. Use `pytest`. Do not require a live Ollama
instance for unit tests — mock `ollama.generate` where needed.

---

## Key Invariants — Never Violate These

1. The daemon **never writes outside `~/wiki`**. The LLM provides a
   `target_path`; validate it is relative and resolve it under `WIKI_ROOT`
   before writing. Reject any path that resolves outside `WIKI_ROOT`.

2. The daemon **never writes back to `/etc`**. Data flows one direction only:
   source file → wiki page. The wiki is documentation, not configuration.

3. The inotify loop **suppresses its own writes**. Every file the daemon writes
   is recorded in a `deque` with a timestamp. Events for those paths are ignored
   for `DEBOUNCE_SECONDS` after writing.

4. The daemon **runs as the login user** via `systemctl --user`. No component
   requires `CAP_SYS_ADMIN` or root. If something seems to require root, find
   an alternative.

5. **File content is capped** before being sent to the LLM. Read at most
   `config["ollama"]["context_limit_bytes"]` bytes. Log a warning if the file
   is truncated.

---

## How to Test Without a Full Arch Install

```bash
# Install deps in a venv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Unit tests (mock Ollama, mock inotify)
pytest tests/

# Integration smoke test (requires Ollama running locally)
WIKI_OS_CONFIG=./config.json python3 -m src.monitor --dry-run

# Test the wiki CLI
PATH="$PWD/bin:$PATH" wiki --help
```

---

## Common Tasks for Claude Code

**Adding a new `wiki` subcommand**: Add a `case` branch to `bin/wiki` and,
if backend logic is needed, add a corresponding Python module in `src/`.

**Adding a new `/etc` file to mirror**: Add its path to `monitor.etc_allowlist`
in `config.json`. No code changes needed — the allowlist is checked at runtime.

**Changing the page template**: Edit `templates/system_config.md` (Jinja2).
The template receives: `source_path`, `title`, `content`, `updated`, `links`.

**Changing the LLM system prompt**: Edit the `SYSTEM_PROMPT` constant in
`src/llm.py`. Keep it concise — smaller models lose instruction following when
the system prompt is too long.

**Rebuilding the index manually**: `python3 -m src.indexer`

**Running the sync manually**: `python3 -m src.sync`

---

## What Not to Do

Do not add a web server, REST API, or browser-based interface. The wiki is a
local-first tool; network exposure is the user's choice and out of scope here.

Do not store user content in SQLite or any database. The wiki is Markdown files.
Indexing lives in `_meta/` as Markdown too, not in a sidecar database.

Do not make the LLM call synchronous in a way that blocks inotify event
processing for more than one file at a time. Use a thread pool or async queue
if event volume demands it.

Do not add a dependency on D-Bus, libnotify, or any GUI toolkit. The daemon is
headless; notifications are out of scope unless explicitly added later.
