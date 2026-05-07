# Wiki-Linux System Integration Guide

Complete setup and usage guide for the integrated wiki-linux ecosystem: Firefox extension, Chromium extension, wiki_ingestor, OpenWebUI diagnostics, and Ollama.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Wiki-Linux Ecosystem                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   Firefox           │      │  Chromium            │        │
│  │   Extension         │      │  Extension           │        │
│  │ ─────────────────── │      │ ─────────────────── │        │
│  │ • Sidebar Panel     │      │ • Side Panel         │        │
│  │ • Status Popup      │      │ • Chat Interface     │        │
│  │ • Wiki Convert      │      │ • Page Analysis      │        │
│  └──────┬───────────────┘      └──────┬──────────────┘        │
│         │                             │                        │
│         ├─────────────┬───────────────┤                        │
│         │             │               │                        │
│    HTML to Markdown   │        Local Ollama Analysis            │
│    (YAML Frontmatter) │                                        │
│         │             │                                        │
│         └─────────┬───┴────────┬──────────────────┐            │
│                   │            │                  │            │
│         ┌─────────▼──────────┐ │   ┌──────────┐  │            │
│         │ ~/wiki/converted/  │ │   │ Ollama   │  │            │
│         │ (Watch Folder)     │─┼──▶│ 11434    │  │            │
│         └────────────────────┘ │   └──────────┘  │            │
│                                │                  │            │
│    ┌────────────────────────────▼─────────────┐  │            │
│    │   wiki_ingestor                          │  │            │
│    │ ─────────────────────────────────────── │  │            │
│    │ • Auto-detect markdown in watch folders │  │            │
│    │ • Parse YAML frontmatter               │  │            │
│    │ • Convert to wiki structure            │  │            │
│    │ • Store in ~/wiki/content/             │  │            │
│    └────────────────────────────────────────┘  │            │
│                      │                          │            │
│            ┌─────────▼──────────┐               │            │
│            │ ~/wiki/content/    │               │            │
│            │ (Final Wiki Store) │               │            │
│            └────────────────────┘               │            │
│                                                 │            │
│                      ┌──────────────────────────┘            │
│                      │                                        │
│         ┌────────────▼─────────────┐                         │
│         │  Open WebUI              │                         │
│         │ ─────────────────────── │                         │
│         │ • Service: 8080          │                         │
│         │ • Diagnostics: 14-17    │                         │
│         │ • Unified Profile        │                         │
│         └──────────────────────────┘                         │
│                                                 │            │
│         ┌──────────────────────────────────────┘            │
│         │                                                    │
│         └──▶ [System Health & Status]                       │
│             • Port monitoring                               │
│             • Process health checks                         │
│             • Database integrity                           │
│                                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start (5 Minutes)

### 1. Start Services
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Open WebUI (optional)
open-webui serve
```

### 2. Install Extensions
```bash
# Firefox: Manual load
# - Go to about:debugging
# - Click "Load Temporary Add-on"
# - Select extensions/wiki-linux-firefox/manifest.json

# Chromium: Manual load
# - Go to chrome://extensions
# - Enable Developer mode
# - Click "Load unpacked"
# - Select extensions/ollama-local-assistant
```

### 3. Start wiki_ingestor Watcher
```bash
cd /path/to/wiki-linux
python -m wiki_ingestor watch
```

### 4. Use Extensions
- Open any webpage
- Firefox: Click extension → Use sidebar panel
- Chromium: Click extension → View side panel
- Save webpages: "💾 Save to Wiki"
- Check status: Click popup to see Ollama/OpenWebUI status

---

## Component Details

### Firefox Extension

**Purpose**: Full-featured assistant with wiki_ingestor integration

**Location**: `extensions/wiki-linux-firefox/`

**Key Features**:
- Sidebar panel with chat-like interface
- System status popup showing Ollama/OpenWebUI/wiki_ingestor status
- Page summarization using local Ollama
- Search within page content
- Link crawling and PDF detection
- HTML to Markdown conversion with YAML frontmatter
- Direct wiki_ingestor integration

**Installation**:
```bash
# Temporary (Development)
about:debugging → Load Temporary Add-on → manifest.json

# Permanent
# Package: bash WIKI-TOOLS/handoff/16-package-ollama-extension.sh
# Result: _meta/reports/extension-build/wiki-linux-firefox-*.zip
# Install: Drag to Firefox
```

**Usage**:
1. Click extension icon → Sidebar opens
2. Select model from dropdown
3. Use action buttons (Summarize, Search, etc.)
4. Click "💾 Save to Wiki" to archive page

### Chromium Extension

**Purpose**: Alternative extension for Chromium-based browsers

**Location**: `extensions/ollama-local-assistant/`

**Key Features**:
- Side panel (Chrome 114+)
- Page snapshot and content extraction
- Form detection
- PDF link finder
- Direct Ollama queries

**Installation**:
```bash
# Developer mode
chrome://extensions → Developer mode ON → Load unpacked
→ Select extensions/ollama-local-assistant
```

### wiki_ingestor Package

**Purpose**: Automated webpage archiving and wiki structure generation

**Location**: `wiki_ingestor/`

**Key Features**:
- OS-specific config detection
- Watch folder monitoring
- HTML to Markdown conversion
- YAML frontmatter generation
- Multi-folder support

**Installation**:
```bash
cd wiki_ingestor
bash install_linux.sh              # Linux
# or
install_windows.bat                # Windows
```

**Configuration**:
```bash
# Interactive setup
python -m wiki_ingestor init

# Run watcher
python -m wiki_ingestor watch

# Manual batch processing
python -m wiki_ingestor batch
```

### OpenWebUI Diagnostic & Repair Tools

**Purpose**: Fix and monitor Open WebUI setup

**Location**: `WIKI-TOOLS/handoff/`

**Scripts**:
- `14-openwebui-single-profile-repair.sh` — Unify profiles
- `15-wiki-linux-diagnostic.sh` — Generate status report
- `16-package-ollama-extension.sh` — Build extension packages
- `17-diagnostic-and-openwebui-fix.sh` — Full workflow

**Usage**:
```bash
# Full diagnostic and repair
./WIKI-TOOLS/handoff/17-diagnostic-and-openwebui-fix.sh

# Just diagnostic
./WIKI-TOOLS/handoff/15-wiki-linux-diagnostic.sh

# Just repair
./WIKI-TOOLS/handoff/14-openwebui-single-profile-repair.sh
```

---

## Complete Workflow

### Capture & Archive a Webpage

**Scenario**: You find an important article and want to archive it with metadata

```
Step 1: Browser
├─ Navigate to webpage
├─ Read content
└─ Decide to archive

Step 2: Firefox Extension
├─ Click extension icon
├─ Review page in sidebar
├─ Click "📝 Summarize" to generate summary
└─ Click "💾 Save to Wiki"
    ├─ Page converted to Markdown
    ├─ YAML frontmatter added
    │   ├─ title, url, date
    │   └─ source: "firefox-extension"
    └─ Ready to save

Step 3: Save File
├─ File format: page-title-TIMESTAMP.md
├─ YAML example:
│  ---
│  title: "Article: How to Learn Rust"
│  url: "https://example.com/rust-tutorial"
│  date: "2026-05-07T18:45:23Z"
│  source: "firefox-extension"
│  tags: [web-capture, ollama]
│  ---
│  # Article Content...
└─ Save to: ~/wiki/converted/ (or your watch folder)

Step 4: wiki_ingestor Processing
├─ Watcher detects new file
├─ Parses YAML frontmatter
├─ Applies any configured transformations
└─ Stores in: ~/wiki/content/

Step 5: Wiki Integration
└─ Page now available in your wiki system
   ├─ Queryable by title, URL, tags
   ├─ Full search available
   └─ Part of permanent archive
```

### Search & Retrieve Information

```
Step 1: Firefox Extension
├─ Navigate to webpage
├─ Click extension → Sidebar
└─ Click "🔍 Search"
    ├─ Enter search query
    ├─ Ollama analyzes page content
    └─ Displays relevant excerpts

Step 2: Information Found
└─ Copy results for use
```

### Automated Form Filling

```
Step 1: Firefox Extension
├─ Navigate to webpage with form
├─ Click extension → Sidebar
└─ Click "📋 Forms"
    ├─ Extension lists form fields
    └─ Shows field types

Step 2: Manual Form Interaction
├─ Forms detected and catalogued
├─ Can be filled manually
└─ Data can be saved with page
```

### System Health Monitoring

```
Step 1: Firefox Popup
├─ Click extension icon (popup, not sidebar)
└─ View Status Cards:
    ├─ 🤖 Ollama: 🟢 Online (127.0.0.1:11434)
    ├─ 🌐 OpenWebUI: 🟢 Online (127.0.0.1:8080)
    └─ 📚 wiki_ingestor: ✓ Installed

Step 2: Quick Actions
├─ 📖 Open Sidebar
├─ 🤖 Open Ollama
└─ 🌐 Open WebUI

Step 3: Available Models
└─ Lists all Ollama models installed
   ├─ llama3.2:3b
   └─ qwen2.5-coder:3b
```

---

## Configuration Files

### wiki_ingestor Configuration
Path: `~/.config/wiki-linux/config.json`

```json
{
  "wiki": {
    "root": "~/wiki",
    "monitor": {
      "watch_dirs": [
        "~/wiki/converted",
        "~/wiki/inbox",
        "~/Downloads"
      ]
    }
  }
}
```

### Open WebUI Configuration
Path: `~/.local/share/wiki-linux/openwebui-data/` or `~/.config/open-webui/data/`

After repair script runs:
- Single unified profile
- Service-only mode (no desktop app fallback)
- All data in canonical location

### Ollama Configuration
Path: `~/.ollama/`

Models stored in: `~/.ollama/models/manifests/`

Start service:
```bash
ollama serve
# or
systemctl --user start wiki-ollama.service
```

---

## Troubleshooting Integration

### Issue: Extensions can't reach Ollama

**Diagnosis**:
```bash
# Check Ollama is running
curl http://127.0.0.1:11434/api/tags

# Check port is open
netstat -tulpn | grep 11434
```

**Solution**:
```bash
# Start Ollama if not running
ollama serve

# Or via systemd
systemctl --user start wiki-ollama.service
```

### Issue: wiki_ingestor not processing files

**Diagnosis**:
```bash
# Check watcher is running
python -m wiki_ingestor status

# Check watch folders exist
ls ~/wiki/converted/
```

**Solution**:
```bash
# Restart watcher
python -m wiki_ingestor watch

# Or do manual batch
python -m wiki_ingestor batch
```

### Issue: Open WebUI keeps resetting

**Diagnosis**:
```bash
# Run diagnostic
./WIKI-TOOLS/handoff/15-wiki-linux-diagnostic.sh

# Check for extra processes
ps aux | grep -i openwebui | grep -v grep
```

**Solution**:
```bash
# Run repair
./WIKI-TOOLS/handoff/14-openwebui-single-profile-repair.sh

# Verify
./WIKI-TOOLS/handoff/15-wiki-linux-diagnostic.sh
```

### Issue: Firefox extension sidebar won't open

**Solution**:
```bash
# Check Firefox version supports MV3 (109+)
# Go to about:
# Look for Application Update → Firefox version

# Reload extension
about:debugging → Find Wiki-Linux Assistant → Reload

# Try manual panel
Ctrl+B (Toggle sidebar)
```

---

## Performance Optimization

### For Fast Operations
- Use `llama3.2:3b` (3B parameters, very fast)
- Suitable for: summarization, search, crawling
- Typical response time: 2-5 seconds

### For Accurate/Complex Operations
- Use `qwen2.5-coder:3b` (code-optimized)
- Better for: technical content, code analysis
- Typical response time: 3-8 seconds

### System Resources
- Ollama: ~4GB RAM minimum per model
- Sidebar panel: ~50MB memory
- wiki_ingestor watcher: ~30MB memory
- Firefox/Chromium: Standard browser memory

### Monitoring
```bash
# Check Ollama process
ollama ps

# Monitor system load during operations
watch -n 1 'ps aux | grep ollama'
```

---

## Security Considerations

✅ **What's Private**:
- All Ollama models run locally
- No data sent to external servers
- All processing on your machine
- Extensions don't phone home

⚠️ **Permissions**:
- Extensions need access to all URLs for page analysis
- No browsing data is logged
- Forms data only used for filling (not stored)
- PDFs linked but not downloaded without user action

🔐 **Best Practices**:
- Keep Ollama service restricted to localhost (default)
- Don't expose port 11434 to network
- Run wiki_ingestor watch in trusted folder
- Regularly review archived content

---

## Advanced Usage

### Custom Ollama Models

```bash
# Add new model
ollama pull [model-name]

# See available models
ollama list

# Use in extension (update sidebar.js model dropdown)
```

### Multi-Directory Monitoring

Configure multiple watch folders in wiki_ingestor:

```bash
python -m wiki_ingestor init
# Select multiple folders when prompted
```

### Batch Processing Large Archives

```bash
# Process entire folder
cd ~/wiki/converted/
python -m wiki_ingestor batch

# Or with custom folder
python -m wiki_ingestor batch --folder ~/Downloads/web-captures/
```

### Export Archives

```bash
# Entire wiki
cp -r ~/wiki/content/ ~/wiki/backup-$(date +%Y%m%d)

# Or use git
cd ~/wiki
git init
git add content/
git commit -m "Wiki archive backup"
```

---

## Version Information

| Component | Version | Status |
|-----------|---------|--------|
| Firefox Extension | 1.0.0 | ✓ Active |
| Chromium Extension | 1.0.0 | ✓ Active |
| wiki_ingestor | 1.0.0 | ✓ Installed |
| OpenWebUI | Any | ✓ Optional |
| Ollama | Any | ✓ Required |
| Firefox | 109+ | ✓ Supported |
| Chrome/Edge | 114+ | ✓ Supported |

---

## Support & Contributing

- **Issues**: Report on GitHub
- **Features**: Submit pull requests
- **Questions**: Check README files in each component
- **Updates**: Pull latest from github.com/sourovdeb/wiki-linux

---

**Created**: May 2026  
**Last Updated**: May 7, 2026  
**Maintained**: wiki-linux project team
