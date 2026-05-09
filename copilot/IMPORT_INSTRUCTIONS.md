# Manual Import Instructions for Open WebUI

Open WebUI is running at: **http://127.0.0.1:8080**

All 8 tools and 8 prompts are ready in `/home/sourov/Documents/wiki-linux/wiki-linux/copilot/`

## Quick Import Steps

### Step 1: Import Tools (8 total)

1. Open Open WebUI → **Settings** (gear icon, bottom-left)
2. Select **Tools** tab
3. Click **"+ Create New Tool"** button
4. For each tool below, copy the entire Python file content into the editor:

| # | File | Name |
|---|------|------|
| 1 | `01_wiki_search.py` | Wiki Search |
| 2 | `02_url_to_wiki.py` | URL to Wiki |
| 3 | `03_linux_sysinfo.py` | Linux Sysinfo |
| 4 | `04_file_finder.py` | File Finder |
| 5 | `05_web_search_ddg.py` | Web Search (DDG) |
| 6 | `06_reminder.py` | Reminder |
| 7 | `07_session_report.py` | Session Report |
| 8 | `08_brainstorm.py` | Brainstorm |

**Note**: Open WebUI automatically parses the Python `Valves` class and generates configuration UI.

### Step 2: Import Prompts (8 total)

1. Open Open WebUI → **Settings**
2. Select **Prompts** tab
3. Click **"+ Create New Prompt"** button
4. For each prompt below, copy the entire Markdown file content:

| # | File | Name |
|---|------|------|
| 1 | `01_url_to_wiki.md` | URL → Wiki + Bullet Summary |
| 2 | `02_wiki_research.md` | Wiki Research + Cited Answer |
| 3 | `03_linux_health.md` | Linux Health Check |
| 4 | `04_file_find.md` | File Find + Summarise |
| 5 | `05_excel_formula.md` | Excel Formula |
| 6 | `06_proofread.md` | Proofread (Diff Output) |
| 7 | `07_session_recap.md` | Last Session Recap |
| 8 | `08_brainstorm.md` | Wiki-grounded Brainstorm |

### Step 3: Test in Chat

1. Open a new chat in Open WebUI
2. Type or select one of the prompts (they'll appear in the prompt selector)
3. Run the prompt to invoke the associated tool
4. Verify results

---

## File Locations

All files are in:
```
/home/sourov/Documents/wiki-linux/wiki-linux/copilot/
```

Access via command line:
```bash
cd /home/sourov/Documents/wiki-linux/wiki-linux/copilot
cat 01_wiki_search.py       # View first tool
cat 01_url_to_wiki.md       # View first prompt
```

---

## Verification

Run the deployment checker:
```bash
/home/sourov/Documents/wiki-linux/wiki-linux/bin/wiki-openwebui-deploy
```

This verifies all files are present and ready for import.

---

## Support

- **Setup Guide**: `SETUP_GUIDE.md` (comprehensive documentation)
- **Integration Checklist**: `INTEGRATION_CHECKLIST.md` (verification steps)
- **Completion Summary**: `COMPLETION_SUMMARY.md` (final status)

After importing, refer to `SETUP_GUIDE.md` in the same directory for detailed usage of each tool.
