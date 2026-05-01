#!/usr/bin/env bash
# Rewrite FINAL-SETUP-SUMMARY.md to reflect the post-Toleria, Obsidian-centric setup.
set -euo pipefail
cat > ~/Desktop/WIKI-TOOLS/FINAL-SETUP-SUMMARY.md <<'EOF'
# Wiki-Linux + Obsidian + Ollama — Final Setup

**Status:** Operational. Obsidian is the wiki UI; Ollama answers questions; whisper transcribes audio.

## What runs at login

1. **Obsidian** — fullscreen, opens `~/wiki/` automatically. BMO Chatbot plugin is wired to localhost Ollama (mistral default).
2. **Welcome popup** — assistance dialog: open Obsidian, ask Ollama, new note, record+transcribe, OBS, status, sync.
3. **Wiki-monitor daemon** — ingests anything dropped in `~/Downloads`, `~/Documents`, `~/wiki`.
4. **Ollama** — 4 models ready: mistral, llama3.2:3b, qwen2.5-coder:3b, nomic-embed-text.

## Desktop = Wiki

The XFCE desktop folder is `~/wiki/`. Files you save to "Desktop" land in your vault. Right-click any `.md` → **Open in Obsidian**.

## Tools available

| Tool | Path | Purpose |
|---|---|---|
| `obsidian` | /usr/bin/obsidian | Vault UI |
| `wiki-welcome` | ~/.local/bin/wiki-welcome | Assistance popup |
| `wiki-transcribe` | ~/.local/bin/wiki-transcribe | Record → whisper → wiki page |
| `ask-ollama` | ~/.local/bin/ask-ollama | Pipe text to mistral |
| `obs` | /usr/bin/obs | Screen recording |
| `whisper` | ~/.local/bin/whisper | Audio transcription |

## Browsers

- **Firefox** — built-in AI sidebar enabled, pointed at local Ollama.
- **Chromium** — side panel enabled; launch via "Chromium (Wiki AI)".
- **Brave** (optional) — Leo AI configurable to use Ollama.

## Daily flow

- Drop files → daemon ingests → committed to git every 5 min.
- Press the welcome popup at login (or run `wiki-welcome`) for any task.
- Edit notes in Obsidian — graph view, backlinks, [[wikilinks]] all work.

## Safety

All EXPECTATIONS guarantees still hold: config locked, /etc untouched, deletions go to `_archive/`, daemon runs as user, everything in git.
EOF
echo "✓ FINAL-SETUP-SUMMARY.md rewritten"
