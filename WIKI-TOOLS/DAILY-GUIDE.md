---
title: How to Use Wiki-Linux Daily
updated: 2026-05-01
tags: [guide, daily, quick-reference]
---

# Your Daily Wiki-Linux Workflow

> **One sentence:** Drop files anywhere, ask questions in the search box, let Ollama do the rest.

---

## The 5-Minute Morning Routine

Every morning when you log in you'll see:

1. **Welcome popup** — shows page count, daemon status, last sync
2. **Everything is already running** — you don't need to start anything

That's it. The daemon is in the background.

---

## How to Use It Day-to-Day

### 1. Drop Files → Wiki Builds Itself

```
Save a file to →          It becomes →
~/Downloads/paper.pdf     wiki/user/research/paper.md
~/Documents/notes.txt     wiki/user/notes/notes.md
~/wiki/user/notes/        (already in your wiki)
```

**You don't do anything.** The daemon watches, calls Ollama, writes the wiki page.

---

### 2. Search Your Wiki (the Search Box)

Press the **keyboard shortcut** (set it up: XFCE Settings → Keyboard → Application Shortcuts → `wiki-search` → bind to `Super+Space`) or run:

```bash
wiki-search
```

You get a dialog. Choose:
- **Ask LLM** — type a question, Ollama answers from your wiki
- **Search** — find keywords across all pages
- **New Note** — create and open a note immediately
- **Status** — check everything is running

---

### 3. Terminal Commands (when you want more)

```bash
wiki ask "How do I reload systemd?"   # LLM answers from your wiki
wiki search "pacman"                   # Find all pages mentioning pacman
wiki new "My SSH setup"                # Create a note and open it
wiki lint                              # Check for broken links in your wiki
wiki sync                              # Commit + push wiki to GitHub now
wiki status                            # See daemon, Ollama, git status
wiki open                              # Open wiki in Obsidian or mdt
```

---

### 4. Adding Sources (papers, articles, docs)

Drop them into `~/Downloads/` or `~/wiki/user/research/`. The daemon handles the rest.

Or manually:
```bash
wiki ingest ~/Downloads/paper.pdf      # Force-ingest a specific file
```

---

### 5. HDD Backup (plug it in, that's all)

When you plug in an **external USB drive**, a popup appears automatically:

```
"Drive connected — backup wiki?"
[Backup Now]  [Skip]
```

Click "Backup Now" and your entire wiki is copied to the drive.

---

## What's Running in the Background

| Service | Does what |
|---|---|
| `wiki-monitor` | Watches your files with inotify, calls Ollama |
| `wiki-sync.timer` | Auto-commits every 5 min to git |
| `ollama` | Local AI (mistral, llama3.2, qwen2.5-coder) |

**Check everything is fine:**
```bash
wiki-panel   # Shows: ◆ mistral | 41p | ✓ wiki
```

---

## Your Ollama Models (Ready to Use)

| Model | Size | Best for |
|---|---|---|
| `mistral` | 7.2B | Default — general wiki pages |
| `llama3.2:3b` | 3.2B | Faster — quick questions |
| `qwen2.5-coder:3b` | 3.1B | Code-related files |
| `nomic-embed-text` | 137M | Semantic search (auto-used) |

**To switch model for all future wiki pages:**
```bash
# Edit config (safely):
install.sh --reconfigure
# Change: "model": "llama3.2:3b"
```

---

## The GUI Option: Obsidian

**Obsidian** is the best GUI viewer for your wiki.

```bash
# Install:
sudo pacman -S obsidian

# Open your wiki:
obsidian ~/wiki
```

What you'll see:
- Left panel: file tree of all your wiki pages
- Graph view: visual network of all your linked pages
- Search: full-text search across everything
- [[wikilinks]] work as clickable links

**Obsidian is read-only from the daemon's perspective** — you edit, the daemon also writes. They don't conflict (self-write suppression is built in).

---

## Quick Troubleshooting

| Problem | Fix |
|---|---|
| Search dialog doesn't open | `wiki-search` in terminal — check WIKI_OS_CONFIG |
| Daemon stopped | `systemctl --user restart wiki-monitor` |
| Files not being processed | Check `tail -f ~/.cache/wiki-linux/monitor.log` |
| Ollama not responding | `systemctl restart ollama` |
| Config locked | `bash ~/Documents/wiki-linux/wiki-linux/install.sh --reconfigure` |

---

## Safety Guarantees (Always True)

- ✅ `/etc` is never written — only read
- ✅ Deleted pages go to `~/wiki/_archive/` — never destroyed
- ✅ Everything in Git — nothing permanently lost
- ✅ `config.json` is read-only — daemon can't corrupt it
- ✅ Daemon runs as you, not root — can't touch system files

---

## One-Line Summary

> **Drop files anywhere, ask questions in the search box, Ollama does the rest — your wiki grows automatically.**
