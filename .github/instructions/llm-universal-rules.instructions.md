---
description: "Universal LLM rules for all environments, tools, and contexts in wiki-linux and any fork. Apply always."
name: "LLM Universal Rules"
applyTo: "**"
---

# LLM Universal Rules

**Scope**: Apply to all LLMs, all environments (local, cloud, Docker), all contexts (Copilot, Claude, Cline, web, CLI).

## 1. Token Efficiency (ALWAYS)
- Keep responses short; omit unnecessary context.
- Use bullet points over prose.
- Combine independent read-only operations in parallel batches.
- Avoid repeating unchanged plans or sections.
- Report only important outcomes: what changed, verified, remains.

## 2. Research Before Start (MANDATORY)
- Read `.github/instructions/` for project-specific guidance.
- Check `_meta/task-log/` and `_meta/log.md` for recent context and status.
- Skim `README.md`, `START-HERE.md`, and `GUIDE.md` for scope.
- Verify git branch and working tree state before changes.
- Do NOT speculate; gather facts first.

## 3. Automate Over Manual (PREFERRED)
- Create surgical scripts (`set -euo pipefail`) for multi-step operations.
- One script = one focused objective.
- Include pre-checks, targeted changes, post-verification.
- Save scripts in `WIKI-TOOLS/handoff/` for reuse.
- Keep side effects narrow; idempotent where possible.

## 4. Surgical Precision (REQUIRED)
- Single responsibility per tool call.
- Exact file paths; no guessing.
- Minimal context in edit strings (3-5 lines before/after).
- Verify results: exit codes, key state, expected artifacts.
- If partial, fine-tune and rerun only affected steps.

## 5. Communication Style (ALWAYS)
- Concise updates; no redundant summaries.
- Omit tool names from responses.
- Report deltas, not full state.
- After parallel batches: brief progress, then next step.
- After 3–5 tool calls or 3+ file edits: progress cadence checkpoint.

## 6. Commitment to Completion (ALWAYS)
- Keep working until the user's request is fully resolved.
- Only stop if solved or genuinely blocked.
- If ambiguous: infer the most useful action and proceed.
- Use task tracking (`manage_todo_list`) for multi-step work.
- Call `task_complete` with summary before yielding.

## 7. Document Decisions (BEST PRACTICE)
- Save LLM process playbooks to `.github/instructions/` for future runs.
- Record decisions, constraints, and lessons learned.
- Keep `.github/instructions/` as the canonical source for this codebase.

## 8. Git Workflow (FOR REPOS WITH GIT)
- Check branch and uncommitted state before major work.
- Commit changes with clear messages: what changed, why.
- Push after each logical checkpoint (not just at end).
- Include task logs in commits: `_meta/task-log/YYYY-MM-DD/hhmmss-*.md`.

---

**Enforcement**: Treat these rules as immutable constraints. Apply to every interaction, every tool call, every response. When in doubt, choose the option that saves tokens, automates repetition, and maintains precision.
