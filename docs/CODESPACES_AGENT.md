# CODESPACES_AGENT.md

> Read **WIKI_AGENT.md** first.
>
> This file tells a **cloud-based agent** (GitHub Codespaces, Gitpod,
> a remote OpenAI Codex sandbox, a Claude Code task running in a
> container) how to bootstrap or extend a wiki vault that lives in a
> Git repository, without touching a local OS.
>
> The cloud case is **simpler** than the local one. There is no
> `/etc` to mirror, no Explorer to customise, no notification system
> to install. The agent's job is purely Karpathy's loop: ingest,
> query, lint, against a Markdown vault checked into Git.

---

## EXPECTED ENVIRONMENT

- A Git repository checked out at `/workspaces/<repo>` (Codespaces) or
  `/workspace/<repo>` (Gitpod) or `/home/user/repo` (generic devcontainer).
- The repository contains, or is becoming, a wiki vault. Layout:

```
<repo>/
  AGENTS.md        ← the schema (this directory's authoritative spec)
  CLAUDE.md        ← copy of AGENTS.md, for Claude Code
  README.md
  system/          (optional — if mirroring repo/CI configs)
  user/
  raw/             ← drop sources here
  _meta/
    index.md
    log.md
    recent.md
```

- A model accessible via either:
  - The agent's built-in tool calls (Claude Code, Codex CLI), OR
  - An Ollama instance on `localhost:11434` (devcontainer extra), OR
  - An OpenAI / Anthropic API key in the environment.

---

## TASK 1 — Detect or initialise

```bash
cd "${REPO_ROOT:-$(git rev-parse --show-toplevel)}"

# Initialise vault structure if missing.
for d in user/notes user/projects user/research raw _meta; do
  mkdir -p "$d"
done

# Initialise schema files if missing.
[ -f AGENTS.md ] || cp /path/to/WIKI_AGENT.md AGENTS.md
[ -f CLAUDE.md ] || cp AGENTS.md CLAUDE.md

# Initialise meta files if missing.
[ -f _meta/index.md  ] || printf '# Wiki Index\n\n' > _meta/index.md
[ -f _meta/log.md    ] || printf '# Wiki Log\n\n'   > _meta/log.md
[ -f _meta/recent.md ] || printf '# Recent\n\n'     > _meta/recent.md

# Devcontainer convenience tooling.
which rg   >/dev/null 2>&1 || sudo apt-get install -y ripgrep
which glow >/dev/null 2>&1 || sudo snap install glow || true
```

## TASK 2 — Devcontainer config (recommended)

If the repo does not have one, create `.devcontainer/devcontainer.json`:

```json
{
  "name": "Wiki Vault",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/python:1": {"version": "3.12"}
  },
  "postCreateCommand": "bash .devcontainer/setup.sh",
  "customizations": {
    "vscode": {
      "extensions": [
        "yzhang.markdown-all-in-one",
        "kortina.vscode-markdown-notes",
        "foam.foam-vscode",
        "shd101wyy.markdown-preview-enhanced"
      ],
      "settings": {
        "files.associations": { "*.md": "markdown" },
        "markdown.preview.breaks": true
      }
    }
  }
}
```

`.devcontainer/setup.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -qq
sudo apt-get install -y ripgrep
pip install --quiet pyyaml jinja2 ollama
echo "Wiki devcontainer ready. Type 'cat AGENTS.md' to see the schema."
```

Commit both files. Anyone (or any agent) opening the codespace lands in
a ready-to-use vault.

## TASK 3 — Agent loop in a codespace

The agent's job inside Codespaces is exactly the Karpathy loop. The
schema in `AGENTS.md` already specifies the JSON contract. Concrete
flow:

```
USER drops a PDF / URL / pasted markdown into raw/
    ↓
USER says: "Ingest the latest source."
    ↓
AGENT:
  1. Read raw/<latest-file>
  2. Generate JSON: { target_path, title, content, links, tags }
  3. Validate target_path is inside the repo (relative, ends in .md,
     resolves under user/ or system/)
  4. Write the file
  5. Append to _meta/log.md:
     ## [YYYY-MM-DD] ingest | <title>
     - source: raw/<file>
     - target: <target_path>
  6. Update _meta/index.md by re-walking the tree
  7. git add -A && git commit -m "ingest: <title>"
  8. Return a one-paragraph summary to the user
```

For queries:

```
USER: "What did the Smith 2024 paper say about scaling?"
    ↓
AGENT:
  1. rg --json -i "smith.*2024|scaling laws|smith et al" .
  2. Take the top 10 matches, read those files in full
  3. Synthesize an answer with [[wikilink]] citations
  4. If the answer has lasting value, write it to user/research/Q-<slug>.md
     and update the index.
  5. git commit
```

For lint passes:

```
USER: "Lint the wiki."
    ↓
AGENT (one query at a time, never all at once):
  - Find pages whose frontmatter date is > 6 months old → list as stale
  - Find pages with no inbound [[wikilinks]] → list as orphans
  - Find concepts mentioned 3+ times but with no page → propose pages
  - Find pairs of pages that contradict → flag for review
  Write the result to _meta/lint-<date>.md and commit.
```

## TASK 4 — Working with the user's existing repo

If the user pointed the agent at an existing wiki repo (e.g. their
`github.com/sourovdeb/wiki-linux`) instead of a fresh one:

```bash
# 1. Read the existing schema.
cat AGENTS.md 2>/dev/null || cat CLAUDE.md 2>/dev/null || echo "(no schema yet)"

# 2. Read the existing structure.
find . -maxdepth 3 -type d -not -path '*/\.*'

# 3. Read recent log entries.
tail -n 50 _meta/log.md 2>/dev/null

# 4. ASK the user what they want to do before changing anything.
```

The agent **does not impose** the WIKI_AGENT.md layout on a repo that
already has its own conventions. It reads what exists, asks the user
what is missing, and adds only what they confirm.

## TASK 5 — When the agent has no shell access

Some agents (notably long-context chat models without code execution)
can only suggest changes. In that mode:

- Still produce the JSON output contract from WIKI_AGENT.md.
- Print the diff in fenced blocks the user can copy.
- Print the exact `git` commands the user should run.
- Never claim a write happened unless a tool confirmed it.

This is the "agent in suggest-only mode" fallback. It is the same
contract, just executed by the user instead of the agent.

---

## DIFFERENCES FROM THE LOCAL SETUP

| Concern | Local | Codespaces |
|---|---|---|
| `/etc` mirroring | Yes (allowlisted) | No — there is no meaningful `/etc` |
| Notification helper | Yes (`wiki-notify`) | No — write to `_meta/notifications.log` only |
| Daemon / inotify | Optional | No — manual ingest is the norm |
| Display name renames | Yes (visual) | No |
| Tool minimisation | Yes | No — the container is already minimal |
| Git auto-commit | Optional | Yes — every write commits |
| Obsidian | Yes | No (use VS Code Markdown Notes / Foam instead) |

The cloud version is purely the **knowledge layer**. The local version
adds the OS layer on top.

---

## ENDING A SESSION

Before the codespace is suspended or destroyed, the agent ensures:

```bash
git status
# → "nothing to commit, working tree clean"

git push origin main
# → All work persisted to the remote.
```

If `git push` fails (no remote, no permissions), the agent tells the
user via stdout, not silently. A wiki that does not push is a wiki
that loses work when the codespace dies.
