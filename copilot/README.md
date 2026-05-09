# openui-tools — Open WebUI prompts + tools for wiki-linux

Branch payload. Drop into the repo as `openui-tools/` (or wherever fits the layout).

## Files

```
prompts/        8 Open WebUI prompt templates
tools/          8 Open WebUI Tools (Python, async, valves)
```

## Tool roster

| # | Tool | Purpose |
|---|---|---|
| 01 | `wiki_search` | ripgrep search of `~/wiki`, optional Ollama synthesis |
| 02 | `url_to_wiki` | fetch URL → markdown → `~/wiki/converted/` (wiki_ingestor picks up) |
| 03 | `linux_sysinfo` | read-only whitelist sysinfo |
| 04 | `file_finder` | glob search rooted in `~/wiki` (jail = `$HOME`) |
| 05 | `web_search_ddg` | DuckDuckGo HTML search |
| 06 | `reminder` | add / list / check_due (the "automatic" loop runs `check_due`) |
| 07 | `session_report` | reads latest `_meta/reports/*.md`, optional Ollama recap |
| 08 | `brainstorm` | wiki-grounded idea generation via Ollama |

## Prompts

| # | Prompt | Tools used |
|---|---|---|
| 01 | URL → wiki + bullet summary | `url_to_wiki` |
| 02 | Wiki research + cited answer | `wiki_search` |
| 03 | Linux health check | `linux_sysinfo` |
| 04 | File find + summarise | `file_finder` |
| 05 | Excel formula | — |
| 06 | Proofread (diff output) | — |
| 07 | Last session recap | `session_report` |
| 08 | Wiki-grounded brainstorm | `brainstorm` (+ `wiki_search`) |

## Configuration

All tools are pre-configured for **wiki-linux** at `/home/sourov/Documents/wiki-linux/wiki-linux`.

Each tool has adjustable **Valves** (settings) in Open WebUI for customization:
- `wiki_root`: Main wiki directory
- `ollama_base`: Ollama HTTP endpoint (default: `http://127.0.0.1:11434`)
- `model`: LLM model for synthesis (default: `llama3.2:3b` for search, `mistral` for brainstorm)
- `timeout_s`: Tool execution timeout
- Other tool-specific settings (see `SETUP_GUIDE.md`)

## Integration Status

✓ All tools syntax-validated  
✓ All paths configured for wiki-linux  
✓ Dependencies installed  
✓ Ready for Open WebUI import  

**See `SETUP_GUIDE.md` for detailed installation and usage.**  
**See `INTEGRATION_CHECKLIST.md` for verification steps.**
- `repo_root = /home/sourov/Documents/wiki-linux/wiki-linux`
- `reports_dir = $repo_root/_meta/reports`
- `ollama = http://127.0.0.1:11434`
- `default_model = llama3.2:3b` (per-tool override via valves)
- All tools respect EXPECTATIONS guarantees: read-only on `/etc`, no destructive ops, no sudo, no path escapes.
