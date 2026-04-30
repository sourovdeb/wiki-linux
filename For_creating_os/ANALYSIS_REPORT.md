# Analysis Report — Wiki-OS (`sourovdeb/wiki-linux`)

Date: 2026-04-30

## Scope
This report reviews the attached Wiki-OS codebase and records verification-first recommendations for a coding agent.

## Repository Profile
- Project type: Local-first Linux daemon + CLI
- Primary runtime language: Python 3.11+
- Additional tooling: Shell scripts + systemd user units
- LLM runtime: local Ollama Python client

## What Works Well
1. Clear architecture split (`config`, `monitor`, `llm`, `indexer`, `search`, `sync`).
2. Good offline-first and user-level daemon model.
3. Uses `format="json"` for structured LLM output in page generation.
4. Includes self-write suppression to avoid feedback loops.
5. Configuration centralization via `src/config.py` is mostly respected.

## Gaps / Risks Found
1. **Path safety check in `src/llm.py`**
   - Current check uses string prefix compare:
     - `str(resolved).startswith(str(wiki_root.resolve()))`
   - Risk: prefix tricks can bypass intent in edge cases.
   - Recommendation: use `resolved.is_relative_to(wiki_root.resolve())` with fallback for older Python.

2. **Ollama timeout not enforced in calls**
   - `timeout_seconds` is loaded but not passed to the client call.
   - Recommendation: pass timeout explicitly where supported, or implement guard in caller.

3. **`src/search.py` has an unused variable**
   - `current_match` declared but never used.
   - Recommendation: remove to reduce noise.

4. **Potential startup fragility if config missing**
   - `cfg = {}` fallback exists, but many modules index `cfg["wiki"]` directly.
   - Recommendation: validate config at startup and fail fast with actionable message.

5. **Installer branch assumption**
   - `git init -b main` in installer may conflict with user preference.
   - Recommendation: keep configurable via `config.json` or detect existing defaults.

## Verification-First Coding Agent Instruction Addendum
Add these mandatory rules:
1. Do not anticipate hidden state. Verify every assumption through code or command output.
2. Before each write operation, verify target path/repo/branch exists and is intended.
3. For security-sensitive checks (path containment, command execution, permissions), prefer explicit APIs over string heuristics.
4. After each change, run a concrete validation step and record result.
5. If verification fails, stop and report instead of continuing optimistically.

## Suggested Immediate Actions
1. Harden path containment check in `src/llm.py`.
2. Apply timeout handling for Ollama calls.
3. Add/expand tests for:
   - path escape attempts
   - malformed JSON responses
   - self-write suppression behavior
4. Add a short “Verification Checklist” section to `AGENTS.md`.

## Conclusion
The project is well-structured and close to production-usable for local personal workflows. The highest-value improvements are security-check hardening and strict verification-first operational discipline.
