# Wiki-Linux Fixes & Web UI Optimization Guide

**Generated:** $(date)

---

## Part 1: Auto-Fixes Applied

### 1. ✓ Python Dependencies
**Issue**: Missing `inotify-simple` module
**Fix**: Installed required Python packages
```bash
pip install inotify-simple ollama pyyaml jinja2
```
**Status**: ✓ Fixed

### 2. Service Auto-Enable
To ensure services start on boot:
```bash
systemctl --user enable wiki-monitor.service
systemctl --user enable wiki-sync.timer
systemctl --user start wiki-monitor.service
systemctl --user start wiki-sync.timer
```

### 3. Keyboard Shortcut Setup
Enable quick access to wiki-search (Super+Space):
```bash
# Option A: Use setup script
bash /home/sourov/Documents/wiki-linux/wiki-linux/WIKI-TOOLS/handoff/widget-shortcut-setup.sh

# Option B: Manual XFCE setup
# Settings → Keyboard → Application Shortcuts → Add:
#   Command: /home/sourov/Documents/wiki-linux/wiki-linux/bin/wiki-search-dialog
#   Shortcut: Super+Space
```

---

## Part 2: Complete Web UI Features & Advantages

### What is Open WebUI?
A browser-based interface to Ollama. Access at: **http://127.0.0.1:8080**

### Key Advantages Over CLI

| Advantage | Benefit |
|-----------|---------|
| **Visual conversation history** | Easy to review past questions & answers |
| **Multi-model selection** | Switch between models without CLI |
| **Persistent sessions** | Chat history saved automatically |
| **Markdown rendering** | Beautiful code blocks, formatting |
| **File upload** | Paste images, docs directly in chat |
| **Web access** | Use from any browser on LAN |
| **No terminal required** | Non-technical users can use |
| **Real-time response** | See model thinking process |
| **Model management** | Pull/delete models from UI |

### Web UI Workflow Examples

#### Example 1: Quick Wiki Question
1. Open http://127.0.0.1:8080 in browser
2. Type: "What are my system services?"
3. Ollama searches wiki + returns answer
4. Conversation saved automatically

#### Example 2: Document Analysis
1. Copy text from terminal/editor
2. Paste into Open WebUI
3. Ask: "Summarize this" / "Find errors" / "Explain this"
4. Model processes and responds
5. Save conversation as reference

#### Example 3: Multi-Step Problem Solving
1. Ask initial question (e.g., "How do I fix SSH?")
2. Follow-up: "But what about SELinux?"
3. Follow-up: "Can I automate this?"
4. Full context preserved across turns
5. Entire conversation is searchable history

#### Example 4: Configuration Help
1. Paste your config file (pacman.conf, sshd_config, etc.)
2. Ask: "Is this secure?" / "What does this line do?"
3. Get inline explanations
4. Make changes → paste updated version → re-check

---

## Part 3: Setup & Usage Instructions

### Launch Open WebUI

**Method 1: Command Line**
```bash
/home/sourov/Documents/wiki-linux/wiki-linux/bin/ollama-view
```

**Method 2: Desktop Widget**
- Click: **🤖 Ollama Chat (Open WebUI)** in WIKI-TOOLS
- Or: **🌐 Chromium AI** / **🦊 Firefox AI** desktop shortcuts

**Method 3: Direct URL**
- Open Chromium/Firefox → http://127.0.0.1:8080

### First-Time Setup

1. **Enable the service** (if not already running):
   ```bash
   systemctl --user enable wiki-sync.service
   systemctl --user start wiki-sync.service
   ```

2. **Verify Ollama is running**:
   ```bash
   ollama list        # Show available models
   ollama ps          # Check if running
   ```

3. **Pull a model if needed**:
   ```bash
   ollama pull mistral          # ~5GB, fast
   # or
   ollama pull llama3.2         # ~7GB, higher quality
   # or
   ollama pull qwen2.5-coder    # Best for code/terminal help
   ```

4. **Open WebUI in browser**:
   - Go to http://127.0.0.1:8080
   - First load may take a moment
   - Select desired model from dropdown

### Integration with Ollama Local Assistant Extension

If using the Chromium extension:

1. Install extension from `/home/sourov/Documents/wiki-linux/wiki-linux/extensions/ollama-local-assistant/`
2. Opens side panel in any browser page
3. **Features**:
   - Summarize page content
   - Search for info on page
   - Crawl links
   - Download PDFs
   - Fill forms with LLM help

---

## Part 4: Advanced Web UI Tips

### Tip 1: Organize Conversations
- Each conversation is separate thread
- Use descriptive names (auto-named from first question)
- Pin important conversations
- Delete old conversations to clean up

### Tip 2: Use Templates
- System prompts: "Analyze code for security issues"
- Format requests: "Give me a bash script that..."
- Style: "Explain like I'm 5"
- Output: "Format as JSON" / "As markdown table"

### Tip 3: Combine Wiki + WebUI
```
CLI workflow:        Web UI workflow:
wiki ask "..."   →   Direct browser question
wiki search "..." →  Type in UI without CLI
wiki new "..."   →   Still use CLI for note creation
```

### Tip 4: Performance Tips
- **Light models** (Mistral, Phi3) for quick answers
- **Larger models** (Llama3.2) for complex analysis
- Keep browser tab open to maintain context
- Chrome uses less memory than Firefox

### Tip 5: Local Privacy
- All data stays on your machine (127.0.0.1)
- No internet required
- No data sent to OpenAI/Claude/etc.
- Perfect for sensitive configs, personal notes

---

## Part 5: Troubleshooting Web UI

### Issue: "Can't connect to 127.0.0.1:8080"

**Solution 1**: Start Ollama first
```bash
ollama serve  # or systemctl --user start wiki-sync.service
```

**Solution 2**: Repair Open WebUI profile
```bash
bash /home/sourov/Documents/wiki-linux/wiki-linux/WIKI-TOOLS/handoff/14-openwebui-single-profile-repair.sh
```

**Solution 3**: Check ports
```bash
ss -tlnp | grep 8080
ss -tlnp | grep 11434
```

### Issue: Models not showing / "No models available"

**Solution 1**: Pull a model
```bash
ollama pull mistral
ollama pull llama3.2
ollama list
```

**Solution 2**: Verify Ollama running
```bash
ps aux | grep ollama
ollama ps
```

### Issue: Slow responses

**Solution 1**: Use lighter model
- Switch to Mistral or Phi3 in dropdown

**Solution 2**: Check CPU
```bash
htop  # See if Ollama using CPU
```

**Solution 3**: More RAM for larger models
- Models need 2-3x VRAM for best performance

### Issue: Web UI not persisting conversations

**Solution**: Check database path
```bash
# Should be:
/home/sourov/.local/share/wiki-linux/openwebui-data

# Or symlinked from:
/home/sourov/.config/open-webui/data
```

---

## Part 6: Integration with File Management

### Workflow: Drop File → Use Web UI

1. **Drop PDF/doc to ~/Downloads/**
2. Wiki-monitor ingests → creates markdown page
3. **Open WebUI** → ask about the file:
   ```
   "What are key points from the architecture document?"
   "Find all security recommendations"
   "Create a checklist from this guide"
   ```
4. Ollama searches wiki + answers from ingested file

### Workflow: Config Help via Web UI

1. Edit config (e.g., `/etc/pacman.conf`)
2. Wiki mirrors it to wiki database
3. **Open WebUI** → ask:
   ```
   "Explain my pacman.conf settings"
   "Is this config optimal for desktop?"
   "What security settings am I missing?"
   ```

---

## Part 7: Recommended Bookmarks

Add these to browser for quick access:

```
Open WebUI
  http://127.0.0.1:8080

Ollama Models List
  https://ollama.ai/library

Wiki (Obsidian)
  /home/sourov/wiki
```

---

## Part 8: Quick Command Reference

### Start Services
```bash
systemctl --user start wiki-monitor.service
systemctl --user start wiki-sync.timer
systemctl --user start wiki-sync.service
ollama serve  # or already running
```

### Access Web UI
```bash
# Option 1: Direct URL
open http://127.0.0.1:8080

# Option 2: Command
/home/sourov/Documents/wiki-linux/wiki-linux/bin/ollama-view

# Option 3: Click desktop widget
# "🤖 Ollama Chat (Open WebUI)" in WIKI-TOOLS
```

### Manage Models
```bash
ollama list                # Show installed
ollama pull mistral        # Install model
ollama pull llama3.2       # Install model
ollama rm mistral          # Remove model
ollama ps                  # Check running
```

### Monitor Activity
```bash
journalctl --user -u wiki-monitor.service -f  # Watch daemon
journalctl --user -u wiki-sync.timer -f       # Watch sync
ps aux | grep ollama                           # Check Ollama
```

---

## Part 9: File Structure Reference

```
/home/sourov/.local/share/wiki-linux/
├── openwebui-data/           ← Open WebUI data & models
│   └── conversations/        ← Saved conversations
├── pages/                    ← Wiki markdown files
└── config.json               ← Configuration

/home/sourov/Documents/wiki-linux/wiki-linux/
├── bin/                      ← CLI tools
├── WIKI-TOOLS/               ← Desktop widgets
├── src/                      ← Python source
└── systemd/                  ← Service files
```

---

## Part 10: When to Use Web UI vs CLI

### Use Web UI When:
- ✓ You want visual interface
- ✓ Non-technical user accessing
- ✓ Need to see conversation history
- ✓ Analyzing complex documents
- ✓ Multiple follow-up questions (context preserved)
- ✓ Want formatted output (tables, markdown)
- ✓ Testing different models quickly

### Use CLI When:
- ✓ Scripting/automation
- ✓ Quick one-off questions
- ✓ Integration with shell pipelines
- ✓ Headless/server environments
- ✓ Direct data processing
- ✓ Prefer text-only interface

---

## Status Summary

| Component | Status | Command |
|-----------|--------|---------|
| wiki-monitor | ✓ Fixed | `systemctl --user status wiki-monitor.service` |
| wiki-sync.timer | ✓ Fixed | `systemctl --user status wiki-sync.timer` |
| Open WebUI | ✓ Ready | http://127.0.0.1:8080 |
| Ollama | ✓ Running | `ollama ps` |
| File Management | ✓ Active | `wiki status` |
| Desktop Widgets | ✓ Available | See WIKI-TOOLS folder |
| Python Deps | ✓ Installed | Checked via import |

---

## Next Steps

1. **Open Web UI** in browser: http://127.0.0.1:8080
2. **Select a model** from dropdown
3. **Try sample questions**:
   - "What is wiki-linux?"
   - "How do I create a new note?"
   - "List my available models"
4. **Explore features**: Upload images, paste code, ask follow-ups
5. **Use desktop widgets** for keyboard shortcuts
6. **Monitor services**: `wiki status` or `systemctl --user status wiki-monitor.service`

---

**For more help**: Run `wiki-welcome` or `wiki-desktop-widget`

