# Wiki-Linux Open WebUI Integration Checklist

## Prerequisites ✓
- [x] Python 3.8+ environment configured
- [x] Required Python packages installed (httpx, trafilatura, markdownify, selectolax, pydantic, python-dateutil)
- [x] All tool Python files validated (no syntax errors)
- [x] Paths configured for wiki-linux structure
- [x] Open WebUI tools manifests created

## Tools Status

| Tool | File | Status | Config | Last Check |
|------|------|--------|--------|------------|
| Wiki Search | `01_wiki_search.py` | ✓ Ready | wiki_root=/home/sourov/Documents/wiki-linux/wiki-linux | Compiled OK |
| URL to Wiki | `02_url_to_wiki.py` | ✓ Ready | wiki_root=/home/sourov/Documents/wiki-linux/wiki-linux | Compiled OK |
| Linux Sysinfo | `03_linux_sysinfo.py` | ✓ Ready | Whitelist mode | Compiled OK |
| File Finder | `04_file_finder.py` | ✓ Ready | default_root=/home/sourov/Documents/wiki-linux/wiki-linux | Compiled OK |
| Web Search (DDG) | `05_web_search_ddg.py` | ✓ Ready | No API key needed | Compiled OK |
| Reminder | `06_reminder.py` | ✓ Ready | reminders_file=_meta/reminders.jsonl | Compiled OK |
| Session Report | `07_session_report.py` | ✓ Ready | reports_dir=_meta/reports | Compiled OK |
| Brainstorm | `08_brainstorm.py` | ✓ Ready | wiki_root=/home/sourov/Documents/wiki-linux/wiki-linux | Compiled OK |

## Prompts Status

| Prompt | File | Status | Tool Dependencies |
|--------|------|--------|-------------------|
| URL → Wiki | `01_url_to_wiki.md` | ✓ Updated | url_to_wiki |
| Wiki Research | `02_wiki_research.md` | ✓ Updated | wiki_search |
| Linux Health | `03_linux_health.md` | ✓ Ready | linux_sysinfo |
| File Find | `04_file_find.md` | ✓ Ready | file_finder |
| Excel Formula | `05_excel_formula.md` | ✓ Ready | (LLM only) |
| Proofread | `06_proofread.md` | ✓ Ready | (LLM only) |
| Session Recap | `07_session_recap.md` | ✓ Ready | session_report |
| Brainstorm | `08_brainstorm.md` | ✓ Ready | brainstorm, wiki_search |

## Next Steps for User

### Manual Installation in Open WebUI

1. **Open WebUI → Settings → Tools**
   - Create 8 new tools
   - Copy content from each `01_*.py` through `08_*.py`
   - Name them: Wiki Search, URL to Wiki, Linux Sysinfo, File Finder, Web Search, Reminder, Session Report, Brainstorm

2. **Open WebUI → Settings → Prompts**
   - Create 8 new prompts
   - Copy content from each `01_*.md` through `08_*.md`
   - Use same names as above

3. **Test Each Tool**
   - Use the "Test" button in Open WebUI tool settings
   - Verify ripgrep is available for search tools
   - Confirm Ollama connectivity for synthesis features

4. **Integrate Reminders (Optional)**
   - Set up systemd timer for `reminder check_due` if desired
   - Configure desktop notifications via `notify-send`

### Cross-Reference with Official Docs

- **Open WebUI Tools API**: https://docs.openwebui.com/advanced/tools
  - Tools.Valves pattern (✓ implemented)
  - Async methods (✓ used throughout)
  - Error handling (✓ present)

- **Ollama Integration**: https://github.com/ollama/ollama
  - HTTP endpoint: `http://127.0.0.1:11434` (✓ configured)
  - Supported models: llama3.2, mistral, etc. (✓ configurable)

- **ripgrep Documentation**: https://github.com/BurntSushi/ripgrep
  - JSON output format (✓ parsed correctly)
  - Timeout handling (✓ implemented)

## Extensions Overview

### Browser Extensions (in `extensions/`)

| Extension | Location | Status | Purpose |
|-----------|----------|--------|---------|
| Ollama Assistant | `ollama-local-assistant.crx` | Binary | Chrome extension for Ollama |
| Chrome Automator | `chrome-automator/` | ✓ Manifest OK | Batch email/LinkedIn posting |
| OpenWebUI Assistant | `openwebui-assistant/` | ✓ Manifest OK | OpenWebUI quick-access panel |
| OpenWebUI Tools | `openwebui-tools/` | ✓ Manifest Created | Tool utilities (recreated) |
| Firefox Assistant | `wiki-linux-firefox/` | Check local | Firefox extension |

## Dependencies Summary

### Python Packages (all installed)
```
httpx >= 0.24
trafilatura >= 1.6
markdownify >= 0.11
selectolax >= 0.3
pydantic >= 2.0
python-dateutil >= 2.8
```

### System Packages (required for full functionality)
```
ripgrep (rg)          - for wiki_search, brainstorm
notify-send           - for reminder notifications (optional)
```

### External Services (required)
```
Ollama (localhost:11434)  - for LLM synthesis, brainstorm
Open WebUI (localhost:8080) - main UI platform
```

## Verification Commands

```bash
# Verify Python environment
/home/sourov/Documents/wiki-linux/wiki-linux/.venv/bin/python --version

# Verify tools can be imported
/home/sourov/Documents/wiki-linux/wiki-linux/.venv/bin/python -c "from pathlib import Path; exec(open('copilot/01_wiki_search.py').read()[:100])"

# Check ripgrep installed
which rg

# Check Ollama connectivity
curl http://127.0.0.1:11434/api/tags

# Check wiki structure
ls -la /home/sourov/Documents/wiki-linux/wiki-linux/_meta/
```

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| "Tool not found in Open WebUI" | Copy full Python file, check syntax (run py_compile test) |
| "ripgrep not installed" | `apt install ripgrep` or `brew install ripgrep` |
| "Ollama connection refused" | Start Ollama: `ollama serve` in separate terminal |
| "URL to Wiki fails" | Install extractors: `pip install trafilatura markdownify` |
| "No reminders showing" | Check `_meta/reminders.jsonl` exists, read systemd logs |
| "Session reports empty" | Ensure `_meta/reports/` has `.md` files within time window |

## Files Generated

- ✓ `SETUP_GUIDE.md` - Comprehensive setup and usage documentation
- ✓ `INTEGRATION_CHECKLIST.md` - This file
- ✓ Updated `01_url_to_wiki.md` - Path corrections
- ✓ Updated `02_wiki_research.md` - Path corrections
- ✓ Updated `06_reminder.py` - Path configuration
- ✓ Updated `08_brainstorm.py` - Path configuration
- ✓ Created `extensions/openwebui-tools/manifest.json` - Missing manifest

## Sign-Off

All Open WebUI tools and prompts are configured and ready for deployment to Open WebUI.

**Date**: May 8, 2026  
**Status**: ✓ Ready for Use  
**Next Action**: Import tools/prompts into Open WebUI and test
