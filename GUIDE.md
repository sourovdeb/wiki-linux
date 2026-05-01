# Wiki-Linux User Guide

> Your personal wiki is running. This file is your starting point.
> The daemon is watching your files. Obsidian (or `mdt`) is your reader.
> `wiki` in a terminal is your control panel.

---

## What Is This?

Your wiki is a **self-maintaining knowledge base** for your Arch Linux system.

Based on Andrej Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):

- Drop a file anywhere the daemon watches → it gets documented automatically
- Ask a question → the LLM searches your wiki and answers from it
- Your `/etc` config files are mirrored here as readable explanations
- Everything is in Git — nothing is ever permanently lost

---

## Folder Structure

```
~/wiki/
├── system/            ← Auto-generated mirrors of /etc config files
│   ├── config/        ← pacman.conf, fstab, sshd_config explained
│   ├── logs/          ← System log summaries
│   └── docs/          ← How your installed services work
├── user/              ← Your own notes (you own these)
│   ├── notes/         ← Quick notes (wiki new "title" creates here)
│   ├── projects/      ← Project pages
│   └── research/      ← Research & reading notes
├── _meta/             ← Auto-generated (do not edit manually)
│   ├── index.md       ← Table of contents
│   ├── recent.md      ← Latest changes
│   ├── log.md         ← Append-only operation log
│   └── tasks/         ← Task notes logged with wiki task
├── _archive/          ← Deleted files land here (not permanently gone)
└── _tmp/              ← Scratch space (not tracked by git)
```

---

## The 5 Things You'll Do Most

### 1. Create a new note
```bash
wiki new "My networking notes"
# Opens in $EDITOR. Save and close to finish.
```

### 2. Search your wiki
```bash
wiki search "GPU driver"
wiki search "pacman"
wiki search "systemd timer"
```

### 3. Ask a question
```bash
wiki ask "What does my fstab mount at boot?"
wiki ask "How do I roll back a package?"
wiki ask "What firewall rules are active?"
# The LLM reads your wiki and answers from it — not from the internet.
```

### 4. Add a source document
```bash
wiki ingest ~/Downloads/arch-hardening-guide.txt
# The LLM reads it and files the knowledge into the appropriate wiki pages.
```

### 5. Sync to GitHub
```bash
wiki sync
# Commits all changes and pushes to your configured git remote.
```

---

## Full Command Reference

| Command | What it does |
|---|---|
| `wiki new "title"` | Create a new page in `user/notes/` |
| `wiki ingest <file>` | Ingest a source file via LLM |
| `wiki open` | Open the wiki in Obsidian (GUI) or `mdt` (terminal) |
| `wiki open system/config/pacman.conf` | Open a specific page |
| `wiki search <query>` | Full-text ripgrep search |
| `wiki ask "<question>"` | LLM Q&A from your wiki |
| `wiki status` | Daemon PID, page count, git status |
| `wiki sync` | Commit and push to git remote |
| `wiki lint` | Check for broken `[[wikilinks]]` |
| `wiki task "title" "body"` | Log a task note to `_meta/tasks/` |
| `wiki reprocess <file>` | Force-regenerate a wiki page |
| `wiki serve` | Run monitor in foreground (debugging) |
| `wiki config` | Show the current configuration |

---

## The Daemon

A background service watches files with inotify and calls the local Ollama LLM
to generate and update wiki pages automatically.

```bash
# Check it's running:
wiki status

# Watch live logs:
journalctl --user -u wiki-monitor -f

# Restart if needed:
systemctl --user restart wiki-monitor

# Temporarily stop:
systemctl --user stop wiki-monitor
```

The daemon **never touches `/etc`** — it only reads it.
The daemon **never hard-deletes** — files moved to `_archive/` instead.

---

## Recovering Deleted Files

Nothing is permanently deleted. Files are moved to `_archive/` with a timestamp.

```bash
# List archived files:
ls ~/wiki/_archive/

# Recover a file:
mv ~/wiki/_archive/my-page.md.deleted.* ~/wiki/user/notes/my-page.md

# Git also has full history:
git -C ~/wiki log --oneline
git -C ~/wiki checkout HEAD~3 -- user/notes/my-page.md
```

---

## Configuration

The config file is at `~/.config/wiki-linux/config.json` and is **read-only** after install.

To edit it:
```bash
bash ~/Documents/wiki-linux/wiki-linux/install.sh --reconfigure
```

Key settings to review:
- `ollama.model` — change from `mistral` to any model you've pulled
- `git.remote` — set your GitHub URL for backup/sync
- `monitor.etc_allowlist` — which `/etc` files get mirrored

---

## Setting Up Git Backup

```bash
# 1. Create a private repo on GitHub called "my-wiki"

# 2. Unlock config temporarily:
bash ~/Documents/wiki-linux/wiki-linux/install.sh --reconfigure

# 3. Edit the remote:
#    Set "remote": "https://github.com/yourusername/my-wiki.git"

# 4. Add the remote and push:
git -C ~/wiki remote add origin https://github.com/yourusername/my-wiki.git
git -C ~/wiki push -u origin main

# 5. Future syncs happen automatically every 5 minutes via wiki-sync.timer,
#    or manually with: wiki sync
```

---

## Using Obsidian (Optional)

Obsidian gives you a graph view of all your wiki links.

```bash
# Open the whole wiki:
wiki open

# Or launch directly:
obsidian ~/wiki
```

- Use `[[double brackets]]` to create links between pages
- The graph view shows connections between everything you know
- The daemon and Obsidian don't conflict — daemon writes, you edit

---

## Notifications

Wiki-Linux sends desktop notifications for key events (ingest complete,
lint warnings, daemon errors) via `wiki-notify`.

Notifications are also logged to `_meta/notifications.log` regardless of
whether the desktop notification was shown.

---

## Tips

- **Don't edit `_meta/`** — it's auto-generated. Edits will be overwritten.
- **`_tmp/` is scratch space** — not tracked by git. Use it for drafts.
- **`sources:` frontmatter** — always link pages back to their source file.
  This is how the wiki stays auditable (Karpathy's key caveat).
- **Run `wiki lint` weekly** — it catches orphan pages and broken links before
  they accumulate.
- **The wiki is yours** — the daemon writes `system/`, but `user/` is entirely
  under your control. Write, edit, delete freely there.

---

*Generated by wiki-linux. See `_meta/index.md` for the auto-generated table of contents.*
