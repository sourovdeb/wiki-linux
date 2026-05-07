# wiki_ingestor

> MarkItDown-powered file-to-Markdown daemon for the **wiki-linux** ecosystem.

Watches your file system for any supported document type, converts it to clean
Markdown using Microsoft's [MarkItDown](https://github.com/microsoft/markitdown)
library, and deposits the result into your `~/wiki/converted/` directory — where
your existing `indexer.py` and `llm.py` tools can immediately find and search it.

---

## How it fits into wiki-linux

```
     Your files                wiki_ingestor               wiki-linux
  ───────────────        ──────────────────────        ──────────────────
  ~/Documents/           watcher.py sees change        indexer.py
  ~/Downloads/    ──▶    converter.py converts   ──▶   ~/wiki/converted/
  /mnt/usb/              ledger deduplicates           llm.py searches
  (any path)             frontmatter added             monitor.py watches
```

No changes are required to your existing wiki-linux files. `wiki_ingestor` is a
drop-in addition that automatically detects and respects your existing wiki-linux
configuration.

---

## Supported file types

| Category       | Extensions                                      |
|----------------|-------------------------------------------------|
| Office         | `.docx` `.xlsx` `.xls` `.pptx` `.ppt`          |
| PDF            | `.pdf`                                          |
| Web / data     | `.html` `.htm` `.csv` `.json` `.xml`            |
| Text / code    | `.txt` `.md` `.rst`                             |
| Images*        | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp`     |
| Audio*         | `.mp3` `.wav` `.m4a` `.ogg`                     |
| Archives       | `.zip`                                          |
| E-book         | `.epub`                                         |

* Images and audio require `llm_enabled: true` and a running Ollama instance
  (or OpenAI key) to generate meaningful content.

---

## Installation

### Linux / Arch

```bash
cd wiki_ingestor
bash install_linux.sh
```

This creates a virtualenv, installs all dependencies, writes a default config,
and registers a **systemd user service** that starts at login.

```bash
# Logs
journalctl --user -u wiki-ingestor -f

# Stop
systemctl --user stop wiki-ingestor

# Uninstall
bash install_linux.sh --uninstall
```

### Windows

```bat
cd wiki_ingestor
install_windows.bat
```

This creates a virtualenv, installs dependencies, writes a default config, and
registers a **Windows Task Scheduler** entry that starts silently at logon.

```bat
REM Stop
schtasks /end /tn wiki_ingestor

REM Remove
schtasks /delete /tn wiki_ingestor /f
```

---

## Configuration

The ingestor automatically detects and uses settings from your existing wiki-linux
configuration if found at:
- Linux: `~/.config/wiki-linux/config.json` or `~/wiki/config.json`
- Windows: `%APPDATA%\wiki-linux\config.json` or `%LOCALAPPDATA%\wiki-linux\config.json`

If wiki-linux config is found, `wiki_ingestor` will use its `monitor.watch_dirs`
setting automatically.

You can also create a specific config file at `~/wiki/wiki_ingestor_config.json`:

```json
{
  "watch_dirs": [
    "~/Documents",
    "~/Downloads",
    "/mnt/usb"
  ],
  "output_subdir": "converted",
  "recursive": true,
  "debounce_seconds": 2.0,
  "batch_on_start": true,
  "llm_enabled": false,
  "llm_provider": "ollama",
  "llm_model": "llava",
  "llm_base_url": "http://localhost:11434/v1",
  "log_level": "INFO"
}
```

### Interactive Setup

Run the following command for an interactive setup that guides you through folder selection:

```bash
python -m wiki_ingestor init
```

This will:
- Search for existing wiki-linux configuration
- Prompt you to select folders to watch
- Validate that folders exist (or create them)
- Support multiple folders (comma-separated)

Restart the service after changes:
```bash
# Linux
systemctl --user restart wiki-ingestor

# Windows
schtasks /end /tn wiki_ingestor && schtasks /run /tn wiki_ingestor
```

---

## CLI commands

```bash
# Start the watcher daemon (foreground)
python -m wiki_ingestor watch

# One-shot: convert everything in watch_dirs right now
python -m wiki_ingestor batch

# Interactive setup: configure watch directories
python -m wiki_ingestor init [--force]

# Show effective config + ledger stats
python -m wiki_ingestor status
```

---

## Output format

Every converted file receives a YAML frontmatter header:

```markdown
---
title: "My Report"
source: "/home/user/Documents/My Report.docx"
source_type: "docx"
converted_at: "2026-05-07T14:30:00+00:00"
tags: [wiki-ingestor, auto-converted]
---

# My Report

... converted Markdown content ...
```

This frontmatter is compatible with wiki-linux's `indexer.py` and typical
static-site generators (Jekyll, Hugo, Obsidian).

---

## Enabling image/audio captioning via Ollama

Set in config:
```json
{
  "llm_enabled": true,
  "llm_provider": "ollama",
  "llm_model": "llava",
  "llm_base_url": "http://localhost:11434/v1"
}
```

Then pull the model: `ollama pull llava`

Images will be described in natural language; audio files will be transcribed.

---

## Deduplication

A SQLite ledger at `~/wiki/.ingestor/ledger.db` tracks the SHA-256 hash of
every converted file. A file is only re-converted when its content changes —
identical re-saves are silently skipped.

---

## Project structure

```
wiki_ingestor/
├── __init__.py               # package exports
├── __main__.py               # CLI entry point
├── config.py                 # configuration loader
├── converter.py              # MarkItDown wrapper + ledger
├── watcher.py                # watchdog-based file system observer
├── wiki_ingestor_config.json # default config template
├── requirements.txt
├── install_linux.sh          # systemd user service installer
└── install_windows.bat       # Task Scheduler installer
```
