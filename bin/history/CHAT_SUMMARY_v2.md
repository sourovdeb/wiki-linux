# Wiki-Linux Planning Session — v2 Chat Summary

**Date:** 2026-05-01
**Session type:** Plan revision (v1 → v2) after EXPECTATIONS.md alignment
**Status:** v2 plan written and saved as
[EXECUTION_PLAN_v2.md](EXECUTION_PLAN_v2.md). Awaiting Phase 0 decisions
before any code changes.

---

## What the User Asked

Three asks in one conversation:

1. **"Investigate `bin/history/`, `AGENTS.md`, `CLAUDE.md`,
   `AGENT_PLAYBOOK.md` and revise the execution plan. Be meticulous and
   break it down."**
2. **"Will this plan be better than the expectation
   (`EXPECTATIONS.md`)?"** — followed by four near-identical
   reformulations of "better/efficient option?".
3. **"Save your elaborate execution plan here and save chat history
   there"** (both into `bin/history/`).

The repeated question in #2 was treated as a signal: *don't pad, prove
the plan is genuinely better*. The v2 plan responds to that by
quantifying the gap between v1 and EXPECTATIONS.md.

---

## What I Did

### Step 1 — Read everything in `bin/history/`

| File | Role | Verdict |
|---|---|---|
| [EXECUTION_PLAN.md](EXECUTION_PLAN.md) (v1) | Code-correctness plan | Solid bug analysis; missed 6 EXPECTATIONS guarantees; over-spec'd new docs |
| [CHAT_SUMMARY.md](CHAT_SUMMARY.md) | v1 summary | Accurate summary of v1, but v1 itself was incomplete |
| [archwiki.md](archwiki.md) | ArchWiki integration notes | Background context only — duplicate of `references/archwiki.md` |
| [karpathy-llm-wiki.md](karpathy-llm-wiki.md) | Karpathy gist mirror | Background context only — duplicate of `references/karpathy-llm-wiki.md` |

The two duplicate `references/` files in `bin/history/` look like a
working copy from when the plan was first drafted. Not load-bearing.

### Step 2 — Verified every claim in v1 against the live repo

Read:
- [src/llm.py](../../src/llm.py) — confirmed dead `timeout` variable at L97
- [src/agent/ingest.py](../../src/agent/ingest.py) — confirmed broken
  `classify_file_content` at L96
- [install.sh](../../install.sh) — confirmed `ollama>=0.3` at L74
- [systemd/*.{service,timer}](../../systemd/) — confirmed `%h/wiki-os/` typo
- [config.json](../../config.json) — confirmed `fix` section absent
- [src/fix.py](../../src/fix.py), [tests/test_fix.py](../../tests/test_fix.py)
  — confirmed both untracked
- [bin/wiki](../../bin/wiki) — confirmed `cmd_reprocess` already exists
  (overlaps with v1's proposed `cmd_ingest`)
- [tests/test_llm.py](../../tests/test_llm.py) — confirmed 5 of 6 tests
  use `patch("src.llm.ollama.generate")` (v1 said all 6)
- [src/monitor.py](../../src/monitor.py) — confirmed self-write
  suppression is correct
- [templates/system_config.md](../../templates/system_config.md) —
  confirmed it's the only template; no `source_summary.md` yet

### Step 3 — Read [EXPECTATIONS.md](../../EXPECTATIONS.md) (the user
contract)

This was the inflection point. EXPECTATIONS makes 12 concrete promises
to the user; **6 of them are not implemented in the codebase** and v1
did not address any of them. Specifically missing:

1. `~/wiki/_archive/` directory (Part 1, Part 5 Guarantee 3)
2. `~/wiki/_meta/log.md` append-only log (Part 1)
3. `chmod 0444` on `config.json` after install (Part 5 Guarantee 1)
4. `install.sh --uninstall` flag (Part 6 Option 3)
5. `install.sh --reconfigure` flag (Part 5 Guarantee 1 §256)
6. `wiki lint` subcommand (Part 2 Tool 1)

The other 6 guarantees (`/etc` read-only, systemd as user, git history,
self-write suppression, etc.) **are** implemented today.

### Step 4 — Wrote v2 plan

[EXECUTION_PLAN_v2.md](EXECUTION_PLAN_v2.md). Structure:

```
Phase 0  Decisions to confirm with user (5 questions)
Phase 1  Stage untracked files (1 commit)
Phase 2  Bug fixes (1 commit, 6 sub-tasks)
Phase 3  Safety primitives — _archive, log, chmod (1 commit)
Phase 4  Module extraction — Jinja2 ingest (1 commit)
Phase 5  install.sh --uninstall/--reconfigure + wiki status (1 commit)
Phase 6  src/lint.py + bin/wiki wiring (1 commit)
Phase 7  Tests (1 commit)
Phase 8  Verification (no commit)
DEFERRED: src/bootstrap.py, 3 new doc files
```

22 files touched (vs v1's 27). 6 EXPECTATIONS guarantees implemented (vs
v1's 0). Same bug fixes. 7 atomic commits with revert paths.

---

## Key Differences v1 → v2

| Dimension | v1 | v2 |
|---|---|---|
| EXPECTATIONS guarantees implemented | 0 (assumed already done) | 6 |
| Bug count | 6 | 6 + 1 untracked-file fix |
| New modules | tasklog, **bootstrap**, ingest, lint | tasklog, **archive**, ingest, lint |
| New CLI subcommands | 5 (`ingest`, `lint`, `fix`, `task`, `bootstrap`) | 4 (`ingest`, `lint`, `fix`, `task`) + `reprocess` alias |
| install.sh changes | 1 (sed systemd path) | 4 (sed, chmod, --uninstall, --reconfigure) |
| New docs | 3 (`ARCHITECTURE`, `USER_GUIDE`, `WIKI_SCHEMA`) | 0 (deferred) |
| Test mock-swap claim | "all 6 tests" (wrong) | 6 tests, 1-line each via `monkeypatch.setattr("src.llm._client", fake)` |
| Commits | 1 implicit | 7 atomic |
| Risk register | absent | present |

**Why v2 is "the better, efficient option" the user asked for:** v1
spent budget on speculative additions (`bootstrap.py`, 3 docs). v2
redirects that budget to user-visible safety promises in EXPECTATIONS.md
that are currently broken. Same total file count; different ratio of
ROI.

---

## Decisions Pending (Phase 0 of v2)

User must confirm or override defaults before Phase 1 begins:

| # | Question | Default |
|---|---|---|
| 0.1 | `llm.py` timeout fix style: module-level `Client` (test-breaking, ~6 mock swaps) or `options=` kwarg (untested) | Module-level `Client` |
| 0.2 | Implement `_archive/` (EXPECTATIONS Guarantee 3) now? | Yes (Phase 3) |
| 0.3 | Implement `install.sh --uninstall` now? | Yes (Phase 5) |
| 0.4 | Implement `install.sh --reconfigure` now? | Yes (Phase 5) |
| 0.5 | Defer `src/bootstrap.py` and 3 new docs? | Yes |

If the user says "go" without further input, I'll apply all defaults.

---

## What Comes Next (Once Phase 0 Clears)

1. **Phase 1:** `git add src/fix.py tests/test_fix.py && git commit`
2. **Phase 2:** Apply 6 bug fixes (5.1–5.6 in v2 §5), commit
3. **Phase 3:** `_archive/`, `tasklog.py`, chmod lock, commit
4. **Phase 4:** Jinja2 + `src/ingest.py` extraction, commit
5. **Phase 5:** `install.sh --uninstall/--reconfigure`, `wiki status`
   format upgrade, commit
6. **Phase 6:** `src/lint.py` + `bin/wiki` subcommands, commit
7. **Phase 7:** Tests, commit
8. **Phase 8:** Run full verification suite per v2 §11

Each phase follows `AGENT_PLAYBOOK.md` §2.3: state phase, do one task,
report, wait for "next".

---

## Files in `bin/history/` After This Session

| File | Status |
|---|---|
| [EXECUTION_PLAN.md](EXECUTION_PLAN.md) | Superseded by v2 (kept for diff history) |
| [CHAT_SUMMARY.md](CHAT_SUMMARY.md) | Superseded by v2 (kept for diff history) |
| [EXECUTION_PLAN_v2.md](EXECUTION_PLAN_v2.md) | **Current** — implementation plan |
| [CHAT_SUMMARY_v2.md](CHAT_SUMMARY_v2.md) | **Current** — this file |
| [archwiki.md](archwiki.md), [karpathy-llm-wiki.md](karpathy-llm-wiki.md) | Working-copy duplicates of `references/`; safe to delete if you want |

---

## One-Sentence Summary

**v1 fixed code; v2 fixes code AND keeps the safety promises EXPECTATIONS.md
already made to the user.**
