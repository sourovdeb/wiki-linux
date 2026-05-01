 re# 🔗 System Integration Guide

## 🎯 How This System is Useful for You

This wiki-linux system transforms your computer into a **personal knowledge management powerhouse** with these key benefits:

### 1. **Centralized Knowledge Base**
- All your notes, documents, and research in one searchable location
- Version-controlled with Git for safety and history
- Accessible from anywhere via GitHub synchronization

### 2. **AI-Powered Search & Answers**
- Ollama LLM integration provides intelligent answers using your own content
- No more forgetting where you stored information
- Get context-aware responses based on your personal knowledge

### 3. **Seamless Workflow Integration**
- Keyboard shortcuts for instant access
- Panel status monitor for system health
- Automatic backups to USB drives
- Toleria GUI for visual knowledge mapping

### 4. **Future-Proof Organization**
- Markdown-based notes (industry standard)
- Git version control (never lose work)
- Open source tools (no vendor lock-in)
- Extensible architecture (add more features as needed)

## 📂 Folder Integration Strategy

### Current Structure
```
~/ (your home folder)
├── wiki/                          ← NEW — your wiki vault (PRIMARY)
│   ├── user/notes/                ← Daily notes, ideas, research
│   ├── user/projects/             ← Project documentation
│   ├── user/attachments/          ← Important files (PDFs, images, etc.)
│   ├── system/                    ← System configuration mirrors
│   └── _meta/                      ← Auto-generated indices
│
├── Documents/                     ← Secondary document storage
├── Downloads/                     ← Temporary files
└── ... (other folders unchanged)
```

### Integration Approach

#### Option 1: Symlinks (Recommended)
```bash
# Create symlinks in your wiki to access Documents/Downloads
ln -s ~/Documents ~/wiki/user/documents
ln -s ~/Downloads ~/wiki/user/downloads

# Now you can access these folders through your wiki
ls ~/wiki/user/documents/  # Shows your Documents folder
ls ~/wiki/user/downloads/  # Shows your Downloads folder
```

#### Option 2: Selective Import
```bash
# Move important documents to wiki permanently
mv ~/Documents/important-project.pdf ~/wiki/user/attachments/
mv ~/Downloads/research-paper.pdf ~/wiki/user/attachments/

# Create wiki pages referencing these files
wiki new "Project Documentation Analysis"
wiki new "Research Paper Summary"
```

#### Option 3: Automated Sync (Advanced)
```bash
# Create a script to sync important files daily
cat > ~/bin/sync-documents-to-wiki << 'EOF'
#!/bin/bash
rsync -av --update ~/Documents/ ~/wiki/user/documents/
rsync -av --update ~/Downloads/ ~/wiki/user/downloads/
EOF

chmod +x ~/bin/sync-documents-to-wiki

# Add to cron for daily sync
(crontab -l 2>/dev/null; echo "0 12 * * * ~/bin/sync-documents-to-wiki") | crontab -
```

## 🎯 Daily Use Methods

### 1. **Quick Capture (30 seconds)**
```bash
# Press Super+Space → "New Note" → Type title → Done!
# Or from terminal:
wiki new "Quick idea about project X"
```

### 2. **Deep Research (5-30 minutes)**
```bash
# Open Toleria for visual mapping
tolaria

# Use graph view to see connections
# Create multiple linked notes
# Use wikilinks: [[related-topic]]
```

### 3. **Information Retrieval (Instant)**
```bash
# Press Super+Space → "Ask LLM" → Type question
# Or from terminal:
wiki ask "What were my thoughts on systemd timers?"

# The system will:
# 1. Search your entire wiki
# 2. Use Ollama to generate a comprehensive answer
# 3. Show sources from your notes
```

### 4. **System Monitoring (Glance)**
- Look at XFCE panel: `◆ mistral | 42p | ✓ wiki`
- `◆ mistral` = Current Ollama model
- `42p` = Number of pages in your wiki
- `✓ wiki` = Daemon status

### 5. **Evening Review (5 minutes)**
```bash
# Review what you've done today
cat ~/wiki/_meta/recent.md

# Commit changes to GitHub
cd ~/wiki && git add . && git commit -m "Daily update" && git push
```

## 🤖 Ollama LLM Integration

### Current Models Available
```bash
ollama list
# mistral:latest       (general purpose)
# llama3.2:3b          (lightweight)
# qwen2.5-coder:3b     (code-focused)
# nomic-embed-text:latest (embeddings)
```

### How to Use LLM with Your Wiki
```bash
# Ask questions using your wiki as context
wiki ask "How do I configure systemd services?"

# The system does:
# 1. Search ~/wiki/ for relevant content
# 2. Use Ollama to generate intelligent answers
# 3. Provide sources from your notes
# 4. Show results in a readable terminal window
```

### Switch Models
```bash
# List available models
ollama list

# Pull new models
ollama pull llama3.2

# Remove unused models
ollama rm qwen2.5-coder:3b
```

## 🌐 Toleria Configuration

### Launch Toleria
```bash
# From terminal
tolaria

# Or from applications menu
# (Look for "Toleria" in your app launcher)
```

### Configure Toleria for Wiki
1. **Open Workspace**: Select `~/wiki/` as your vault
2. **Enable Graph View**: Visualize note connections
3. **Set Default Location**: `~/wiki/user/notes/` for new notes
4. **Configure Hotkeys**: Set up your preferred keyboard shortcuts

### Toleria Features to Use
- **Graph View**: See how notes connect
- **Backlinks**: Find notes linking to current page
- **Search**: Full-text search across all notes
- **Templates**: Use for consistent note structure

## 🔍 Desktop Search Box Setup

### Current Setup
- **Shortcut**: `Super+Space` (already configured)
- **Command**: `/home/sourov/Documents/wiki-linux/wiki-linux/bin/wiki-search-dialog`

### How to Use
1. Press `Super+Space`
2. Choose from 4 options:
   - **Ask LLM**: Intelligent answers from your wiki
   - **Search**: Keyword search across all pages
   - **New Note**: Quick note creation
   - **Status**: System health check

### Customize the Search Box
```bash
# Edit the search dialog script
nano ~/Documents/wiki-linux/wiki-linux/bin/wiki-search-dialog

# You can modify:
# - Default search options
# - Window size and position
# - Terminal geometry
# - Default editor (currently nvim)
```

## 🎯 Karpathy-Style Wiki Usage

### 1. **Capture Everything**
```bash
# Quick notes throughout the day
wiki new "Meeting with team about project timeline"
wiki new "Interesting article about Rust performance"
wiki new "Idea for weekend project"
```

### 2. **Link Notes Together**
```markdown
# In your notes, create connections:
- [[project-timeline]] - Related to main project
- [[rust-performance]] - Technical details
- [[weekend-ideas]] - Personal projects

# This creates a web of knowledge
```

### 3. **Review and Refine**
```bash
# Daily review
cat ~/wiki/_meta/recent.md

# Weekly review
rg "TODO|FIXME|IDEA" ~/wiki/  # Find action items
```

### 4. **Ask Your Wiki Questions**
```bash
# Use LLM to find patterns
wiki ask "What were my main projects last month?"
wiki ask "Summarize my research on Rust performance"
wiki ask "What ideas did I have for weekend projects?"
```

## 🛠️ System Maintenance

### Update All Components
```bash
# Update wiki-linux system
cd ~/Documents/wiki-linux/wiki-linux
git pull origin main
./install.sh

# Update Ollama models
ollama pull mistral:latest

# Update Toleria
# Download latest AppImage and replace ~/.local/bin/tolaria
```

### Monitor System Health
```bash
# Check all services
systemctl status ollama
systemctl --user status wiki-monitor

# Check disk usage
df -h ~/wiki
du -sh ~/wiki
```

### Backup Strategy
1. **Automatic USB Backup**: Plug in USB → Get popup → Backup
2. **GitHub Sync**: Daily `git push` to remote repository
3. **Manual Backup**:
```bash
tar -czvf wiki-backup-$(date +%Y-%m-%d).tar.gz ~/wiki
```

## ✅ Complete Setup Checklist

### ✅ Already Configured
- [x] Ollama LLM with multiple models
- [x] Wiki daemon with file monitoring
- [x] XFCE panel status monitor
- [x] Super+Space keyboard shortcut
- [x] HDD backup popup (udev rules)
- [x] Toleria AppImage installed
- [x] Comprehensive documentation

### 🔄 Ready for You to Configure
- [ ] GitHub repository setup (`wiki-arch` branch)
- [ ] SSH keys for GitHub authentication
- [ ] Documents/Downloads folder integration
- [ ] Daily workflow habits

### 🎯 Recommended Next Steps

1. **Set up GitHub** (follow GITHUB-SETUP.md)
2. **Create first daily note**:
```bash
wiki new "My first wiki note"
```
3. **Test the search box** (Super+Space)
4. **Launch Toleria** and explore the graph view
5. **Ask your wiki a question**:
```bash
wiki ask "What is this wiki system for?"
```

Your personal knowledge management system is now ready! The more you use it, the more valuable it becomes as your personal AI assistant grows with your knowledge.