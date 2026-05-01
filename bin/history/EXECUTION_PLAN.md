# Wiki-OS Execution Plan

## Context

Wiki-OS is a Python daemon that adds a Git-tracked Markdown wiki layer on top of Arch Linux, driven by a local Ollama LLM. The project has a working core (monitor, llm, indexer, search, sync, config) but has several bugs, missing modules, unwired CLI commands, and undocumented code. This plan closes every gap identified by reading all source files against `CLAUDE.md`, `AGENTS.md`, and `AGENT_PLAYBOOK.md`.

**Outcome:** All modules referenced in `CLAUDE.md` exist, are wired into `bin/wiki`, are tested, and all existing + new tests pass with no live Ollama required.

---

## Bugs to Fix (Phase 1)

### 1.1 — Dead `timeout` variable in `src/llm.py`

**File:** [src/llm.py](src/llm.py)

`timeout = cfg.get("ollama", {}).get("timeout_seconds", 30)` (≈line 97) is read but never passed to `ollama.generate()`. The ollama ≥0.4.0 client sets timeout only via `ollama.Client(timeout=...)`.

**Fix:** Replace both `ollama.generate(...)` call sites with `ollama.Client(timeout=timeout).generate(...)`.

**Impact:** All 6 tests in `tests/test_llm.py` use `patch("src.llm.ollama.generate", ...)` — update mock target to `patch("src.llm.ollama.Client")` simultaneously.

**New mock pattern:**
```python
mock_client = MagicMock()
mock_client.generate.return_value = _make_response({...})
with patch("src.llm.ollama.Client", return_value=mock_client):
    ...
```

### 1.2 — Broken `classify_file_content()` in `src/agent/ingest.py`

**File:** [src/agent/ingest.py](src/agent/ingest.py) ≈line 96

`llm.answer_question(prompt, [])` returns the hardcoded string `"No relevant content found in the wiki for that question."` when `snippets=[]`. `json.loads()` fails → function always returns `None` → entire ingest agent is non-functional.

**Fix:** Replace the `llm.answer_question(prompt, [])` call with a direct `ollama.Client(timeout=timeout).generate(model=model, prompt=prompt, format="json", stream=False)`. Mirror the pattern from Phase 1.1.

### 1.3 — Version mismatch: `install.sh` vs `requirements.txt`

**File:** [install.sh](install.sh)

`install.sh` installs `"ollama>=0.3"` but `requirements.txt` specifies `ollama>=0.4.0`.

**Fix:** Change the pip install line in `install.sh` to use `ollama>=0.4.0`.

**Verify:** `grep -n "ollama" install.sh requirements.txt` — both must show `>=0.4.0`.

### 1.4 — Systemd units hardcode `wiki-os` path (should be `wiki-linux`)

**Files:** [systemd/wiki-monitor.service](systemd/wiki-monitor.service), [systemd/wiki-sync.service](systemd/wiki-sync.service), [systemd/wiki-sync.timer](systemd/wiki-sync.timer)

All three reference `%h/wiki-os/` as `ExecStart`, `WorkingDirectory`, and `PYTHONPATH`. The actual repo directory is `wiki-linux`.

**Fix:** Replace `%h/wiki-os` with `%h/wiki-linux` in all three unit files. Keep `wiki-os` only in the config namespace path (`%h/.config/wiki-os`).

Also add a `sed -i` substitution in `install.sh` after copying unit files, so the path is always correct regardless of where the repo is cloned:
```bash
PROJ_RELPATH="${PROJECT_ROOT#$HOME/}"
for unit in wiki-monitor.service wiki-sync.service wiki-sync.timer; do
  sed -i "s|%h/wiki-os|%h/${PROJ_RELPATH}|g" "$SYSTEMD_DIR/$unit"
done
```

### 1.5 — Add `fix` section to `config.json`

**File:** [config.json](config.json)

`src/fix.py` reads `cfg.get("fix", {})` but no `fix` section exists. Graceful degradation works, but the config should document defaults.

**Fix:** Add:
```json
"fix": {
  "doc_roots": ["~/wiki"],
  "max_snippets": 8,
  "snippet_bytes": 2000
}
```

### 1.6 — Document `src/fix.py` and `src/agent/ingest.py` in layout docs

**Files:** [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md)

These modules exist but are absent from the repository layout trees.

**Fix:** Add entries for `src/fix.py`, `src/agent/`, and `src/agent/ingest.py` to the layout section in both files.

---

## New Modules to Create (Phase 2)

Creation order within Phase 2: `tasklog.py` → `bootstrap.py` → `ingest.py` → `lint.py` (dependency order).

### 2.1 — `templates/source_summary.md`

**File:** [templates/source_summary.md](templates/source_summary.md) *(new)*

Jinja2 template for raw source summary pages. Variables: `title`, `source_path`, `updated`, `ingested`, `explanation`, `contents`, `links`. This is the first template that will actually be rendered by Python code (via `src/ingest.py`).

### 2.2 — `src/tasklog.py`

**File:** [src/tasklog.py](src/tasklog.py) *(new)*

Master log writer. All other modules call this — must be created first.

```python
def append_log(message: str, wiki_root: Path | None = None) -> None
def write_task_note(title: str, body: str, tags: list[str] | None = None, wiki_root: Path | None = None) -> Path | None
def _log_path(wiki_root: Path) -> Path
def _task_path(title: str, wiki_root: Path) -> Path
```

**Invariants:** Never raises. Opens log in append mode. Calls `monitor.record_self_write()` before every write. Uses `_meta/log.md` for the append log and `_meta/tasks/<slug>.md` for task notes.

### 2.3 — `src/bootstrap.py`

**File:** [src/bootstrap.py](src/bootstrap.py) *(new)*

Idempotent wiki directory setup. Python counterpart to `install.sh`'s directory creation.

```python
def bootstrap(wiki_root: Path | None = None) -> bool
def is_bootstrapped(wiki_root: Path | None = None) -> bool
def _create_dirs(wiki_root: Path) -> None
def _write_readme(wiki_root: Path) -> None
def _init_log(wiki_root: Path) -> None
def _init_git(wiki_root: Path) -> bool
def _write_obsidian_stub(wiki_root: Path) -> None
```

**Invariants:** All writes call `monitor.record_self_write()`. `subprocess` allowed only for `git init` (same as `sync.py`).

### 2.4 — `src/ingest.py`

**File:** [src/ingest.py](src/ingest.py) *(new)*

Single-file ingest primitive. Distinct from `src/agent/ingest.py` (which does bulk directory scanning). This is what `bin/wiki ingest <file>` dispatches to.

```python
def ingest_file(source: Path, wiki_root: Path | None = None, *, dry_run: bool = False) -> Path | None
def ingest_batch(sources: list[Path], wiki_root: Path | None = None, *, dry_run: bool = False) -> dict[str, int]
def _render_page_from_template(source_path: Path, title: str, explanation: str, contents: str, updated: str, links: list[str]) -> str
```

**Implementation:** Calls `llm.generate_wiki_page()`, re-validates that target resolves inside `wiki_root`, calls `monitor.record_self_write()` before writing, calls `tasklog.append_log()` after. Uses `templates/source_summary.md` via Jinja2 for the `_render_page_from_template` helper.

**`__main__` block:** `python3 -m src.ingest <file> [--dry-run]`

### 2.5 — `src/lint.py`

**File:** [src/lint.py](src/lint.py) *(new)*

Wiki health-check report writer. Implements checks from `AGENT_PLAYBOOK.md` Section 6.

```python
def run_lint(wiki_root: Path | None = None) -> dict
def write_lint_report(results: dict, wiki_root: Path | None = None) -> Path | None
def _find_wikilinks(text: str) -> list[str]
def _check_broken_links(pages: dict[str, str], wiki_root: Path) -> list[dict]
def _find_orphans(pages: dict[str, str]) -> list[str]
def _check_missing_source(pages: dict[str, str], wiki_root: Path) -> list[str]
def _check_stale_pages(pages: dict[str, str], stale_days: int = 180) -> list[dict]
def _check_duplicate_titles(pages: dict[str, str]) -> list[dict]
```

**Checks:** broken `[[wikilinks]]`, orphan pages (no incoming links), missing `source:` frontmatter, pages older than 180 days, duplicate `title:` values.

**Output:** Writes `_meta/lint-report-<YYYY-MM-DD>.md` via `write_lint_report()`. Calls `tasklog.append_log()` after writing. Skips `_meta/` and `_tmp/` directories.

**`__main__` block:** `python3 -m src.lint`

---

## CLI Wiring (Phase 3)

**File:** [bin/wiki](bin/wiki)

Add `case` branches and handler functions for:

| Subcommand | Handler | Dispatches to |
|---|---|---|
| `ingest <file> [--dry-run]` | `cmd_ingest()` | `python3 -m src.ingest "$file"` |
| `lint` | `cmd_lint()` | `python3 -m src.lint` |
| `fix "<problem>"` | `cmd_fix()` | `python3 -m src.fix "$problem"` |
| `task "<title>" ["<body>"]` | `cmd_task()` | inline python one-liner calling `tasklog.write_task_note()` |
| `bootstrap` | `cmd_bootstrap()` | `python3 -m src.bootstrap` |

Update `_usage()` to list all subcommands including new ones.

---

## Tests to Create (Phase 4)

All tests must mock Ollama — zero live LLM calls. Mock targets after Phase 1.1 fix: `patch("src.llm.ollama.Client")`.

### 4.1 `tests/test_ingest.py` *(new)*

- `test_ingest_file_writes_page` — LLM returns valid dict, page written
- `test_ingest_file_returns_none_on_llm_failure` — LLM returns None
- `test_ingest_file_rejects_path_escape` — LLM returns `../../etc/passwd.md`
- `test_ingest_file_dry_run` — no file written in dry_run mode
- `test_ingest_batch_counts` — correct `ingested`/`failed`/`skipped` counts
- `test_render_page_from_template` — Jinja2 renders expected frontmatter

### 4.2 `tests/test_lint.py` *(new)*

- `test_find_wikilinks_basic` — extracts `[[target]]`
- `test_find_wikilinks_with_display_text` — `[[link|display]]` extracts only `link`
- `test_check_broken_links_detects_missing` — flags links to non-existent pages
- `test_check_broken_links_valid` — passes valid links
- `test_find_orphans` — detects pages with no incoming links
- `test_check_missing_source` — detects pages without `source:` frontmatter
- `test_write_lint_report_creates_file` — report written to `_meta/`
- `test_run_lint_returns_structure` — result dict has all required keys

### 4.3 `tests/test_tasklog.py` *(new)*

- `test_append_log_creates_file` — creates `_meta/log.md` if absent
- `test_append_log_appends` — does not overwrite existing log
- `test_append_log_has_timestamp` — ISO 8601 timestamp present
- `test_write_task_note_creates_page` — `_meta/tasks/<slug>.md` created with frontmatter
- `test_write_task_note_returns_path` — correct Path returned
- `test_append_log_records_self_write` — `monitor.record_self_write()` called

### 4.4 `tests/test_bootstrap.py` *(new)*

- `test_bootstrap_creates_dirs` — `system/`, `user/`, `_meta/`, `_tmp/` created
- `test_bootstrap_idempotent` — safe to call twice
- `test_is_bootstrapped_false_before` — returns False on empty dir
- `test_is_bootstrapped_true_after` — returns True after bootstrap
- `test_write_readme_preserves_existing` — does not overwrite README.md
- `test_bootstrap_handles_path_collision` — returns False if path is a file

### 4.5 Update `tests/test_llm.py`

Update all 6 existing tests to mock `src.llm.ollama.Client` instead of `src.llm.ollama.generate` (required by Phase 1.1 fix).

---

## Documentation Files (Phase 5)

### 5.1 `ARCHITECTURE.md` *(new)*

ASCII data-flow diagram, module dependency graph, self-write suppression explanation, security boundaries (WIKI_ROOT constraint), systemd topology, config schema cross-reference.

### 5.2 `USER_GUIDE.md` *(new)*

Installation, first run (`wiki bootstrap`, `wiki status`), daily use commands, all new subcommands (`ingest`, `lint`, `fix`, `task`), config customization, troubleshooting.

### 5.3 `WIKI_SCHEMA.md` *(new)*

YAML frontmatter fields and semantics, required vs optional per page type, wikilink format, directory conventions, log format.

---

## Verification Commands (Phase 6)

```bash
# All tests pass with no live Ollama
pytest tests/ -v --tb=short

# CLI smoke tests
export PYTHONPATH=/home/sourov/Documents/wiki-linux/wiki-linux
export WIKI_OS_CONFIG=/home/sourov/Documents/wiki-linux/wiki-linux/config.json
PATH="/home/sourov/Documents/wiki-linux/wiki-linux/bin:$PATH"
wiki bootstrap
wiki status
EDITOR=true wiki new "Test Page"
wiki lint
wiki config
wiki help | grep -E "ingest|lint|fix|task|bootstrap"

# Version consistency
grep -n "ollama" requirements.txt install.sh  # both must show >=0.4.0

# Systemd path correctness
grep "wiki-os\|wiki-linux" systemd/*.service systemd/*.timer

# Template rendering
python3 -c "
import jinja2, pathlib
tdir = pathlib.Path('templates')
env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(tdir)))
tmpl = env.get_template('source_summary.md')
print(tmpl.render(title='T', source_path='/etc/t', updated='2026-05-01', ingested='2026-05-01', explanation='x', contents='a=1', links=[]))
"
```

---

## Execution Order and Dependencies

```
Phase 1 (bugs)
  1.1 llm.py timeout fix + test_llm.py mock update
  1.2 agent/ingest.py classify_file_content fix
  1.3 install.sh version fix
  1.4 systemd path fix
  1.5 config.json fix section
  1.6 CLAUDE.md + AGENTS.md layout update
    ↓
Phase 2 (new modules, in dependency order)
  2.1 templates/source_summary.md
  2.2 src/tasklog.py         ← no deps on new modules
  2.3 src/bootstrap.py       ← needs tasklog
  2.4 src/ingest.py          ← needs llm, monitor, tasklog
  2.5 src/lint.py            ← needs tasklog
    ↓
Phase 3 (bin/wiki wiring)    ← needs all Phase 2 modules
    ↓
Phase 4 (tests)              ← needs Phase 2 complete; can TDD alongside Phase 2
    ↓
Phase 5 (docs)               ← independent, can be done anytime
    ↓
Phase 6 (integration check)  ← everything must be complete
```

---

## Critical Files

| File | Action |
|---|---|
| [src/llm.py](src/llm.py) | Fix timeout Client pattern |
| [src/agent/ingest.py](src/agent/ingest.py) | Fix `classify_file_content` LLM call |
| [install.sh](install.sh) | Fix ollama version + add sed path substitution |
| [systemd/wiki-monitor.service](systemd/wiki-monitor.service) | Fix `wiki-os` → `wiki-linux` |
| [systemd/wiki-sync.service](systemd/wiki-sync.service) | Fix `wiki-os` → `wiki-linux` |
| [systemd/wiki-sync.timer](systemd/wiki-sync.timer) | Fix `wiki-os` → `wiki-linux` |
| [config.json](config.json) | Add `fix` section |
| [CLAUDE.md](CLAUDE.md) | Add `fix.py` and `agent/` to layout |
| [AGENTS.md](AGENTS.md) | Add `fix.py` and `agent/` to layout |
| [bin/wiki](bin/wiki) | Add 5 new subcommand handlers |
| [tests/test_llm.py](tests/test_llm.py) | Update mock target to `ollama.Client` |
| [templates/source_summary.md](templates/source_summary.md) | Create (Jinja2 template) |
| [src/tasklog.py](src/tasklog.py) | Create |
| [src/bootstrap.py](src/bootstrap.py) | Create |
| [src/ingest.py](src/ingest.py) | Create |
| [src/lint.py](src/lint.py) | Create |
| [tests/test_ingest.py](tests/test_ingest.py) | Create |
| [tests/test_lint.py](tests/test_lint.py) | Create |
| [tests/test_tasklog.py](tests/test_tasklog.py) | Create |
| [tests/test_bootstrap.py](tests/test_bootstrap.py) | Create |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Create |
| [USER_GUIDE.md](USER_GUIDE.md) | Create |
| [WIKI_SCHEMA.md](WIKI_SCHEMA.md) | Create |
