# Wiki-Linux Execution Plan — v2 (Expectations-Aligned)

> **Supersedes:** [EXECUTION_PLAN.md](EXECUTION_PLAN.md) (v1) and
> [CHAT_SUMMARY.md](CHAT_SUMMARY.md).
>
> **Authored:** 2026-05-01
>
> **Why v2 exists:** v1 was a code-correctness plan. It fixed bugs and added
> three modules (`tasklog`, `ingest`, `lint`). But v1 did **not** satisfy
> several of the user-facing safety guarantees that
> [EXPECTATIONS.md](../../EXPECTATIONS.md) promises a setup user will see.
> v2 is the gap-aware plan that closes both the code drift *and* the
> expectations drift.
>
> **Read this with:**
> 1. [WIKI_AGENT.md](../../WIKI_AGENT.md) — philosophy
> 2. [AGENT_PLAYBOOK.md](../../AGENT_PLAYBOOK.md) — execution discipline
> 3. [CLAUDE.md](../../CLAUDE.md) / [AGENTS.md](../../AGENTS.md) — code conventions
> 4. [EXPECTATIONS.md](../../EXPECTATIONS.md) — **the user contract** (this is what we are building toward)
> 5. This file — the integrated plan

---

## TL;DR — Is This Better Than EXPECTATIONS?

**EXPECTATIONS.md is the *contract*; this plan is the *implementation* of that contract.**

The two are not in competition. They sit at different layers:

| Layer | File | Audience | Purpose |
|---|---|---|---|
| **Promise** | `EXPECTATIONS.md` | End user (read-once during install) | "Here is what you will see and what is locked" |
| **Plan** | This file | Implementer / agent | "Here is exactly how we make those promises true" |

**v1's failure:** v1 silently assumed the existing code already satisfied
EXPECTATIONS, then proceeded to add three more modules. It did not.
Specifically, **6 of the 12 EXPECTATIONS guarantees are not currently
implemented**:

| # | Guarantee | Currently Implemented? | Source of truth |
|---|---|---|---|
| 1 | `~/wiki/_archive/` exists; deletes go there | ❌ Not implemented | EXPECTATIONS Part 1 §49, Part 5 Guarantee 3 |
| 2 | `~/wiki/_meta/log.md` append-only operation log | ❌ Not implemented (planned in v1 as `tasklog.py`) | EXPECTATIONS Part 1 §46 |
| 3 | `config.json` chmod'd `u-w` after install | ❌ Not implemented | EXPECTATIONS Part 5 Guarantee 1 |
| 4 | `install.sh --uninstall` leaves `~/wiki/` intact | ❌ No uninstall flag exists | EXPECTATIONS Part 6 Option 3 |
| 5 | `install.sh --reconfigure` for re-locking config | ❌ Not implemented | EXPECTATIONS Part 5 Guarantee 1 §256 |
| 6 | `wiki lint` subcommand exists | ❌ Not wired (planned in v1) | EXPECTATIONS Part 2 Tool 1 §106 |
| 7 | `wiki status` shows daemon PID + remote + size | ⚠️ Partial — current `cmd_status` shows pages/git/systemd but not in EXPECTATIONS' format | EXPECTATIONS Part 2 Tool 1 §97 |
| 8 | Daemon never hard-deletes — uses `_archive/` move | ❌ Daemon doesn't delete at all today; behaviour for deletes is undefined | EXPECTATIONS Part 5 Guarantee 3 |
| 9 | Self-write suppression provably enforced | ✅ Implemented in `monitor.py:67-83` | EXPECTATIONS implied (Part 3 daemon log §167) |
| 10 | `/etc` never written | ✅ Implemented (no write paths to `/etc`) | EXPECTATIONS Part 5 Guarantee 4 |
| 11 | systemd runs as user, not root | ✅ Implemented (`systemctl --user`) | EXPECTATIONS Part 5 Guarantee 5 |
| 12 | Git tracks every change | ✅ Implemented in `sync.py` | EXPECTATIONS Part 5 Guarantee 2 |

**v2 closes 6 gaps. v1 closed 1 (the lint subcommand).** That's the
"better, efficient" answer to the user's question.

### Direct answers to the user's four sub-questions

1. **"better option?"** — v2 is better than v1. v1 fixed bugs but ignored
   six concrete promises in EXPECTATIONS. v2 maps every promise to either
   "already implemented" or "phase X.Y of this plan."
2. **"better efficient option"** — v2 is more efficient *per unit of
   user-visible value*. v1 added 3 docs files (low value) and skipped the
   archive/uninstall machinery (high value). v2 inverts that ratio.
3. **"efficient option"** — v2 deletes 7 files of v1 scope (3 docs +
   `bootstrap.py` + 3 tests) and adds 4 files that *directly* implement
   EXPECTATIONS guarantees (`archive.py`, `uninstall` flag in `install.sh`,
   chmod step, `wiki status` upgrade).
4. **"efficient option."** — same as 3.

The user repeated the question four times. I'm reading that as: *"Be sure
this plan is genuinely better, not just longer. Don't pad."* Acknowledged.
This file ends at section 16, and section 16 is the one-page card. Anything
that doesn't map to a guarantee or a verified bug is cut.

---

## Section 1 — Investigation Summary (what is true today)

I read every file referenced by v1. Here is the verified state of the repo
as of 2026-05-01:

### 1.1 Real bugs (5 of v1's 6 stand; 1 is overstated)

| # | v1 claim | Verified? | Evidence |
|---|---|---|---|
| 1.1.a | `src/llm.py:97` — dead `timeout` variable | ✅ Real | Variable read but never passed to `ollama.generate()` |
| 1.1.b | `src/agent/ingest.py:96` — broken `classify_file_content()` | ✅ Real | `llm.answer_question(prompt, [])` short-circuits to fixed string at `llm.py:163` |
| 1.1.c | `install.sh:74` pins `ollama>=0.3` vs `requirements.txt`'s `>=0.4.0` | ✅ Real | Direct grep |
| 1.1.d | systemd units use `%h/wiki-os/` | ✅ Real | All 3 unit files; repo is `wiki-linux` |
| 1.1.e | `config.json` missing `fix` section | ⚠️ Cosmetic | `src/fix.py:21,26-27` reads via `cfg.get(..., default)` so works without it |
| 1.1.f | `CLAUDE.md`/`AGENTS.md` layout missing `fix.py`, `agent/` | ✅ Real | Trees do not list these files |

**Plus one more bug v1 missed:**

| # | v1 missed | Evidence |
|---|---|---|
| 1.1.g | `src/fix.py` and `tests/test_fix.py` are untracked in git | `git status` shows `?? src/fix.py` and `?? tests/test_fix.py` |

### 1.2 EXPECTATIONS guarantees not yet implemented

Listed in the TL;DR table above. Six concrete features that
EXPECTATIONS promises and the codebase does not yet deliver.

### 1.3 v1 plan errors

| # | v1 said | Reality | Correction |
|---|---|---|---|
| 1.3.a | "Update all 6 tests in `test_llm.py` mock target to `ollama.Client`" | Only 5 of 6 mock `ollama.generate`; switching to `Client` is a stylistic choice not a requirement | Use module-level `_client = ollama.Client(timeout=...)` and patch `_client.generate` |
| 1.3.b | "Replace `%h/wiki-os` with `%h/${PROJECT_ROOT#$HOME/}` via sed" | Breaks if repo is outside `$HOME` (e.g. `/opt/wiki-linux`, Codespaces) | Default unit files to `%h/wiki-linux`; sed only patches when needed |
| 1.3.c | "Create `src/bootstrap.py`" | `install.sh:96-136` already bootstraps; Python version duplicates effort unless we need it for Codespaces | Defer until Codespaces-only install lands |
| 1.3.d | "Add 3 new docs (`ARCHITECTURE.md`, `USER_GUIDE.md`, `WIKI_SCHEMA.md`)" | Repo already has 11 doc files; these duplicate `EXPECTATIONS.md` + `README.md` + `WIKI_AGENT.md` | Cut. Spend the budget on EXPECTATIONS guarantees instead |
| 1.3.e | "`bin/wiki` adds 5 new subcommands" | One of them (`reprocess`) already exists and overlaps with proposed `ingest` | Rename `reprocess` to `ingest`; keep `reprocess` as a compat alias for one release |
| 1.3.f | v1 called for `format_wiki_page()` in `src/agent/ingest.py:328-355` to be duplicated in new `src/ingest.py` | Single source of truth wins | Extract to `src/ingest.py::render_page` with Jinja2; `agent/ingest.py` calls it |

---

## Section 2 — Phase Structure

Phases are grouped by **commit boundary**. Each phase is one commit. If a
phase fails verification, only that commit gets reverted.

```
Phase 0  Decisions & alignment       (no code)
Phase 1  Stage untracked files       (1 commit)
Phase 2  Bug fixes                    (1 commit)
Phase 3  EXPECTATIONS guarantees A    (1 commit) — archive, log, lock
Phase 4  Module extraction            (1 commit) — tasklog + ingest refactor
Phase 5  EXPECTATIONS guarantees B    (1 commit) — uninstall, status, lint subcommand
Phase 6  Lint module + CLI            (1 commit)
Phase 7  Tests                        (1 commit, can squash with phase it tests)
Phase 8  Verification & integration   (no commit)

DEFERRED (require user OK):
- Phase 9   src/bootstrap.py            (only if --codespaces install needed)
- Phase 10  3 new doc files             (only if user names a real gap)
```

Each phase is reversible. Each phase has explicit verification at the end
that must pass before moving on.

---

## Section 3 — Phase 0: Decisions to Confirm

Five questions. **Do not start Phase 1 until the user answers.** Defaults
shown; I'll apply defaults if the user says "go".

| # | Question | Default | Why it matters |
|---|---|---|---|
| 0.1 | `llm.py` timeout fix style: module-level `Client` (test-breaking) or pass `options={"timeout": ...}` (untested)? | Module-level `Client` | Existing `tests/test_llm.py` 6 tests need a mock-target swap (small, mechanical). Per-call `Client(...)` is wasteful. |
| 0.2 | `EXPECTATIONS.md` Guarantee 3 (`_archive/` for deletes) — implement now or later? | **Now** (Phase 3) | This is the most user-visible safety promise and is currently a lie. |
| 0.3 | `install.sh --uninstall` flag — implement now or later? | **Now** (Phase 5) | EXPECTATIONS Part 6 Option 3 explicitly references it. |
| 0.4 | `install.sh --reconfigure` flag (for editing locked config)? | **Now** (Phase 5) | Pairs with the chmod lock. Without it, users `chmod u+w` manually, which leaks the lock state. |
| 0.5 | Phase 9 (`bootstrap.py`) and Phase 10 (3 docs) — keep deferred? | **Yes, deferred** | YAGNI. `install.sh` already bootstraps; existing docs cover the audience. |

---

## Section 4 — Phase 1: Stage Untracked Files

**Goal:** Get the repo into a clean baseline before edits.

**Commands:**
```bash
git status                                              # confirm only src/fix.py, tests/test_fix.py untracked
git add src/fix.py tests/test_fix.py
git commit -m "chore: stage previously-untracked fix module and tests

src/fix.py implements 'wiki fix \"<problem>\"' (RAG over local docs)
tests/test_fix.py covers _collect_snippets, suggest_fix.

Module already imported by future bin/wiki cmd_fix wiring."
```

**Verification:**
```bash
git status                  # working tree clean
git log -1 --stat           # one commit, two files added
pytest tests/test_fix.py -q # green
```

---

## Section 5 — Phase 2: Bug Fixes (One Commit)

Each bug fix is independently verifiable. Apply in the order below; do
**not** combine commits.

### 5.1 — `src/llm.py` timeout actually used

**Files:** [src/llm.py](../../src/llm.py)

**Change:**
```python
# At module top:
_client: ollama.Client | None = None

def _get_client() -> ollama.Client:
    """Lazy module-level Client so tests can monkey-patch it cleanly."""
    global _client
    if _client is None:
        timeout = cfg.get("ollama", {}).get("timeout_seconds", 30)
        _client = ollama.Client(timeout=timeout)
    return _client
```

Replace both `ollama.generate(...)` call sites with `_get_client().generate(...)`.

**Test impact:** [tests/test_llm.py](../../tests/test_llm.py) — 5 of 6 tests
patch `src.llm.ollama.generate`. Update each to:
```python
from src.llm import _get_client  # not strictly needed
with patch("src.llm.ollama.Client") as MockClient:
    MockClient.return_value.generate = MagicMock(return_value=_make_response({...}))
    # ... call code under test
```

Or, simpler, monkeypatch the module global:
```python
def test_xxx(monkeypatch, ...):
    fake_client = MagicMock()
    fake_client.generate.return_value = _make_response({...})
    monkeypatch.setattr("src.llm._client", fake_client)
    # ... call code under test
```

**Use the second form** — it's a one-line change per test instead of three.

**Why this matters:** Without the timeout, an offline Ollama daemon hangs
the wiki-monitor for the system default (~120s) per event.

### 5.2 — `src/agent/ingest.py::classify_file_content`

**Files:** [src/agent/ingest.py:62-108](../../src/agent/ingest.py)

**Change:** Replace the `llm.answer_question(prompt, [])` call with a
direct call through the shared `_get_client()` (after 5.1 lands):
```python
client = llm._get_client()
model = cfg.get("ollama", {}).get("model", "mistral")
try:
    response = client.generate(
        model=model,
        prompt=prompt,
        format="json",
        stream=False,
    )
    raw = response.response if hasattr(response, "response") else response["response"]
    parsed = json.loads(raw)
except (json.JSONDecodeError, ValueError, AttributeError) as e:
    log.warning("LLM classification failed for %s: %s", filename, e)
    return None
```

**Verification:** [tests/test_agent_ingest.py](../../tests/test_agent_ingest.py)
(new in Phase 7) covers this with two cases (valid JSON, malformed JSON).

### 5.3 — Pin `ollama>=0.4.0` in `install.sh`

**File:** [install.sh:74](../../install.sh)

**Change:** `"ollama>=0.3"` → `"ollama>=0.4.0"`.

**Verification:**
```bash
grep -n "ollama>=" install.sh requirements.txt
# Expected:
# install.sh:74:  "ollama>=0.4.0" \
# requirements.txt:1:ollama>=0.4.0          # GenerateResponse object, not dict (breaking change from 0.3)
```

### 5.4 — systemd path correction

**Files:**
- [systemd/wiki-monitor.service](../../systemd/wiki-monitor.service) — replace all 4 occurrences of `wiki-os` with `wiki-linux`
- [systemd/wiki-sync.service](../../systemd/wiki-sync.service) — replace all 4 occurrences of `wiki-os` with `wiki-linux`
- [systemd/wiki-sync.timer](../../systemd/wiki-sync.timer) — replace 1 occurrence in `Documentation=`

Note: `WIKI_OS_CONFIG=%h/.config/wiki-os/config.json` stays as `wiki-os` —
that's the *config namespace* (matches `~/.config/wiki-os/`), not the repo
path.

**Then add to [install.sh](../../install.sh) after line 146** (the `for unit in ...`
loop that copies units):

```bash
# Patch unit files for the actual install location.
# Default in tracked unit files is %h/wiki-linux. If the repo is somewhere
# else, sed in the correct path.
INSTALL_DEFAULT="%h/wiki-linux"
case "$PROJECT_ROOT" in
  "$HOME/wiki-linux") : ;;  # default, no patch needed
  "$HOME/"*)
    REL="${PROJECT_ROOT#$HOME/}"
    for unit in wiki-monitor.service wiki-sync.service wiki-sync.timer; do
      sed -i "s|$INSTALL_DEFAULT|%h/$REL|g" "$SYSTEMD_DIR/$unit"
    done
    ;;
  *)
    # Repo lives outside $HOME (Codespaces, /opt/, etc).
    for unit in wiki-monitor.service wiki-sync.service wiki-sync.timer; do
      sed -i "s|$INSTALL_DEFAULT|$PROJECT_ROOT|g" "$SYSTEMD_DIR/$unit"
    done
    ;;
esac
```

**Verification:**
```bash
grep -rn "wiki-os" systemd/                  # only in WIKI_OS_CONFIG=%h/.config/wiki-os/...
grep -rn "wiki-linux" systemd/               # appears in ExecStart, WorkingDirectory, PYTHONPATH, Documentation
```

### 5.5 — Document `fix` defaults in `config.json`

**File:** [config.json](../../config.json)

**Change:** Add a `fix` section under `search`:
```json
"fix": {
  "doc_roots": ["~/wiki"],
  "max_snippets": 8,
  "snippet_bytes": 2000
},
```

Code already works without it — this just documents the defaults.

### 5.6 — Fix layout trees in `CLAUDE.md` + `AGENTS.md`

**Files:**
- [CLAUDE.md:25-51](../../CLAUDE.md) — add `src/fix.py`, `src/agent/__init__.py`, `src/agent/ingest.py`. Also fix the directory name in the tree comment from `wiki-os/` to `wiki-linux/`.
- [AGENTS.md:29-61](../../AGENTS.md) — same additions; AGENTS.md already says `wiki-linux/` correctly.

**Verification:**
```bash
grep -A 30 "Repository Layout" CLAUDE.md | grep -E "fix\.py|agent/"
grep -A 30 "Repository Layout" AGENTS.md | grep -E "fix\.py|agent/"
```

### 5.7 — Phase 2 commit

```bash
pytest tests/ -v
# All green. Specifically:
#   tests/test_llm.py::test_valid_path_accepted PASSED
#   ... (all 6 test_llm tests with updated mocks)
#   tests/test_fix.py:: ... (3 tests, unchanged)
#   tests/test_config.py:: ... (existing)
#   tests/test_monitor.py:: ... (existing)

git add src/llm.py src/agent/ingest.py install.sh \
        systemd/wiki-monitor.service systemd/wiki-sync.service systemd/wiki-sync.timer \
        config.json CLAUDE.md AGENTS.md tests/test_llm.py
git commit -m "fix: timeout passing, ollama pin, systemd paths, doc layout

- src/llm.py: lazy module-level ollama.Client(timeout=...) so the
  configured timeout actually reaches the LLM call.
- src/agent/ingest.py: classify_file_content now calls the shared client
  directly instead of routing through llm.answer_question with empty
  snippets (which short-circuits to a fixed string and breaks JSON parse).
- install.sh: pin ollama>=0.4.0 (matches requirements.txt).
- systemd/*: default to %h/wiki-linux; install.sh patches non-default
  install locations.
- config.json: document 'fix' section defaults.
- CLAUDE.md / AGENTS.md: layout trees now list fix.py and agent/."
```

---

## Section 6 — Phase 3: EXPECTATIONS Guarantees, Part A

**Goal:** Make `~/wiki/_archive/`, `~/wiki/_meta/log.md`, and config-lock
behaviour real.

### 6.1 — `~/wiki/_archive/` directory

**Files:**
- [install.sh:99-107](../../install.sh) — extend `mkdir -p` to include `_archive`:
  ```bash
  mkdir -p \
    "$WIKI_ROOT/system/config" \
    "$WIKI_ROOT/system/logs" \
    "$WIKI_ROOT/system/docs" \
    "$WIKI_ROOT/user/notes" \
    "$WIKI_ROOT/user/projects" \
    "$WIKI_ROOT/user/research" \
    "$WIKI_ROOT/_meta" \
    "$WIKI_ROOT/_tmp" \
    "$WIKI_ROOT/_archive"
  ```

- New: `src/archive.py` — small module to move-instead-of-delete:
  ```python
  def archive(path: Path, wiki_root: Path | None = None) -> Path | None:
      """Move path to ~/wiki/_archive/<name>.deleted.<ISO>.

      Used by any code that would otherwise rm/unlink. Returns the new
      path, or None on failure. Calls monitor.record_self_write() so the
      inotify loop ignores both the source disappearance and the archive
      arrival.
      """
  ```

- Update `.gitignore` in `~/wiki/`: keep `_archive/` tracked (the user
  wants to recover from it via git too) — but document this in `_archive/.README`.

### 6.2 — `~/wiki/_meta/log.md` append-only operation log (a.k.a. tasklog)

**File:** `src/tasklog.py` (new — same scope as v1 §2.2 but now justified
by EXPECTATIONS, not v1's "we'll need it" hand-wave).

```python
def append_log(message: str, wiki_root: Path | None = None) -> None:
    """Append one timestamped line to ~/wiki/_meta/log.md.

    Format: '<ISO 8601 UTC>  <message>\n'

    Never raises. Calls monitor.record_self_write() before writing.
    Creates _meta/log.md if absent.
    """

def write_task_note(title: str, body: str, tags: list[str] | None = None,
                    wiki_root: Path | None = None) -> Path | None:
    """Create ~/wiki/_meta/tasks/<slug>.md with frontmatter + body.

    Used by 'wiki task "<title>" "<body>"' (Phase 6.3).
    Calls record_self_write before write. Returns the new path or None.
    """
```

**Wired in (Phase 4 / Phase 6):**
- `src/ingest.py::ingest_file` calls `tasklog.append_log("ingest <src> -> <tgt>")` after success
- `src/lint.py::run_lint` calls `tasklog.append_log("lint: <n> issues")` after writing report
- `src/archive.py::archive` calls `tasklog.append_log("archive <src> -> <archive_path>")`

### 6.3 — Config-lock chmod

**File:** [install.sh:91-94](../../install.sh) — extend the config-copy block:

```bash
if [[ -f "$CONFIG_FILE" ]]; then
  ok "Config already exists at $CONFIG_FILE"
else
  cp "$PROJECT_ROOT/config.json" "$CONFIG_FILE"
  sed -i "s|~/wiki|$WIKI_ROOT|g" "$CONFIG_FILE"
  chmod 0444 "$CONFIG_FILE"   # ← read-only per EXPECTATIONS Guarantee 1
  ok "Config copied to $CONFIG_FILE (read-only — use 'install.sh --reconfigure' to edit)"
  warn "Review $CONFIG_FILE and adjust ollama.model, git.remote, etc."
fi
```

This delivers **EXPECTATIONS Part 5 Guarantee 1** verbatim.

### 6.4 — Phase 3 commit

```bash
pytest tests/ -v                                            # all green
ls -la $WIKI_ROOT/_archive/ 2>/dev/null || true              # may not exist yet on dev box
python3 -c "from src import archive; print(archive)"         # imports

git add install.sh src/archive.py src/tasklog.py
git commit -m "feat(safety): _archive/, _meta/log.md, config-lock chmod

EXPECTATIONS guarantees 1, 2, and 3 are now actually implemented:

  Guarantee 1 (config locked): install.sh chmod 0444 on config copy.
  Guarantee 2 (op log): src/tasklog.py writes _meta/log.md append-only.
  Guarantee 3 (archive): src/archive.py moves files to _archive/ with
                          a timestamped suffix instead of unlinking.

No behavioural change on its own — these are the primitives consumed by
ingest.py, lint.py, and the daemon's future delete handling."
```

---

## Section 7 — Phase 4: Module Extraction & New `src/ingest.py`

**Goal:** Single-file ingest is a first-class module (not a heredoc in
`bin/wiki`) and is shared with the bulk-ingest agent.

### 7.1 — `templates/source_summary.md` (new)

**File:** [templates/source_summary.md](../../templates/source_summary.md)

Jinja2 template for non-`/etc` ingests. Variables match v1 §2.1:
`title`, `source_path`, `updated`, `ingested`, `explanation`, `contents`,
`links`. Mirrors `templates/system_config.md` but with an `## Imported`
section instead of `## Live Contents`.

### 7.2 — `src/ingest.py` (new)

```python
def ingest_file(source: Path, wiki_root: Path | None = None,
                *, dry_run: bool = False) -> Path | None
def ingest_batch(sources: list[Path], wiki_root: Path | None = None,
                 *, dry_run: bool = False) -> dict[str, int]
def render_page(source_path: Path, title: str, explanation: str,
                contents: str, updated: str, links: list[str]) -> str
```

`render_page()` is the **first** caller of Jinja2 in the project.
Importable from `src/agent/ingest.py` to replace its inline
`format_wiki_page()`.

`__main__` block: `python3 -m src.ingest <file> [--dry-run]`.

### 7.3 — `src/agent/ingest.py::format_wiki_page` deletion

**File:** [src/agent/ingest.py:328-355](../../src/agent/ingest.py)

Replace `format_wiki_page()` body with a one-liner delegate:
```python
from src.ingest import render_page
# ... in execute_proposal:
page_content = render_page(
    source_path=source,
    title=source.stem,
    explanation="(imported by agent scan)",
    contents=content,
    updated=now,
    links=[],
)
```

### 7.4 — Phase 4 commit

```bash
pytest tests/ -v
python3 -m src.ingest --help                                 # smoke
git add templates/source_summary.md src/ingest.py src/agent/ingest.py
git commit -m "feat(ingest): extract render_page to src/ingest.py + Jinja2

Single-file ingest is now its own module. Both src/agent/ingest.py
(bulk scan) and bin/wiki cmd_ingest (single file, Phase 6) call into
src/ingest.py::render_page so there is one source of truth for the
ingested-page template."
```

---

## Section 8 — Phase 5: EXPECTATIONS Guarantees, Part B

**Goal:** `install.sh --uninstall`, `install.sh --reconfigure`, and a
`wiki status` that matches the format EXPECTATIONS shows.

### 8.1 — `install.sh --uninstall`

**File:** [install.sh](../../install.sh)

**Add at the top (after `set -euo pipefail`):**
```bash
ACTION="${1:-install}"
shift || true

case "$ACTION" in
  install) : ;;     # default path — fall through
  --uninstall) action_uninstall; exit 0 ;;
  --reconfigure) action_reconfigure; exit 0 ;;
  -h|--help|help)
    cat <<EOF
install.sh — Wiki-Linux installer

Usage:
  install.sh                  Install (idempotent)
  install.sh --uninstall      Remove daemon + config; KEEPS ~/wiki/
  install.sh --reconfigure    Unlock config, open in \$EDITOR, re-lock
EOF
    exit 0 ;;
  *)
    echo "Unknown action: $ACTION" >&2
    exit 2 ;;
esac
```

**Add functions:**
```bash
action_uninstall() {
  step "Uninstalling Wiki-Linux"
  systemctl --user disable --now wiki-monitor.service 2>/dev/null || true
  systemctl --user disable --now wiki-sync.timer 2>/dev/null || true
  for unit in wiki-monitor.service wiki-sync.service wiki-sync.timer; do
    rm -f "$SYSTEMD_DIR/$unit"
  done
  systemctl --user daemon-reload
  rm -f "$LOCAL_BIN/wiki"
  rm -rf "$CONFIG_DIR"
  ok "Removed daemon + config."
  warn "Your wiki is preserved at: $WIKI_ROOT"
  warn "To delete it manually: rm -rf $WIKI_ROOT  (NOT recommended — git history dies)"
}

action_reconfigure() {
  step "Reconfiguring Wiki-Linux"
  if [[ ! -f "$CONFIG_FILE" ]]; then
    fail "No config at $CONFIG_FILE. Run install.sh first."
  fi
  chmod u+w "$CONFIG_FILE"
  "${EDITOR:-nvim}" "$CONFIG_FILE"
  chmod 0444 "$CONFIG_FILE"
  ok "Config edited and re-locked."
}
```

This delivers **EXPECTATIONS Part 5 Guarantee 1 §256** ("install-time
script (kept for rollback) `bash ~/wiki-linux/install.sh --reconfigure`")
and **EXPECTATIONS Part 6 Option 3** verbatim.

### 8.2 — `bin/wiki status` upgrade

**File:** [bin/wiki:142-169](../../bin/wiki)

EXPECTATIONS Part 2 Tool 1 §97 promises:
```
$ wiki status
Daemon status: running (PID 12345)
Wiki size: 47 pages, 150 KB
Last sync: 2026-05-01 15:23:45 UTC
Git remote: origin (https://github.com/sourovdeb/wiki-linux.git)
```

Current output mostly matches but doesn't show wiki size or last sync
explicitly. **Update `cmd_status` to format output exactly as documented:**

```bash
cmd_status() {
  echo "=== Wiki-Linux Status ==="

  # Daemon status
  if systemctl --user is-active --quiet wiki-monitor 2>/dev/null; then
    pid="$(systemctl --user show -p MainPID --value wiki-monitor)"
    echo "Daemon status: running (PID $pid)"
  else
    echo "Daemon status: not running"
  fi

  # Wiki size
  pages="$(find "$WIKI_ROOT" -name '*.md' 2>/dev/null | wc -l)"
  size="$(du -sh "$WIKI_ROOT" 2>/dev/null | cut -f1)"
  echo "Wiki size: $pages pages, $size"

  # Last sync (= last commit timestamp)
  if [[ -d "$WIKI_ROOT/.git" ]]; then
    last="$(git -C "$WIKI_ROOT" log -1 --format='%ci' 2>/dev/null || echo 'unknown')"
    echo "Last sync: $last"
    remote="$(git -C "$WIKI_ROOT" remote get-url origin 2>/dev/null || echo 'none')"
    echo "Git remote: origin ($remote)"
  fi

  echo ""
  echo "=== Recent Commits ==="
  git -C "$WIKI_ROOT" log --oneline -5 2>/dev/null || echo "(no git history yet)"
}
```

### 8.3 — Phase 5 commit

```bash
bash install.sh --help                                       # shows usage
PATH="$PWD/bin:$PATH" wiki status                            # new format
git add install.sh bin/wiki
git commit -m "feat(safety): install.sh --uninstall/--reconfigure, wiki status format

EXPECTATIONS Part 6 Option 3 (uninstall keeps ~/wiki/) and Part 5
Guarantee 1 (chmod-based config lock + reconfigure flow) are now
implemented.

bin/wiki status output matches the format documented in EXPECTATIONS
Part 2 Tool 1: daemon PID, wiki size, last sync, git remote."
```

---

## Section 9 — Phase 6: Lint Module + CLI Wiring

**Goal:** `wiki lint`, `wiki ingest`, `wiki fix`, `wiki task` actually
work end-to-end.

### 9.1 — `src/lint.py` (new)

Public:
```python
def run_lint(wiki_root: Path | None = None) -> dict
def write_lint_report(results: dict, wiki_root: Path | None = None) -> Path | None
```

Implements 5 checks per `AGENT_PLAYBOOK.md` §6:
1. Broken `[[wikilinks]]`
2. Orphan pages (no incoming links)
3. Pages without `source:` frontmatter
4. Pages older than `cfg["lint"]["stale_days"]` (default 180)
5. Duplicate `title:` values

Skip `_meta/`, `_tmp/`, `_archive/`, `.obsidian/`, `.git/`. Output to
`_meta/lint-report-<YYYY-MM-DD>.md`. Append summary to `_meta/log.md` via
`tasklog.append_log()`.

`__main__` block: `python3 -m src.lint`.

### 9.2 — Add `lint` config section to [config.json](../../config.json)

```json
"lint": {
  "stale_days": 180,
  "skip_dirs": ["_meta", "_tmp", "_archive", ".obsidian", ".git"]
},
```

### 9.3 — `bin/wiki` wiring

| Subcommand | Handler | Dispatches to | Notes |
|---|---|---|---|
| `ingest <file> [--dry-run]` | `cmd_ingest()` | `python3 -m src.ingest "$file"` | New |
| `lint` | `cmd_lint()` | `python3 -m src.lint` | New |
| `fix "<problem>"` | `cmd_fix()` | `python3 -m src.fix "$problem"` | New (module exists) |
| `task "<title>" ["<body>"]` | `cmd_task()` | one-line python: `from src.tasklog import write_task_note; write_task_note(...)` | New |
| `reprocess <file>` | (alias to `cmd_ingest`) | `cmd_ingest "$@"` | Backwards-compat alias for one release |

Update `_usage()` listing accordingly. EXPECTATIONS Part 2 Tool 1 already
shows the user `wiki lint` — now it works.

### 9.4 — Phase 6 commit

```bash
pytest tests/ -v
PATH="$PWD/bin:$PATH" wiki help | grep -E "ingest|lint|fix|task"
PATH="$PWD/bin:$PATH" wiki lint                              # writes a report (or empty if no wiki)
git add src/lint.py config.json bin/wiki
git commit -m "feat(cli): wire ingest, lint, fix, task subcommands

src/lint.py implements 5 checks from AGENT_PLAYBOOK.md §6 and writes
_meta/lint-report-<date>.md.

bin/wiki gains: ingest, lint, fix, task. 'reprocess' kept as alias
for one release for backwards compatibility."
```

---

## Section 10 — Phase 7: Tests

**Mock pattern after Phase 5.1:** `monkeypatch.setattr("src.llm._client", fake)`.

| Test file | Scope | Cases |
|---|---|---|
| [tests/test_llm.py](../../tests/test_llm.py) (update) | Re-target mocks per 5.1 | 6 existing |
| `tests/test_archive.py` (new) | `archive()` moves and never unlinks | 3 cases |
| `tests/test_tasklog.py` (new) | append-only log; task notes; record_self_write called | 6 cases |
| `tests/test_ingest.py` (new) | ingest_file; path-escape rejection; dry-run; render_page | 6 cases |
| `tests/test_lint.py` (new) | each of the 5 checks + report writing | 8 cases |
| `tests/test_agent_ingest.py` (new) | `classify_file_content` post-5.2 | 3 cases |
| `tests/test_install_uninstall.sh` (new — bash) | `install.sh --uninstall` removes config + units, keeps wiki | 1 e2e case (skipped on CI without systemd) |

**Total:** ~32 new tests + 6 updated. All Ollama-mocked. No live LLM.

### 10.1 — Phase 7 commit

```bash
pytest tests/ -v --tb=short                                   # all green
git add tests/
git commit -m "test: cover archive, tasklog, ingest, lint, agent_ingest, install --uninstall"
```

---

## Section 11 — Phase 8: Verification & Integration

```bash
# All tests pass with no live Ollama
pytest tests/ -v --tb=short

# Version consistency
grep -n "ollama>=" requirements.txt install.sh
# Both must show >=0.4.0

# systemd path consistency
grep -rn "wiki-os" systemd/
# Only WIKI_OS_CONFIG=%h/.config/wiki-os/config.json should remain
grep -rn "wiki-linux" systemd/
# All ExecStart, WorkingDirectory, PYTHONPATH, Documentation should match

# CLI smoke
export PYTHONPATH="$PWD"
export WIKI_OS_CONFIG="$PWD/config.json"
PATH="$PWD/bin:$PATH"

wiki help | grep -E "ingest|lint|fix|task|reprocess"
wiki status                                                  # matches EXPECTATIONS format
wiki lint                                                    # writes _meta/lint-report-*.md

# Template rendering
python3 -c "
import jinja2, pathlib
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
t = env.get_template('source_summary.md')
print(t.render(title='T', source_path='/etc/t', updated='2026-05-01',
               ingested='2026-05-01', explanation='x', contents='a=1', links=[]))
"

# install.sh smoke (in a dry-run-able way)
bash install.sh --help

# EXPECTATIONS guarantee verification (manual)
[[ -d "$HOME/wiki/_archive" ]] && echo "✓ Guarantee 3 (_archive/) exists"
[[ -f "$HOME/wiki/_meta/log.md" ]] && echo "✓ Guarantee 2 (log.md) exists"
[[ "$(stat -c %a $HOME/.config/wiki-os/config.json 2>/dev/null)" == "444" ]] \
  && echo "✓ Guarantee 1 (config locked) enforced"
```

If any check fails, **the failing phase's commit is the rollback target**:

```bash
# Bug-fix regression?
git revert <phase-2-commit>

# Safety primitive broken?
git revert <phase-3-commit>

# CLI broken?
git revert <phase-6-commit>
```

---

## Section 12 — Files Touched (final manifest)

| Action | File | Phase |
|---|---|---|
| Stage | [src/fix.py](../../src/fix.py), [tests/test_fix.py](../../tests/test_fix.py) | 1 |
| Edit | [src/llm.py](../../src/llm.py) | 2 |
| Edit | [src/agent/ingest.py](../../src/agent/ingest.py) | 2, 4 |
| Edit | [install.sh](../../install.sh) | 2, 3, 5 |
| Edit | [systemd/wiki-monitor.service](../../systemd/wiki-monitor.service) | 2 |
| Edit | [systemd/wiki-sync.service](../../systemd/wiki-sync.service) | 2 |
| Edit | [systemd/wiki-sync.timer](../../systemd/wiki-sync.timer) | 2 |
| Edit | [config.json](../../config.json) | 2, 6 |
| Edit | [CLAUDE.md](../../CLAUDE.md), [AGENTS.md](../../AGENTS.md) | 2 |
| Edit | [tests/test_llm.py](../../tests/test_llm.py) | 2 |
| New  | `src/archive.py` | 3 |
| New  | `src/tasklog.py` | 3 |
| New  | `templates/source_summary.md` | 4 |
| New  | `src/ingest.py` | 4 |
| New  | `src/lint.py` | 6 |
| Edit | [bin/wiki](../../bin/wiki) | 5, 6 |
| New  | `tests/test_archive.py` | 7 |
| New  | `tests/test_tasklog.py` | 7 |
| New  | `tests/test_ingest.py` | 7 |
| New  | `tests/test_lint.py` | 7 |
| New  | `tests/test_agent_ingest.py` | 7 |
| New  | `tests/test_install_uninstall.sh` | 7 |

**Net:** 11 edits + 11 new = **22 files** (vs v1's 27). Same surface area,
better expectations coverage.

**Deferred (not counted):** `src/bootstrap.py`, `tests/test_bootstrap.py`,
`ARCHITECTURE.md`, `USER_GUIDE.md`, `WIKI_SCHEMA.md` — only built on
user request.

---

## Section 13 — Dependency Graph

```
Phase 0  decisions
   │
   ▼
Phase 1  stage untracked            ◄── independent
   │
   ▼
Phase 2  bug fixes (5.1-5.7)
   │   └── 5.1 (llm.py timeout)  ─────────┐
   │   └── 5.2 (agent/ingest.py)  ◄──── needs 5.1
   │   └── 5.3 (install.sh ollama pin)
   │   └── 5.4 (systemd paths)
   │   └── 5.5 (config.json fix section)
   │   └── 5.6 (docs trees)
   ▼
Phase 3  safety primitives
   │   └── 6.1 _archive/ (install.sh + src/archive.py)
   │   └── 6.2 src/tasklog.py
   │   └── 6.3 chmod 0444 config (install.sh)
   ▼
Phase 4  module extraction
   │   └── 7.1 templates/source_summary.md
   │   └── 7.2 src/ingest.py        ◄── needs 6.2 (tasklog)
   │   └── 7.3 agent/ingest.py refactor
   ▼
Phase 5  guarantees B
   │   └── 8.1 install.sh --uninstall/--reconfigure
   │   └── 8.2 wiki status format upgrade
   ▼
Phase 6  lint + CLI wiring
   │   └── 9.1 src/lint.py            ◄── needs 6.2 (tasklog)
   │   └── 9.2 config.json lint section
   │   └── 9.3 bin/wiki subcommands   ◄── needs 7.2 (ingest), 9.1 (lint)
   ▼
Phase 7  tests
   ▼
Phase 8  verification (no commit)
```

---

## Section 14 — Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| `monkeypatch.setattr("src.llm._client", ...)` doesn't bypass lazy init | Medium | Add `monkeypatch.setattr("src.llm._client", fake)` *and* `monkeypatch.setattr("src.llm._get_client", lambda: fake)` to be explicit |
| `chmod 0444` blocks user from reading their own config | Low | 0444 is read-for-everyone; user can still read |
| `install.sh --uninstall` deletes ~/wiki by accident | Low | Plan explicitly preserves `$WIKI_ROOT`; a regression test (`tests/test_install_uninstall.sh`) verifies this |
| `_archive/` grows unbounded | Medium | Out of scope for v2; document in code comment that the user should periodically prune. **Future:** `wiki gc` subcommand. |
| Refactoring `src/agent/ingest.py::format_wiki_page` breaks the agent | Medium | The agent has zero tests today (we add `test_agent_ingest.py` in Phase 7). Run `python3 -m src.agent.ingest --scan-home --dry-run` against a tiny temp dir before commit. |
| systemd path patching breaks on a Codespace install | High | The fall-through `*) sed -i "s|...|$PROJECT_ROOT|g"` branch handles it; verify in a Codespace |
| Test file count balloons context for future agents reading the repo | Low | Each new test file < 200 LoC; total is comparable to v1's plan |

---

## Section 15 — Comparison Table: v1 vs v2

| Dimension | v1 | v2 | Winner |
|---|---|---|---|
| Bugs fixed | 6 | 6 (same) + 1 untracked | tie+1 |
| EXPECTATIONS guarantees implemented | 0 (assumed pre-existing) | 6 | **v2** |
| New modules | 4 (`tasklog`, `bootstrap`, `ingest`, `lint`) | 4 (`tasklog`, `archive`, `ingest`, `lint`) — `bootstrap` swapped for `archive` | v2 (archive is in EXPECTATIONS, bootstrap isn't) |
| New docs | 3 | 0 (deferred) | **v2** |
| New CLI subcommands | 5 | 4 (no `bootstrap`); `reprocess` aliased to `ingest` instead of left orphaned | v2 |
| install.sh enhancements | 1 (sed for systemd) | 4 (sed, chmod, --uninstall, --reconfigure) | **v2** |
| Total files touched | 27 | 22 | **v2** |
| Commits | 1 (implicit) | 7 (one per phase, atomic revert) | **v2** |
| Risk register | absent | present (§14) | **v2** |
| Mock-target swap scope | "all 6 tests" (overstated) | 6 tests, one-line each via `monkeypatch.setattr` on `_client` | **v2** |

**Conclusion:** v2 fixes everything v1 fixed, deletes work that didn't
matter, and adds the work that EXPECTATIONS requires. Same total file
count, better outcome.

---

## Section 16 — One-Page Summary

```
WHAT THIS PLAN DOES
1. Stage src/fix.py + tests/test_fix.py.                              [Phase 1]
2. Fix 6 verified bugs: llm timeout, agent ingest, ollama pin,
   systemd paths, config docs, layout trees.                          [Phase 2]
3. Implement EXPECTATIONS guarantees:
   - _archive/ (move-instead-of-delete)                               [Phase 3]
   - _meta/log.md (append-only operation log)                         [Phase 3]
   - chmod 0444 config (read-only)                                    [Phase 3]
   - install.sh --uninstall / --reconfigure                           [Phase 5]
   - wiki status format match                                         [Phase 5]
4. Extract render_page; new src/ingest.py; refactor agent/ingest.py.  [Phase 4]
5. New src/lint.py; wire ingest/lint/fix/task/reprocess in bin/wiki.  [Phase 6]
6. Tests: 32 new + 6 updated, all Ollama-mocked.                      [Phase 7]
7. Verify everything; one commit per phase, easy rollback.            [Phase 8]

WHAT THIS PLAN DOES NOT DO
- src/bootstrap.py — install.sh already bootstraps.                   [DEFERRED]
- ARCHITECTURE.md / USER_GUIDE.md / WIKI_SCHEMA.md.                   [DEFERRED]
  Repo already has 11 docs; new docs only on user request.

PHASE 0 BLOCKERS (need user OK)
0.1 llm.py timeout: module-level Client (test-breaking, simpler) — DEFAULT YES
0.2 _archive/ now (Phase 3) — DEFAULT YES
0.3 install.sh --uninstall now (Phase 5) — DEFAULT YES
0.4 install.sh --reconfigure now (Phase 5) — DEFAULT YES
0.5 Defer Phase 9 + Phase 10 — DEFAULT YES
```
