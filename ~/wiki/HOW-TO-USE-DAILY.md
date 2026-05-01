# 📖 Daily Use Guide for Wiki-Linux System

## 🌅 Morning Routine

### 1. Start Your Day
```bash
# Start the wiki daemon (if not running)
systemctl --user start wiki-monitor

# Check system status
wiki status
```

### 2. Quick Search
- **Keyboard Shortcut**: Press `Super+Space` to open the search dialog
- **Options Available**:
  - **Ask LLM**: Ask questions about your wiki content
  - **Search**: Find specific pages or keywords
  - **New Note**: Create a new note quickly
  - **Status**: Check system health

## 📝 Taking Notes Throughout the Day

### Method 1: Quick Terminal Notes
```bash
# Create a new note from terminal
wiki new "Meeting notes about project X"

# This opens your editor with a pre-formatted template
```

### Method 2: Toleria GUI
1. Launch Toleria from your applications menu
2. Navigate to `~/wiki/user/notes/`
3. Create new files or edit existing ones
4. Use the graph view to see connections between notes

### Method 3: Obsidian (if installed)
```bash
# Open wiki in Obsidian
wiki open
```

## 🔍 Finding Information

### Search Your Wiki
```bash
# Search for keywords
wiki search "systemd configuration"

# Ask LLM questions
wiki ask "How do I set up a systemd timer?"
```

### Panel Status Monitor
Look at your XFCE panel for real-time status:
- `◆ mistral | 42p | ✓ wiki` - Shows Ollama model, page count, and daemon status

## 📁 File Management

### Documents & Downloads Integration
Your wiki is connected to:
- `~/Documents/` - For formal documents
- `~/Downloads/` - For temporary files

**How to link files to wiki:**
```bash
# Move important documents to wiki
mv ~/Downloads/important-file.pdf ~/wiki/user/attachments/

# Create a wiki page referencing it
wiki new "Document analysis"
```

### Automatic Backup
- When you plug in a USB drive, you'll get a popup asking to back up your wiki
- Backups are stored as `wiki-backup-YYYY-MM-DD_HHMM/` on your USB drive

## 🤖 Using Ollama LLM

### Available Models
- `mistral:latest` - General purpose
- `llama3.2:3b` - Lightweight model
- `qwen2.5-coder:3b` - Code-focused
- `nomic-embed-text:latest` - Embeddings

### Query Your Wiki with LLM
```bash
# Ask questions using your wiki as context
wiki ask "What were my notes about the networking setup?"

# The system will:
# 1. Search your wiki for relevant content
# 2. Use Ollama to generate a comprehensive answer
# 3. Show sources from your wiki
```

## 🌙 Evening Routine

### Review Changes
```bash
# See what you've worked on today
cat ~/wiki/_meta/recent.md

# Check the operation log
tail ~/wiki/_meta/log.md
```

### Sync to GitHub
```bash
# Commit and push changes
cd ~/wiki
git add .
git commit -m "Daily updates $(date +%Y-%m-%d)"
git push origin main
```

## 🚀 Advanced Features

### Full-Text Search
```bash
# Use ripgrep to search all markdown files
rg "search term" ~/wiki/

# With context
rg -A 3 -B 3 "search term" ~/wiki/
```

### Link Notes Together
```markdown
# In your markdown files, use wikilinks:
[[other-note]]  # Links to other-note.md
[[folder/subpage]]  # Links to folder/subpage.md

# Or use standard markdown links:
[description](other-note.md)
```

### Graph View
- Open Toleria and use the graph view to visualize connections
- See how your notes relate to each other
- Discover patterns in your knowledge

## 🎯 Best Practices

1. **Daily Notes**: Create a daily note in `~/wiki/user/notes/`
2. **Tagging**: Use YAML frontmatter for tags and categories
3. **Linking**: Connect related notes with wikilinks
4. **Review**: Spend 5 minutes daily reviewing `recent.md`
5. **Backup**: Let the system automatically back up to USB drives

## 🛠️ Troubleshooting

### Daemon Issues
```bash
# Check daemon status
systemctl --user status wiki-monitor

# Restart if needed
systemctl --user restart wiki-monitor
```

### Ollama Issues
```bash
# Check Ollama status
systemctl status ollama

# List available models
ollama list
```

### Git Issues
```bash
# Check git status
cd ~/wiki && git status

# Pull latest changes
git pull origin main