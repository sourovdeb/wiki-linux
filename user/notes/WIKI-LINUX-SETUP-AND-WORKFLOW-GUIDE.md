# Wiki-Linux: Complete Setup & Workflow Guide

**Generated**: $(date '+%Y-%m-%d %H:%M:%S')  
**System**: Arch Linux 6.19.12-arch1-1  
**Location**: `/home/sourov/Documents/wiki-linux/wiki-linux`

---

## ⚡ QUICK ANSWERS TO YOUR QUESTIONS

### 1. 🚀 At Boot: How Many Things Open?

**Total: 11 systemd services enabled at boot**

| Service | Type | Purpose | Can Disable? |
|---------|------|---------|--------------|
| `wiki-boot-health.service` | Service | Boot health check | ⚠️ Yes (optional) |
| `wiki-monitor.service` | Service | File watching daemon | ❌ Core feature |
| `wiki-ollama.service` | Service | Local LLM backend | ❌ Core feature |
| `wiki-openwebui.service` | Service | Web UI server | ⚠️ Yes (if not used) |
| `wiki-screensaver-watch.service` | Service | Screensaver watcher | ⚠️ Yes (optional) |
| `wiki-sync.timer` | Timer | Auto-commit (5min) | ⚠️ Yes (manual sync) |
| `wiki-wallpaper.timer` | Timer | Wallpaper refresh (30sec) | ⚠️ Yes (static wallpaper) |
| `aeon-habits.service` | Service | Habit tracking | ⚠️ Yes (optional) |
| `aeon-log-translator.service` | Service | Log translation | ⚠️ Yes (optional) |
| `aeon-notification.service` | Service | Notifications | ⚠️ Yes (optional) |
| `aeon-timeshift.timer` | Timer | Backup automation | ⚠️ Yes (manual backup) |

**Recommendation**: Keep wiki-monitor, wiki-ollama, wiki-sync.timer. Disable the rest if not needed.

**Popups at boot**:
- Welcome popup (shows page count, status)
- Optional: Desktop live widget (if autostart enabled)

---

### 2. 🌐 Is Web Open UI the Main UI Hub?

**Answer: NO** — You have **5 different UI entry points**. Choose your preferred workflow:

#### UI Hierarchy (Pick Your Primary)

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR 5 UI OPTIONS                        │
├─────────────────────────────────────────────────────────────┤
│ 1. 🌐 Web UI (Open WebUI)         http://127.0.0.1:8080    │
│    ↳ Chat interface, model switching, web-based            │
│    ↳ Best for: Long conversations, web browsing            │
│                                                             │
│ 2. 🖥️ Terminal (`wiki` command)                            │
│    ↳ CLI power user interface                              │
│    ↳ Best for: Quick tasks, automation, SSH                │
│                                                             │
│ 3. 🔍 Desktop Widgets (WIKI-TOOLS/)                        │
│    ↳ XFCE shortcuts, quick actions                         │
│    ↳ Best for: Desktop integration, keyboard shortcuts     │
│                                                             │
│ 4. 📝 Obsidian (GUI wiki viewer)                           │
│    ↳ Full GUI wiki browsing, editing, linking             │
│    ↳ Best for: Wiki navigation, note taking                │
│                                                             │
│ 5. 🌐 Browser Extension (Chromium)                         │
│    ↳ Side-panel AI assistant for web browsing             │
│    ↳ Best for: Web research, page summarization            │
└─────────────────────────────────────────────────────────────┘
```

**Recommended Primary UI by Use Case**:
- **Knowledge worker**: Obsidian + Terminal
- **Web researcher**: Browser Extension + Web UI
- **Power user**: Terminal + Desktop Widgets
- **Casual user**: Web UI + Desktop Widgets

**All UIs connect to the same backend** (Ollama + wiki vault), so use whatever feels natural!

---

### 3. 📁 Where Should User Save Main Files?

**The file workflow is automatic. Drop files in these watched locations:**

```
┌────────────────────────────────────────────────────────────┐
│                    FILE DROP ZONES                          │
├────────────────────────────────────────────────────────────┤
│ ~/Downloads/                → Auto-ingested by daemon      │
│ ~/wiki/user/notes/          → Manual notes (you write)     │
│ ~/wiki/user/research/       → Research papers, docs        │
│ ~/wiki/user/projects/       → Project documentation        │
│ ~/wiki/sources/             → Source material              │
├────────────────────────────────────────────────────────────┤
│ ⚠️ DO NOT EDIT:                                            │
│ ~/wiki/system/              → Auto-generated config docs   │
│ ~/wiki/_meta/               → Auto-generated metadata      │
└────────────────────────────────────────────────────────────┘
```

#### Workflow Examples:

**Example 1: Save a PDF paper**
```bash
# Drop anywhere:
cp ~/paper.pdf ~/Downloads/
# OR
cp ~/paper.pdf ~/wiki/user/research/

# What happens automatically:
# 1. wiki-monitor detects file (inotify)
# 2. Calls Ollama to read & summarize
# 3. Creates wiki/user/research/paper.md
# 4. 5 min later: auto-commits to git
```

**Example 2: Create a quick note**
```bash
wiki new "My networking notes"
# Opens in $EDITOR
# Save & close → auto-commits in 5 min
```

**Example 3: Manual markdown file**
```bash
# Just drop it in:
vim ~/wiki/user/notes/my-note.md
# Write markdown directly
# Save → auto-commits in 5 min
```

---

### 4. 🔄 Does User Require Manual Markdown Conversion?

**Answer: NO** — Automatic conversion for most files!

#### Supported File Types (Auto-Conversion)

| File Type | Auto-Convert? | Notes |
|-----------|---------------|-------|
| `.pdf` | ✅ Yes | Ollama extracts text + summarizes |
| `.txt` | ✅ Yes | Direct ingestion |
| `.md` | ✅ Already markdown | No conversion needed |
| `.html` | ✅ Yes | HTML → Markdown |
| `.docx` | ⚠️ Partial | May need `pandoc` |
| `.epub` | ⚠️ Partial | May need `pandoc` |
| Images | ❌ No | Manual description needed |
| Videos | ❌ No | Manual notes needed |

#### Manual Override

If you want to manually convert:
```bash
wiki ingest ~/Downloads/document.pdf
# Forces immediate processing (don't wait for daemon)
```

---

### 5. ⚙️ And Then What? (Complete File Lifecycle)

```
┌─────────────────────────────────────────────────────────────┐
│              FILE LIFECYCLE (Automatic)                      │
└─────────────────────────────────────────────────────────────┘

1. 📂 YOU DROP FILE
   ↓
   ~/Downloads/paper.pdf
   
2. 👁️ DAEMON DETECTS (inotify)
   ↓
   wiki-monitor.service sees the file
   
3. 🤖 OLLAMA PROCESSES
   ↓
   - Reads PDF content
   - Summarizes key points
   - Extracts metadata
   
4. 📝 MARKDOWN CREATED
   ↓
   ~/wiki/user/research/paper.md
   (Frontmatter: title, created, tags)
   
5. 🔍 SEARCHABLE IMMEDIATELY
   ↓
   wiki search "paper topic"
   wiki ask "What does the paper say about X?"
   
6. 💾 AUTO-COMMIT (5 min timer)
   ↓
   Git commit + push to GitHub
   
7. 📊 INDEXED FOR SEARCH
   ↓
   Available in all UIs:
   - Terminal: wiki search/ask
   - Web UI: chat queries
   - Obsidian: wiki links
   - Desktop widgets: search dialog

✅ DONE — No manual intervention needed!
```

---

### 6. 🎨 Interactive Desktop Wallpaper

**You already have dynamic wallpaper! It's running.**

Current system:
- **wiki-wallpaper.timer** — Updates every 30 seconds
- **wiki-wallpaper-gen** — Python script generates PNG with live stats
- **wiki-desktop-live** — Terminal overlay widget (optional)

#### What it shows:
- 📊 Page count in vault
- 📝 Total git commits
- 💾 Disk space available
- 🤖 Ollama models loaded
- ⏰ Last update time
- 🕐 Current date & time

#### GitHub Interactive Desktop Projects (Research)

If you want MORE interactivity:

**Option 1: Conky** (Most popular)
```bash
sudo pacman -S conky
# Config: ~/.config/conky/conky.conf
# Shows: CPU, RAM, network, custom scripts
```

**Option 2: Polybar** (Status bar)
```bash
sudo pacman -S polybar
# Modern status bar (replaces XFCE panel)
```

**Option 3: Rainmeter-style (PyWal + Rofi)**
```bash
sudo pacman -S pywal rofi
# Dynamic color schemes + launcher
```

**Option 4: Keep Current System**
Your `wiki-wallpaper-gen` is already interactive (updates every 30sec with live data). Consider:
- Increase font size (more readable)
- Add more metrics (Ollama status, service health)
- Add clickable overlays (wiki-desktop-live)

---

### 7. 📝 Todo List & Session Reports (Improvements Needed)

**Current State:**
- No dedicated todo system found in wiki-linux
- "Aeon" services seem to handle habits/notifications
- Session reports: `~/wiki/_meta/session/*.md` (static markdown)

**Recommendations:**

#### Todo List Improvements
```bash
# Option 1: Use wiki tasks
wiki task "Fix networking" "Need to configure static IP"
# Creates _meta/tasks/<date>-<title>.md

# Option 2: Integrate with Obsidian Tasks plugin
# Install: Obsidian → Community Plugins → "Tasks"
# Syntax: - [ ] Task name

# Option 3: Use Web UI for task tracking
# Open http://127.0.0.1:8080
# Create "Tasks" knowledge base
```

#### Interactive Session Reports

**Current** (static markdown):
```
~/wiki/_meta/session/2026-05-05.md
```

**Make Interactive** (2 options):

**Option A: HTML Dashboard**
```bash
# Create interactive HTML report
cat << 'EOF' > ~/wiki/_meta/session/interactive-dashboard.html
<!DOCTYPE html>
<html>
<head><title>Wiki Session Dashboard</title></head>
<body>
  <h1>Session Analytics</h1>
  <div id="stats"></div>
  <script>
    // Fetch session data
    fetch('2026-05-05.md')
      .then(r => r.text())
      .then(data => {
        document.getElementById('stats').innerHTML = 
          '<pre>' + data + '</pre>';
      });
  </script>
</body>
</html>
EOF

# Open in browser:
xdg-open ~/wiki/_meta/session/interactive-dashboard.html
```

**Option B: Obsidian Dataview**
```markdown
<!-- In Obsidian, enable Dataview plugin -->
<!-- Create query in any note: -->

```dataview
TABLE created, updated, tags
FROM "_meta/session"
SORT created DESC
LIMIT 10
```
```

---

## 🔧 AUTOMATIC SETUP SCRIPT

I'll create a script to automate everything that doesn't need manual intervention:

```bash
#!/bin/bash
# AUTO-SETUP-WIKI-LINUX.sh
# Automatically configure wiki-linux optimal settings

echo "🚀 Wiki-Linux Auto-Setup"
echo "========================"
echo ""

# 1. Enable core services only (disable optional)
echo "1️⃣ Optimizing boot services..."
systemctl --user enable wiki-monitor.service
systemctl --user enable wiki-ollama.service
systemctl --user enable wiki-openwebui.service
systemctl --user enable wiki-sync.timer

# Disable optional services
systemctl --user disable aeon-habits.service 2>/dev/null || true
systemctl --user disable aeon-log-translator.service 2>/dev/null || true
systemctl --user disable aeon-notification.service 2>/dev/null || true
systemctl --user disable wiki-boot-health.service 2>/dev/null || true

echo "✅ Core services enabled, optional services disabled"

# 2. Set up keyboard shortcut (XFCE)
echo ""
echo "2️⃣ Configuring keyboard shortcuts..."
if command -v xfconf-query &>/dev/null; then
    xfconf-query -c xfce4-keyboard-shortcuts -p '/commands/custom/<Super>space' \
        -n -t string -s 'wiki-search-dialog' 2>/dev/null || \
    xfconf-query -c xfce4-keyboard-shortcuts -p '/commands/custom/<Super>space' \
        -s 'wiki-search-dialog'
    echo "✅ Keyboard shortcut: Super+Space → wiki-search"
else
    echo "⚠️ XFCE not detected, skipping keyboard shortcut"
fi

# 3. Create desktop shortcuts
echo ""
echo "3️⃣ Creating desktop shortcuts..."
mkdir -p ~/Desktop
cp ~/Documents/wiki-linux/wiki-linux/WIKI-TOOLS/1-SEARCH-BOX.desktop ~/Desktop/ 2>/dev/null
cp ~/Documents/wiki-linux/wiki-linux/WIKI-TOOLS/7-CHROMIUM-AI.desktop ~/Desktop/ 2>/dev/null
cp ~/Documents/wiki-linux/wiki-linux/WIKI-TOOLS/9-DASHBOARD.desktop ~/Desktop/ 2>/dev/null
chmod +x ~/Desktop/*.desktop 2>/dev/null
echo "✅ Desktop shortcuts created"

# 4. Verify Ollama models
echo ""
echo "4️⃣ Checking Ollama models..."
if ollama list | grep -q "mistral\|llama3.2\|qwen2.5-coder"; then
    echo "✅ Ollama models detected"
else
    echo "⚠️ No Ollama models found. Install with:"
    echo "   ollama pull mistral"
fi

# 5. Test Web UI
echo ""
echo "5️⃣ Testing Web UI..."
if curl -s http://127.0.0.1:8080 >/dev/null; then
    echo "✅ Web UI accessible: http://127.0.0.1:8080"
else
    echo "⚠️ Web UI not responding. Check wiki-openwebui.service"
fi

# 6. Configure git auto-sync
echo ""
echo "6️⃣ Configuring git auto-sync..."
if cd ~/Documents/wiki-linux/wiki-linux && git remote -v | grep -q "origin"; then
    echo "✅ Git remote configured"
else
    echo "⚠️ No git remote found. Add with:"
    echo "   cd ~/Documents/wiki-linux/wiki-linux"
    echo "   git remote add origin <your-repo-url>"
fi

echo ""
echo "✅ Auto-setup complete!"
echo ""
echo "📋 Next Manual Steps:"
echo "   1. Configure git remote (if not done)"
echo "   2. Test keyboard shortcut: Press Super+Space"
echo "   3. Open Web UI: http://127.0.0.1:8080"
echo "   4. Review services: systemctl --user status wiki-*"
echo ""
```

---

## 📚 MANUAL SETUP CHECKLIST

These require your input:

### 1. Git Remote Configuration
```bash
cd ~/Documents/wiki-linux/wiki-linux
git remote add origin git@github.com:your-username/wiki-linux.git
git push -u origin main
```

### 2. Obsidian Setup (Optional)
```bash
# Install Obsidian
yay -S obsidian

# Open vault:
obsidian ~/Documents/wiki-linux/wiki-linux
```

### 3. Browser Extension (Optional)
```bash
# Build extension:
bash ~/Documents/wiki-linux/wiki-linux/WIKI-TOOLS/handoff/16-package-ollama-extension.sh

# Load in Chromium:
# 1. Open chrome://extensions
# 2. Enable Developer Mode
# 3. Load Unpacked
# 4. Select: ~/Documents/wiki-linux/wiki-linux/_meta/reports/extension-build/
```

### 4. Custom Prompts (Optional)
```bash
# Add your own prompts:
mkdir -p ~/Documents/wiki-linux/wiki-linux/copilot/copilot-custom-prompts
vim ~/Documents/wiki-linux/wiki-linux/copilot/copilot-custom-prompts/my-prompt.md
```

---

## 🎯 RECOMMENDED DAILY WORKFLOW

### Morning (Login)
1. Welcome popup appears (ignore or read status)
2. Everything runs automatically

### During Work
3. Drop files → `~/Downloads/` or `~/wiki/user/research/`
4. Create notes → `wiki new "Title"` or `Super+Space → New Note`
5. Search → `wiki search "keyword"` or `Super+Space → Search`
6. Ask questions → `wiki ask "question"` or Web UI chat

### Evening (Shutdown)
7. Auto-commit runs (no action needed)
8. Optional: `wiki-safe-shutdown` (graceful shutdown)

---

## 🔗 QUICK REFERENCE CARD

```
┌───────────────────────────────────────────────────────┐
│           WIKI-LINUX QUICK REFERENCE                  │
├───────────────────────────────────────────────────────┤
│ 🔍 Search:        Super+Space OR wiki search          │
│ 📝 New Note:      wiki new "Title"                    │
│ 🤖 Ask LLM:       wiki ask "Question"                 │
│ 🌐 Web UI:        http://127.0.0.1:8080               │
│ 📊 Status:        wiki status                         │
│ 🔄 Sync:          Automatic every 5 min               │
│ 📂 Drop Files:    ~/Downloads/ (auto-processed)       │
│ ✅ Check Health:  wiki lint                           │
├───────────────────────────────────────────────────────┤
│ UI Options:                                           │
│  1. Terminal       → wiki command                     │
│  2. Web Browser    → http://127.0.0.1:8080            │
│  3. Desktop        → Super+Space                      │
│  4. Obsidian       → wiki open                        │
│  5. Extension      → Chromium side panel              │
└───────────────────────────────────────────────────────┘
```

---

## 🐛 TROUBLESHOOTING

### Problem: Services not starting
```bash
systemctl --user status wiki-monitor.service
journalctl --user -u wiki-monitor.service -n 50
```

### Problem: Ollama not responding
```bash
systemctl --user restart wiki-ollama.service
ollama list
```

### Problem: Web UI not accessible
```bash
systemctl --user restart wiki-openwebui.service
curl http://127.0.0.1:8080
```

### Problem: Files not auto-processing
```bash
# Check daemon:
systemctl --user status wiki-monitor.service

# Manual force:
wiki ingest ~/Downloads/file.pdf
```

---

## ✅ SUMMARY

**Your Questions Answered:**

1. ✅ **Boot services**: 11 total, keep 4 core ones (guide above)
2. ✅ **Main UI**: NO single hub — use Terminal/Web UI/Desktop widgets (your choice!)
3. ✅ **File saving**: Drop in `~/Downloads/` or `~/wiki/user/*` (auto-processes)
4. ✅ **Markdown conversion**: Automatic for most files (PDF, TXT, HTML)
5. ✅ **Then what**: Auto-process → wiki page → git commit → searchable
6. ✅ **Interactive wallpaper**: Already running! (wiki-wallpaper-gen)
7. ✅ **Todo improvements**: Use `wiki task` or Obsidian Tasks plugin
8. ✅ **Interactive reports**: Create HTML dashboard or use Obsidian Dataview

**Files Created:**
- This guide: `~/Desktop/WIKI-LINUX-SETUP-AND-WORKFLOW-GUIDE.md`
- Auto-setup script: (run it below)

---

**Next Steps:**
1. Run auto-setup script (below)
2. Choose your primary UI (Terminal/Web UI/Desktop)
3. Drop a test file in ~/Downloads/ to verify workflow
4. Customize as needed!
