# Wiki-OS Planning Session Summary

**Date:** 2026-05-01  
**Session Type:** Full codebase audit and execution planning  
**Status:** Plan approved and ready for implementation

## Overview

Conducted a comprehensive review of the Wiki-OS project against its own documentation (`CLAUDE.md`, `AGENTS.md`, `AGENT_PLAYBOOK.md`, `EXPECTATIONS.md`). Identified 6 bugs, 12 missing files, and design gaps. Created a phased 6-phase execution plan to close all gaps.

## Key Findings

### Bugs (Phase 1)
1. **`src/llm.py`** — Dead `timeout` variable never passed to LLM calls
2. **`src/agent/ingest.py`** — Broken `classify_file_content()` (RAG call with empty snippets)
3. **`install.sh`** — Version mismatch (`ollama>=0.3` vs `ollama>=0.4.0`)
4. **Systemd units** — Hardcoded `wiki-os` path instead of `wiki-linux`
5. **`config.json`** — Missing `fix` section referenced by `src/fix.py`
6. **Docs** — `src/fix.py` and `src/agent/ingest.py` not listed in layout

### Missing Files (Phases 2–5)

#### New Core Modules (Phase 2)
- `src/tasklog.py` — Master log writer (used by all other new modules)
- `src/bootstrap.py` — Wiki directory initialization
- `src/ingest.py` — Single-file ingest (distinct from agent version)
- `src/lint.py` — Wiki health-check report writer
- `templates/source_summary.md` — Jinja2 template for ingested source pages

#### CLI Wiring (Phase 3)
- Add subcommands to `bin/wiki`: `ingest`, `lint`, `fix`, `task`, `bootstrap`

#### Tests (Phase 4)
- `tests/test_ingest.py` — 6 test cases
- `tests/test_lint.py` — 8 test cases
- `tests/test_tasklog.py` — 6 test cases
- `tests/test_bootstrap.py` — 6 test cases
- Update `tests/test_llm.py` — mock target change (6 existing tests)

#### Documentation (Phase 5)
- `ARCHITECTURE.md` — System design and data flow
- `USER_GUIDE.md` — User-facing operations guide
- `WIKI_SCHEMA.md` — Data schema and conventions

## Critical Decisions

1. **Two ingest modules:** `src/agent/ingest.py` (bulk scan) vs `src/ingest.py` (single file)
2. **Jinja2 rendering:** `src/ingest.py` is the first module to actually use Jinja2 templates
3. **Ollama Client pattern:** Phase 1.1 establishes the correct timeout pattern for all new code
4. **Mock targets:** All new tests use `patch("src.llm.ollama.Client")` instead of `patch("src.llm.ollama.generate")`
5. **No subprocess for Ollama:** Direct `ollama.Client()` API only; subprocess reserved for `git` (already done in `sync.py`)

## Execution Order

```
Phase 1: Fix bugs (6 changes)
  ↓
Phase 2: Create new modules (tasklog → bootstrap → ingest → lint)
  ↓
Phase 3: Wire CLI subcommands
  ↓
Phase 4: Write all tests (can TDD alongside Phase 2)
  ↓
Phase 5: Write documentation (independent)
  ↓
Phase 6: Integration verification
```

## Verification Strategy

- All tests pass with zero live Ollama calls (fully mocked)
- CLI smoke tests for all 5 new subcommands
- Version consistency check (ollama, paths, config)
- Template rendering verification
- Self-write suppression validation

## Files Modified/Created

**Total changes:** 27 files (6 bug fixes, 4 new modules, 1 new template, 5 CLI commands, 5 new tests, 3 docs)

**All changes respect:** WIKI_ROOT constraint, no writes to `/etc/`, Python 3.11+, pathlib, logging, no dependencies added, self-write suppression, config-driven values.

## Next Step

Begin Phase 1 implementation: Fix the 6 bugs in sequence (1.1–1.6).
