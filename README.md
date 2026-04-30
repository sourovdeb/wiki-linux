# Wiki-OS: An Arch Linux Wiki-Native Knowledge Layer

## What This Is

Wiki-OS is a personal knowledge system that treats your Arch Linux machine as a
living wiki. Every system config, every note, every project gets documented in
plain Markdown, cross-linked like a wiki, automatically maintained by a local
LLM, and version-controlled with Git.

It does **not** rearrange your filesystem. `/etc` stays exactly where it is.
The kernel, systemd, pacman, and every other tool continues reading files in the
same paths they always have. Wiki-OS adds a parallel knowledge layer on top —
a directory of Markdown pages that *mirror and document* your system — rather
than trying to replace the system itself with Markdown.

---

## Why Each Decision Was Made

### Why Markdown and a plain directory — not a database

Markdown files in a directory tree are the most durable format a personal
knowledge system can use. They open in any editor from 1990 to today. They work
with every Unix tool — `grep`, `find`, `cat`, `diff`, `rsync`, `git`. They
survive the death of any application. If Obsidian stops working tomorrow, your
data is still perfectly readable. This durability is the entire reason the system
is worth building in the first place.

A database (SQLite, Postgres, a proprietary app format) adds query capability at
the cost of opacity and fragility. We get query capability from ripgrep and an
LLM without paying that cost.

### Why `~/wiki` is separate from `/etc` and `/home`

The original proposal was to symlink `/etc` and `/home` into the wiki. This
cannot work because the files under `/etc` are not Markdown — they are INI
files, key-value configs, unit files, and binary databases — and the tools that
read them (pacman, systemd, sshd, the kernel itself) do not understand Markdown.
Symlinking them away from their expected locations breaks every tool that looks
for them, which is most of userspace, and the machine fails to boot.

The solution is a **one-way mirror**: the wiki contains a `system/config/` tree
of Markdown pages, one per documented config. Each page holds a human-written
explanation, a code block with the verbatim live contents, a timestamp, and
cross-links to related pages. The real `/etc/pacman.conf` is never touched.
Data flows one direction only — source system file → derived wiki page — which
means a hallucinating LLM or a bug in the daemon cannot damage system
configuration. This asymmetry is the most important safety property of the whole
design.

### Why inotify instead of fanotify

fanotify is a privileged kernel API designed for antivirus scanners and mandatory
access control systems. Using it to watch a personal wiki directory requires
running your daemon as root, which is an unnecessary attack surface.

inotify is the kernel's standard filesystem notification mechanism, available to
any process watching paths it can already read. The wiki daemon runs as your
normal user through `systemctl --user`, with no more privileges than you have at
the shell. If the daemon crashes, misbehaves, or is compromised, the blast radius
is limited to your user files, not the system.

### Why the Ollama Python library instead of a subprocess call

`subprocess.run(["ollama", "run", model, prompt])` looks simple but has serious
problems in a daemon. It spawns a fresh OS process per file event, pays the
model cold-start loading time on every event (potentially several seconds), has
no mechanism to receive structured output, and discards errors silently.

The Ollama REST API, wrapped by the `ollama` Python library, talks over a
persistent socket to the already-running `ollama.service`. The model stays loaded
in memory between calls. `format="json"` instructs the model to return parseable
structured data rather than prose. The `timeout` and `stream=False` options make
the call deterministic from the caller's perspective. This is the difference
between a daemon that handles dozens of events per minute and one that crawls.

### Why `format="json"` and a tight system prompt

A small model like Mistral 7B or Llama 3.2 3B is perfectly capable of
generating a good wiki page, but only if you constrain what it is allowed to
produce. A loose prompt like "update the wiki based on this file" gives you
prose that cannot be automatically parsed and acted on.

`format="json"` with a system prompt that specifies an exact JSON schema forces
the model to produce machine-readable output — a `target_path`, `title`,
`content` string, and `links` list — that the daemon can validate, write, and
cross-link without further interpretation. The model does the knowledge work;
the daemon does the mechanical file work.

### Why Git for portability instead of rsync alone

`rsync` copies files but has no history and no conflict resolution. If you edit
on two machines and sync in both directions, you lose one version. Git gives you
the full history of every wiki change, a conflict model you already understand,
and the ability to push to any remote (Gitea, GitHub, Forgejo, an SSH server on
your external SSD) for backup and sync. `rsync` is kept as a fast flat-copy tool
for external drives where Git may not be installed.

### Why a `wiki` shell command rather than a dedicated TUI

Writing a TUI from scratch is a multi-month project and creates a dependency that
can rot. The tools that already exist — Obsidian for GUI, `mdt` for terminal
navigation, Neovim for editing, `ripgrep` for search — each do their specific
job better than a custom TUI could. The `wiki` shell command is a thin dispatcher
that ties them together: `wiki search`, `wiki open`, `wiki new`, `wiki ask`.
Adding a new subcommand is a `case` branch in a shell script.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Your Arch Linux System                       │
│                                                                  │
│  /etc/pacman.conf          ←  read-only by daemon               │
│  /etc/fstab                ←  (never written, never moved)       │
│  /etc/ssh/sshd_config      ←                                     │
│                                                                  │
│                    ↓  inotify events (read-only)                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  wiki-monitor.service  (systemctl --user)                 │   │
│  │  ┌──────────────┐   ┌──────────────┐   ┌─────────────┐  │   │
│  │  │  monitor.py  │ → │   llm.py     │ → │  indexer.py │  │   │
│  │  │  (inotify)   │   │  (Ollama API)│   │  (ripgrep)  │  │   │
│  │  └──────────────┘   └──────────────┘   └─────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                 ↓ writes                         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  ~/wiki/                                                     │ │
│  │  ├── system/config/pacman.conf.md   (mirrored + documented) │ │
│  │  ├── system/config/fstab.md                                  │ │
│  │  ├── user/notes/                   (your own notes)          │ │
│  │  ├── user/projects/                                          │ │
│  │  ├── _meta/index.md                (auto-generated index)    │ │
│  │  └── _meta/recent.md                                         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                    ↓  Git auto-commit (every 5 min)              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  External SSD / Remote Git server / Gitea                  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  Interface Layer                                          │    │
│  │  Obsidian (GUI vault) │ mdt (TUI nav) │ Neovim (editor)  │    │
│  │  wiki new │ wiki search │ wiki ask │ wiki sync            │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

**`src/config.py`** loads `~/.config/wiki-os/config.json` and expands all
`~` paths. Every other module imports from this; no path is hardcoded elsewhere.

**`src/monitor.py`** is the core daemon. It adds inotify watches on `~/wiki`,
`~/notes`, and each path in the `/etc` allowlist. On `CLOSE_WRITE` or `CREATE`
events it filters for allowed extensions, checks a self-write deque to suppress
its own edits (preventing the feedback loop where writing a wiki page triggers
re-processing of that same page), and calls `llm.py`.

**`src/llm.py`** wraps the Ollama Python client. It reads the source file,
truncates it to the configured byte limit, and asks the model for a JSON
response describing the target wiki page to write. It validates the JSON
structure before writing anything. If the model returns garbage, it logs and
returns `False` — no file is written.

**`src/indexer.py`** rebuilds `_meta/index.md` and `_meta/recent.md` by
walking the wiki tree and reading each page's YAML frontmatter. It runs after
every LLM write and on daemon startup.

**`src/search.py`** runs `rg --json <query> ~/wiki`, takes the top 10 matching
snippets, and sends them to Ollama with a retrieval-augmented prompt. The model
sees only those snippets, so it cannot hallucinate content that is not in your
wiki.

**`src/sync.py`** is called by `wiki-sync.timer` every five minutes. It runs
`git add -A && git commit -m "auto: <timestamp>"` inside `~/wiki`, then
`git push` if a remote is configured.

**`bin/wiki`** is a bash dispatcher. Every subcommand resolves to a Python call
or a system tool.

**`systemd/`** contains the user-level service and timer units that keep the
daemon and sync running without root.

---

## Installation Quick Reference

```bash
# 1. Clone or copy this project
git clone <this-repo> ~/wiki-os
cd ~/wiki-os

# 2. Run the installer (never needs sudo except for AUR packages)
bash install.sh

# 3. Pull your chosen Ollama model
ollama pull mistral   # or: llama3.2, phi3, tinyllama

# 4. Enable the services
systemctl --user enable --now wiki-monitor
systemctl --user enable --now wiki-sync.timer

# 5. Start using the wiki
wiki new "My first page"
wiki open
wiki ask "What does my pacman.conf do?"
```

---

## Extending the System

To add a new watched path, add it to `monitor.watch_paths` in your
`config.json`. To add a new `/etc` file to mirror, add its absolute path to
`monitor.etc_allowlist`. To change the LLM model, change `ollama.model` in the
config and make sure the model is pulled (`ollama pull <name>`). To add a `wiki`
subcommand, add a `case` branch to `bin/wiki` that calls `python3
~/wiki-os/src/<whatever>.py`.

The system is intentionally small. Every component is a plain file you can read
in five minutes.

---

## Caveats and Limits

The LLM-generated mirror pages for `/etc` files are documentation, not
configuration. Never edit them expecting the edit to propagate back to the system
— it will not, by design. Edit the real file in `/etc` with `sudoedit` or
`sudo nvim`, and the daemon will regenerate the mirror page automatically.

TinyLlama (1.1B) is fast but produces mediocre summaries. Mistral 7B Instruct is
the sweet spot on machines with ≥ 8 GB RAM. Llama 3.2 3B is a reasonable middle
ground at ≈ 2 GB RAM overhead.

The self-write deque suppresses feedback for `DEBOUNCE_SECONDS` (default 5).
If you have a use case where you need to manually trigger reprocessing of a wiki
page you just wrote, run `wiki reprocess <path>`.
