# wiki-linux

> A wiki-native knowledge layer for Linux (and Windows). Built on Andrej
> Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

**The short version:** `~/wiki/` is a Git-tracked directory of Markdown
files. A daemon watches your system configs with inotify and uses a
local LLM (Ollama) to generate and maintain wiki pages for them. Your
`/etc` is never touched. Your OS works exactly as before. You get a
searchable, cross-linked, LLM-queryable knowledge base built on top.

---

## Quick Start (Arch Linux)

```bash
git clone https://github.com/sourovdeb/wiki-linux ~/wiki-linux
cd ~/wiki-linux
bash install.sh

# Pull your chosen model
ollama pull mistral        # or: llama3.2 / phi3 / tinyllama

# Enable services
systemctl --user enable --now wiki-monitor
systemctl --user enable --now wiki-sync.timer

# Use it
wiki new "My first note"
wiki ask "What does my pacman.conf do?"
wiki status
```

---

## Repository Layout

```
wiki-linux/
├── WIKI_AGENT.md            ← LLM idea file: paste into any AI agent
├── AGENTS.md                ← agent schema (Codex, Claude Code, etc.)
├── CLAUDE.md                ← Claude Code specific schema
├── LINUX_AGENT_TASKS.md     ← setup steps for Linux agents
├── WINDOWS_AGENT_TASKS.md   ← setup steps for Windows agents
├── SUPPORT_POPUP.md         ← wiki-notify popup helper
├── CODESPACES_AGENT.md      ← GitHub Codespaces agent tasks
├── config.json              ← configuration (copy to ~/.config/wiki-os/)
├── install.sh               ← idempotent installer
├── requirements.txt         ← Python deps
├── bin/wiki                 ← CLI dispatcher
├── src/                     ← Python daemon modules
│   ├── config.py, monitor.py, llm.py
│   ├── indexer.py, search.py, sync.py
├── systemd/                 ← user-level service and timer units
└── templates/               ← Jinja2 page templates
```

---

## Architecture

```
/etc/pacman.conf  (never modified)
      ↓ inotify (read-only)
monitor.py → llm.py (Ollama API, format=json)
      ↓ writes
~/wiki/system/config/pacman.conf.md
      ↓ every 5 min
git auto-commit → optional remote push
      ↓ interface
Obsidian (GUI) │ mdt (TUI) │ wiki CLI │ ripgrep+RAG
```

Data flows **one direction only**: source file → wiki page. Never the
reverse. A hallucinating LLM cannot damage your system configuration.

---

## Using with AI Agents

**Paste `WIKI_AGENT.md` into any LLM agent.** It's the master
instruction file — self-contained, model-agnostic, works with TinyLlama
through Opus. The agent will read it and instantiate the wiki system in
collaboration with you.

- Claude Code: `cat CLAUDE.md` in your project directory
- OpenAI Codex: paste `WIKI_AGENT.md` as system prompt
- GitHub Codespaces: see `CODESPACES_AGENT.md`
- Windows: see `WINDOWS_AGENT_TASKS.md`

---

## What It Looks Like Day-to-Day

You edit `/etc/pacman.conf`. Two seconds later, without any action from
you, `~/wiki/system/config/pacman.conf.md` is updated with a
human-readable explanation of the file, the verbatim contents in a code
block, a timestamp, and cross-links to related wiki pages. Obsidian
shows the new page. The change is committed to git.

You want to remember why you changed something six months ago. You run
`wiki ask "Why did I add the multilib repo?"`. The RAG pipeline searches
your wiki, finds the relevant note, and the LLM synthesises an answer
from your own writing.

---

## Configuration

Copy `config.json` to `~/.config/wiki-os/config.json` and edit:

```jsonc
{
  "ollama": { "model": "mistral" },      // tinyllama / llama3.2 / phi3
  "monitor": {
    "etc_allowlist": ["/etc/pacman.conf", "/etc/fstab", "..."]
  },
  "git": { "remote": "origin" }          // push target, empty = no push
}
```

---

## Invariants the Code Enforces

- Never writes outside `~/wiki` (path escape check on every LLM output)
- Never writes to `/etc` or any system path
- Suppresses its own writes (prevents inotify feedback loops)
- Runs as normal user, no root, no fanotify
- LLM output always validated as JSON before any file write

---

## License

MIT
