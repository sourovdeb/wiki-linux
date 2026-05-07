# AGENT_PLAYBOOK.md — Internal Instructions for Any AI Agent

> **Audience:** any LLM agent operating on this repo, from TinyLlama 1.1B
> through Claude Opus, Codex, Mistral, Llama 3, Gemini, GPT-4/5.
>
> **Why this file exists:** smaller models lose context. Larger models
> sometimes skip steps when "obvious". This playbook is the lowest-common-
> denominator script — written so a 1B-parameter model can follow it
> mechanically and a frontier model has nothing to argue with.
>
> **Read order if you are an agent on this repo:**
> 1. `WIKI_AGENT.md` (the philosophy)
> 2. This file (the explicit script)
> 3. The platform task file for the user's OS
> 4. `CLAUDE.md` or `AGENTS.md` (the schema)

---

## Section 1 — Core Rules (Memorise These; They Are Non-Negotiable)

These are stated as imperatives. Apply them on every action:

1. **Do not write outside `~/wiki/`.** Resolve every path first; reject if it
   resolves outside `WIKI_ROOT`.
2. **Do not write to `/etc/`, `/usr/`, `/var/`, `C:\Windows\`, `/System/`,
   `/Library/`, or any other system path.** Read-only. Always.
3. **Do not run `sudo` without proposing the command first and getting a `y`
   from the user.** No exceptions.
4. **Do not delete files.** Move them to `~/wiki/_archive/` instead. Let the
   user delete manually if they wish.
5. **Do not call `git push --force` or `git reset --hard` without confirming.**
6. **Stop and ask** if you don't have a clear instruction in this playbook for
   the situation you encounter. Do not improvise.

If you are a small model (≤ 7B parameters) and you are unsure whether an
action is allowed, the answer is: **no, ask the user.**

---

## Section 2 — How to Read a User Request

For every user message, do these in order:

### Step 2.1 — Classify the request

Pick exactly one bucket:

| Bucket | Example user message | Where to go |
|---|---|---|
| **Setup** | "Install wiki-linux on my Arch box" | Section 3 |
| **Ingest** | "I added a paper to raw/, please process" | Section 4 |
| **Query** | "What did I write about networking?" | Section 5 |
| **Lint** | "Check the wiki for problems" | Section 6 |
| **Edit** | "Update the page about X with Y" | Section 7 |
| **Other** | Anything else | Ask the user to rephrase as one of the above |

If you cannot classify, say so and ask. **Do not guess.**

### Step 2.2 — State your understanding

Before doing anything, write **one sentence** back to the user describing
what you understood. Pattern:

> "I understand you want me to **[verb] [object]**. I'll do that by
> **[high-level approach]**. Confirm or correct."

Wait for `y` / "go" / "yes" before continuing. The only exception is when the
user has already said "go" or "proceed" in this same conversation turn.

### Step 2.3 — Plan, then execute

For multi-step tasks, write the plan as a numbered list. Execute one step,
report what happened, then move to the next. Don't bundle.

---

## Section 3 — Setup (Initial Install)

### Step 3.1 — Detect the platform

Run **one** detection command:

| Platform guess | Command | Expected output |
|---|---|---|
| Linux | `uname -a` | `Linux ...` |
| macOS | `uname -a` | `Darwin ...` |
| Windows | `ver` (cmd) or `$PSVersionTable` (PS) | Windows / PowerShell info |

Then read the matching file:

- Linux  → `LINUX_AGENT_TASKS.md`
- macOS  → `MACOS_AGENT_TASKS.md`
- Windows → `WINDOWS_AGENT_TASKS.md`
- Codespaces → `CODESPACES_AGENT.md`

Do not start typing commands until you have read the file end-to-end.

### Step 3.2 — Run the pre-flight checks from that file

Each platform file has a "Pre-Flight Checks" section. Run every check.
Report each result. **Stop on first failure** and tell the user what's
missing.

### Step 3.3 — Phases

The platform file lists phases (Vault Init, Tool Install, etc.). For each
phase:

1. State the phase name to the user
2. Run only the commands in that phase
3. Report success or failure
4. **Wait** for the user to say "next" or "go"
5. Move to the next phase

Never skip a phase. Never combine phases. Even if you are a frontier model
that "knows" what's next, ask first.

---

## Section 4 — Ingest

### Step 4.1 — Find the source

The user said "I added a source" or named a file. Confirm:

```bash
ls -la <path-the-user-mentioned>
```

If the file isn't there or is unreadable, stop and ask.

### Step 4.2 — Read the source

For each ingest:
- Read at most **8 KB** of the source file (configurable in `config.json`).
- If larger, read first 8 KB and note "truncated" in the resulting page.

### Step 4.3 — Decide where the wiki page goes

Output a JSON object **before** writing anything:

```json
{
  "action": "ingest",
  "source_path": "<absolute path>",
  "target_path": "<relative to WIKI_ROOT, ending in .md>",
  "title": "<human-readable>",
  "tags": ["..."],
  "links_to_existing": ["wiki/path/to/existing-page"]
}
```

Validate the `target_path`:
- Must be relative
- Must end in `.md`
- Must resolve inside `WIKI_ROOT` (otherwise reject — see Section 1)

### Step 4.4 — Get user approval (only if `--interactive`)

If the user invoked you with interactive mode, print the JSON and ask
"Proceed?". Otherwise (auto mode), proceed but include the JSON in `log.md`.

### Step 4.5 — Write the wiki page

Use this exact frontmatter schema:

```yaml
---
title: <title>
source: <absolute path or URL of original>
ingested: <ISO 8601 UTC timestamp>
tags: [tag1, tag2]
related: [[other-page]]
confidence: high | medium | low
---
```

Then the body:

```markdown
# <title>

## Summary
<one paragraph in your own words>

## Key Points
- ...
- ...

## Verbatim Excerpt (if useful)
> "..."

## Source
<source path or URL>

## See Also
- [[wiki/related-page-1]]
- [[wiki/related-page-2]]
```

### Step 4.6 — Update cross-references

For each `[[wikilink]]` you added, open the target page and add a back-link
under its `## See Also` section if not already there.

### Step 4.7 — Append to log

Append one line to `_meta/log.md`:

```
2026-05-01T12:34Z ingest <source-path> -> <target-path>
```

---

## Section 5 — Query

### Step 5.1 — Search the wiki

Use `ripgrep` (already installed):

```bash
rg --type md --ignore-case "<keywords>" ~/wiki/
```

Take the top 5–10 matches. **Do not** retrieve from `raw/` — the wiki is the
synthesised layer; that's the point.

### Step 5.2 — Build the answer

Compose your reply using ONLY content from the matched wiki pages. After each
factual claim, cite the page in brackets:

> "The OSI model has 7 layers [[system/teaching/osi-model]]."

If the answer isn't in the wiki, say so:

> "I don't see this in your wiki. The closest pages are [[a]] and [[b]].
> Want me to ingest a new source?"

### Step 5.3 — Offer to file the answer

If the user found the answer useful, offer:

> "Want me to file this synthesis as `wiki/answers/<slug>.md` so you don't
> have to ask again?"

If they say yes, write the page following the Section 4 schema.

---

## Section 6 — Lint

Run these checks in order. Report findings; don't fix without asking.

| Check | How |
|---|---|
| Broken `[[wikilinks]]` | for each `[[X]]`, verify a file exists at that path |
| Orphan pages | files with no incoming links from other pages |
| Pages without `source:` | grep frontmatter for missing `source:` field |
| Pages over 6 months stale | check `ingested:` field, flag if old |
| Duplicate titles | same `title:` across multiple pages |
| Dangling references in `_meta/log.md` | log mentions pages that don't exist |

Output as a markdown report. Save to `_meta/lint-report-<date>.md`.

---

## Section 7 — Edit

User asks "Update page X with Y". Process:

1. **Read** page X completely first
2. **Restate** what's there in one sentence: *"This page currently says A,
   B, C."*
3. **Confirm** what to change: *"You want me to add Y, which would make it
   say A, B, C, Y. Correct?"*
4. **Edit** only after `y`
5. **Update** the `updated:` field in frontmatter to current time
6. **Append** to log

Never silently rewrite a page. If the user's request would replace existing
content, show a diff first.

---

## Section 8 — Output Format Rules

### When you are about to make a change

Always emit a JSON proposal first:

```json
{
  "action": "ingest|edit|create|delete|move",
  "target": "<path>",
  "reason": "<why>",
  "reversible": true,
  "reverse_command": "<exactly how to undo>"
}
```

`reversible: false` requires extra confirmation from the user.

### When you finish a step

Output exactly:

```
✓ <step name> done. <one-line summary>.
```

Or on failure:

```
✗ <step name> failed: <error>. <suggested next step>.
```

No prose padding. No emojis. No "I will now..." preambles.

### When you are confused

Say so:

```
✗ I don't have an instruction for this. Can you clarify whether this is
  ingest / query / lint / edit / setup / other?
```

Don't guess.

---

## Section 9 — Special Instructions for Small Models

If you are TinyLlama, Phi-2, Llama 3.2 1B / 3B, or any model under 7B
parameters:

1. **Don't try multi-step plans.** Do one thing at a time, report, wait.
2. **Use templates verbatim** from this file. Don't paraphrase the
   frontmatter or the JSON proposal — copy the exact format.
3. **For ingest:** classify the source into ONE of these categories only:
   `system | code | notes | research | reference`.
   Don't invent new ones.
4. **For query:** if `ripgrep` returns more than 10 matches, say "too many
   matches, please narrow your question." Don't try to synthesise across all
   of them.
5. **If unsure, refuse.** A small-model refusal ("I'm not confident enough
   to do this safely, please confirm or rephrase") is always better than a
   small-model improvisation.

---

## Section 10 — Special Instructions for Frontier Models

If you are Claude Opus / Sonnet, GPT-4/5, Gemini Pro, or similar:

1. The temptation to "be helpful" and skip steps is the failure mode here.
   The user wants **mechanical adherence**, not creative shortcuts.
2. Don't optimise away the pause-and-confirm loop in Section 2.2 just
   because you can predict the user will say yes. The pause is the safety
   feature.
3. Don't add code optimisations to the daemon source unless the user
   asked. The simplicity is intentional.
4. Verify against `references/karpathy-llm-wiki.md` before changing the
   pattern. The pattern came from elsewhere — don't redesign it.
5. Verify against the official docs of every dependency before changing
   how the code calls it. Specifically:
   - **ollama** Python client → https://github.com/ollama/ollama-python
   - **inotify_simple** → https://inotify-simple.readthedocs.io/
   - **systemd** unit syntax → https://www.freedesktop.org/software/systemd/man/systemd.unit.html
   - **ArchWiki** for any Arch-specific behaviour → https://wiki.archlinux.org/
6. The 16 unit tests in `tests/` are the contract. If a change breaks a
   test, the change is wrong (not the test). If you genuinely think the
   test is wrong, propose changing it as a separate step with reasoning.

---

## Section 11 — Codespaces Differences

When running inside a GitHub Codespace:

- **No `systemd`.** Don't try `systemctl --user enable ...`. Run the daemon
  directly: `python3 -m src.monitor &`
- **No real `/etc` to mirror.** The container's `/etc` is artificial. Don't
  enable `etc_allowlist` watching here.
- **No Ollama by default.** You can install it (`curl -fsSL
  https://ollama.com/install.sh | sh`) but it eats RAM. For a quick
  Codespace, mock the LLM layer or use a remote Ollama via `OLLAMA_HOST`.
- **`git push` works** (Codespaces have GitHub credentials). Encourage
  frequent commits — every wiki change should be a commit.

For Codespaces-specific tasks see `CODESPACES_AGENT.md`.

---

## Section 12 — Verification Loops (the missing piece)

Before declaring success on any task, run the corresponding verification:

| Task | Verification |
|---|---|
| Created a wiki page | `ls -la <target>` confirms file exists, `head <target>` confirms frontmatter is valid YAML |
| Updated a page | `git diff <target>` shows the expected change and nothing else |
| Installed a package | `command -v <pkg>` returns a path |
| Started a daemon | `pgrep -f monitor.py` returns a PID |
| Ran tests | `pytest tests/ -q` reports `N passed, 0 failed` |

**If the verification fails, the task failed**, even if the steps before it
appeared to succeed. Report the failure honestly.

---

## Section 13 — When the User Disagrees

If the user pushes back ("no, that's wrong") on something you've done:

1. **Don't apologise reflexively.** Read what they said carefully.
2. **Ask one specific question:** *"Which part is wrong — the file
   location, the content, or the timing?"*
3. **Make exactly one fix at a time.** Don't bundle "fixes" — that hides
   what worked from what didn't.
4. **Verify after the fix** (Section 12) and report.

---

## Section 14 — When You Disagree with the User

If the user asks for something that violates Section 1 (the core rules):

> "I can't do that because [rule X]. Here's an alternative that gets you
> [the underlying goal]: [alternative]. Want to do that instead?"

Don't moralise. Don't lecture. State the rule, offer the alternative,
ask the question. Move on either way.

---

## Section 15 — One-Page Summary

If you remember nothing else:

```
1.  Read WIKI_AGENT.md before acting.
2.  Classify the request: setup / ingest / query / lint / edit.
3.  Restate understanding, get a "go".
4.  Plan in numbered steps. Execute one. Report. Wait.
5.  Validate every path resolves inside WIKI_ROOT.
6.  Use the JSON proposal format for any change.
7.  Use the frontmatter template exactly. No improvisation.
8.  Verify after every step (Section 12).
9.  Ask if unsure. Refuse if asked to break a rule.
10. Append to log.md when you're done.
```
