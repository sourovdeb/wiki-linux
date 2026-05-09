# Open WebUI Tools & Prompts Setup Guide

This directory contains 8 Open WebUI tools and 8 corresponding prompts, configured for the `wiki-linux` knowledge base system.

## Quick Start

### 1. Prerequisites
- Open WebUI running at `http://127.0.0.1:8080`
- Ollama running at `http://127.0.0.1:11434`
- Python 3.8+ with required packages installed:
  ```bash
  pip install httpx trafilatura markdownify selectolax pydantic python-dateutil
  ```
- `ripgrep` (`rg`) installed for full-text search

### 2. Installation

#### Copy Tools to Open WebUI
1. Navigate to Open WebUI settings → **Tools**
2. For each Python file (`01_wiki_search.py` through `08_brainstorm.py`):
   - Click **Create new tool**
   - Copy the entire Python file content
   - Save

#### Import Prompts to Open WebUI
1. Navigate to Open WebUI settings → **Prompts**
2. For each Markdown file (`01_url_to_wiki.md` through `08_brainstorm.md`):
   - Click **Create new prompt**
   - Copy the Markdown content
   - Save

### 3. Configuration

All tools use configurable **Valves** (settings). Defaults are set for `wiki-linux`:

| Tool | Key Settings |
|------|--------------|
| `01_wiki_search` | `wiki_root`, `ollama_base`, `model`, `timeout_s` |
| `02_url_to_wiki` | `wiki_root`, `subdir` (= `converted/`), `timeout_s` |
| `03_linux_sysinfo` | `timeout_s`, `include_systemctl` |
| `04_file_finder` | `default_root`, `max_results`, `max_depth` |
| `05_web_search_ddg` | `timeout_s`, `max_results`, `region` |
| `06_reminder` | `reminders_file`, `notify` (notify-send) |
| `07_session_report` | `reports_dir`, `max_reports`, `max_chars_per_report` |
| `08_brainstorm` | `wiki_root`, `ollama_base`, `model`, `rg_timeout_s` |

All paths default to `/home/sourov/Documents/wiki-linux/wiki-linux` and related subdirectories.

## Tool Roster

| # | Tool | Purpose | Requires |
|---|------|---------|----------|
| **01** | `wiki_search` | Full-text search of wiki via ripgrep, optional Ollama synthesis | `rg`, Ollama |
| **02** | `url_to_wiki` | Fetch URL → markdown → `wiki/converted/` (wiki_ingestor pickup) | `httpx`, `trafilatura`, `markdownify` |
| **03** | `linux_sysinfo` | Read-only whitelist system info snapshot | — |
| **04** | `file_finder` | Glob search rooted in wiki (jail = `$HOME`) | — |
| **05** | `web_search_ddg` | DuckDuckGo HTML search | `httpx`, `selectolax` |
| **06** | `reminder` | Add/list/check_due reminders (systemd timer for checks) | `python-dateutil`, (optional) `notify-send` |
| **07** | `session_report` | Read latest `_meta/reports/*.md`, optional Ollama recap | Ollama (optional) |
| **08** | `brainstorm` | Wiki-grounded idea generation via Ollama | `rg`, Ollama |

## Usage Examples

### Wiki Search (with LLM synthesis)
**Prompt**: "Search my wiki for 'systemd timers' and synthesise an answer."

**Steps**:
1. Use prompt `02_wiki_research` or call `wiki_search` tool directly
2. Tool returns matching snippets from `*.md` files
3. If `answer_with_llm=true`, feeds top snippets to Ollama model for synthesis
4. Output includes citations: `[file.md:line]`

### Convert & Ingest URL
**Prompt**: "Save this tech article to my wiki: https://example.com/article"

**Steps**:
1. Use prompt `01_url_to_wiki`
2. `url_to_wiki` tool fetches, extracts main text to Markdown
3. Saves as `wiki/converted/<slug>.md`
4. `wiki_ingestor` automatically picks up and processes on next sync
5. Output includes preview and follow-up questions

### Check System Health
**Prompt**: "What's my system status?"

**Steps**:
1. Use prompt `03_linux_health`
2. `linux_sysinfo` runs whitelist-only commands (no sudo, no shell)
3. Returns disk, memory, load, top processes, failed systemd units
4. Suitable for quick diagnostics

### Find Files
**Prompt**: "Find all Python scripts in my wiki"

**Steps**:
1. Use prompt `04_file_find`
2. `file_finder` globs for `*.py` under wiki root
3. Returns table: path, size, modified time
4. Can optionally preview largest match

### Web Search (No Tracking)
**Prompt**: "Search DuckDuckGo for 'systemd best practices'"

**Steps**:
1. Use prompt (custom) or call `web_search_ddg` tool
2. Returns ranked results: title, URL, snippet
3. No tracking, free, no API key needed

### Add Reminder
**Prompt**: "Remind me to review backup configs tomorrow at 9am"

**Steps**:
1. Call `reminder` tool with message + when
2. Stores in `_meta/reminders.jsonl`
3. Systemd timer runs `check_due` periodically
4. Desktop notification on due (if `notify-send` available)

### Session Recap
**Prompt**: "What happened in my last session?"

**Steps**:
1. Use prompt `07_session_recap`
2. `session_report` reads recent reports from `_meta/reports/`
3. Optional: sends to Ollama for a one-paragraph summary
4. Useful after system reboots or long gaps

### Brainstorm Ideas
**Prompt**: "Generate ideas for improving my wiki-linux setup. Use my notes."

**Steps**:
1. Use prompt `08_brainstorm`
2. `brainstorm` tool ripgreps wiki for related snippets (grounding)
3. Feeds snippets + topic to Ollama for creative generation
4. Returns cited ideas with sources

## Troubleshooting

### Tool Disabled or Not Showing in Open WebUI
- Ensure Python requirements are installed in Open WebUI's environment
- Check Open WebUI logs for import/syntax errors
- Verify `required_open_webui_version` is met (0.4.0+)

### Search Returns "ripgrep not found"
- Install ripgrep: `sudo apt install ripgrep` (Debian/Ubuntu) or `brew install ripgrep` (macOS)

### URL to Wiki Fails with "no extractor available"
- Install extractors: `pip install trafilatura markdownify`

### Ollama Synthesis Returns Error
- Ensure Ollama is running: `ollama serve` in another terminal
- Check `ollama_base` valve is correct (default: `http://127.0.0.1:11434`)
- Verify model exists: `ollama list`

### Reminders Not Firing
- Check systemd timer is running: `systemctl status wiki-reminder.timer` (if configured)
- Check `notify-send` is installed for desktop notifications: `sudo apt install libnotify-bin`

### Session Report Empty
- Ensure `_meta/reports/` directory exists with `.md` files
- Check `since_hours` parameter isn't too restrictive

## Integration with Wiki Ingestor

The `url_to_wiki` tool saves files to `wiki/converted/` by default. The `wiki_ingestor` watches this directory and:
1. Converts each markdown file
2. Embeds metadata (title, timestamp, source)
3. Moves processed file to the main wiki
4. Updates indices

To trigger immediately:
```bash
/path/to/wiki-kb-sync
```

## Extending

### Add Custom Prompts
Create new `.md` files in this directory with YAML frontmatter:
```yaml
---
title: My Custom Prompt
slug: custom
description: Brief description
---

Your prompt template using {{variable}} syntax.
```

### Modify Valve Defaults
Edit any tool's `class Valves` to change defaults. Recommended for:
- Different wiki location
- Alternative Ollama model
- Custom notification title
- Different timeout values

## License

All tools and prompts are MIT-licensed. Attribution to `wiki-linux` appreciated.

## See Also

- [wiki-linux Architecture](../docs/SYSTEM-ARCHITECTURE.md)
- [Open WebUI Docs](https://docs.openwebui.com/)
- [Ollama Docs](https://github.com/ollama/ollama)
