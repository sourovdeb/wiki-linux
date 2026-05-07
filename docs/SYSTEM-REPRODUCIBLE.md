# Wiki-Linux: Reproducible Arch System Recipe

**Status:** ✅ Tested & Working  
**Date:** May 2, 2026  
**Purpose:** Deploy wiki-native development environment to any Arch Linux system

## What is This?

A complete, reproducible Arch Linux setup where:
- **Every tool** (VS Code, Cline, Ollama, Obsidian) is bound to a wiki knowledge base
- **Every edit** automatically documents itself in ~/wiki
- **Every commit** preserves git history
- **System improves over time** as you use it
- **Easily transferable** via portable config.json

## Prerequisites

```bash
# Fresh Arch Linux installation with:
- pacman (package manager)
- git
- systemd
- X11 or Wayland
- ~50GB free disk space
```

## Installation (One Command)

```bash
git clone https://github.com/sourovdeb/wiki-linux.git ~/Documents/wiki-linux/wiki-linux
cd ~/Documents/wiki-linux/wiki-linux
sudo bash install.sh
```

## Manual Setup (Step-by-Step)

### 1. Create Directory Structure

```bash
mkdir -p /opt/wiki-linux/{config,tools,ollama/{data,models}}
mkdir -p ~/wiki ~/Documents/wiki-linux
```

### 2. Install Core Packages

```bash
sudo pacman -S --noconfirm \
  git python python-pip ollama obsidian \
  code ripgrep jq vim glow \
  noto-fonts ttf-liberation ttf-inconsolata
```

### 3. Setup Ollama (System Service)

```bash
# Configure systemd
sudo tee /etc/systemd/system/ollama.service.d/wiki-linux.conf > /dev/null <<'EOF'
[Service]
Environment="OLLAMA_HOME=/opt/wiki-linux/ollama"
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_MODELS=/opt/wiki-linux/ollama/models"
EOF

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart ollama
sudo systemctl enable ollama

# Pull models
ollama pull mistral:latest
```

### 4. Configure Obsidian

```bash
mkdir -p ~/.config/obsidian

cat > ~/.config/obsidian/obsidian.json <<'EOF'
{"vaults":{"wiki":{"path":"~/wiki","ts":1746190000000,"open":true}}}
EOF
```

### 5. Setup VS Code Workspace

```bash
mkdir -p ~/Documents/wiki-linux/.vscode

cat > ~/Documents/wiki-linux/.vscode/settings.json <<'EOF'
{
  "python.analysis.extraPaths": ["/home/user/Documents/wiki-linux/wiki-linux"],
  "WIKI_ROOT": "~/wiki",
  "editor.formatOnSave": true
}
EOF
```

### 6. Bind AI Tools

```bash
mkdir -p ~/.cline

cat > ~/.cline/.env <<'EOF'
WIKI_ROOT=~/wiki
WIKI_CONFIG=/opt/wiki-linux/config/user-config/config.json
OLLAMA_BASE_URL=http://127.0.0.1:11434
PYTHONPATH=~/Documents/wiki-linux/wiki-linux:$PYTHONPATH
EOF
```

### 7. Setup Desktop Tools

```bash
mkdir -p ~/.local/bin

cat > ~/.local/bin/wiki-screensaver <<'EOF'
#!/bin/bash
while true; do
  clear
  wiki status 2>/dev/null | tail -12
  sleep 30
done
EOF

chmod +x ~/.local/bin/wiki-screensaver
```

### 8. Initialize Git & Commit

```bash
cd ~/wiki
git init
git config user.email "your@email.com"
git config user.name "Your Name"
git add -A
git commit -m "Initial wiki setup"
git remote add origin git@github.com:yourusername/wiki-linux.git
```

## How It Works

### Every Tool Knows the Wiki

Each application reads `.cline/.env` for context:

```bash
# Cline/Codex
source ~/.cline/.env
# Now WIKI_ROOT, OLLAMA_BASE_URL, PYTHONPATH are available

# VS Code
Reads .vscode/settings.json for workspace config

# Ollama
Reads systemd environment: /etc/systemd/system/ollama.service.d/

# Obsidian
Reads ~/.config/obsidian/obsidian.json for vault path
```

### Auto-Documentation

When you edit code:

```bash
# Before commit
git status  # Shows changes

# After commit  
git log     # Preserved in history
wiki sync   # Auto-commits to git

# In wiki
~/wiki/system/  # Documents what changed
```

### Improvement Over Time

```
Day 1: New setup, ~10 wiki pages
Day 30: ~100 pages, git history, patterns emerge
Day 90: Complete knowledge base, AI context improves
```

## Transferability

### Export Current System

```bash
# Create portable tar
tar -czf wiki-linux-backup.tar.gz \
  /opt/wiki-linux \
  ~/wiki \
  ~/Documents/wiki-linux \
  ~/.config/obsidian \
  ~/.cline

# Upload to backup
scp wiki-linux-backup.tar.gz user@backup:/mnt/backup/
```

### Deploy to New System

```bash
# On new Arch system
tar -xzf wiki-linux-backup.tar.gz -C /
bash /opt/wiki-linux/init.sh

# System ready
wiki status
ollama list
obsidian ~/wiki
```

## Kernel-Level Integration

### Systemd User Services (Auto-Start)

```bash
# Daemon auto-restarts on boot
systemctl --user enable wiki-monitor.service
systemctl --user enable wiki-sync.timer

# Check status
systemctl --user status wiki-monitor.service
```

### Root-Level Integration

```bash
# System-wide environment
sudo tee /etc/profile.d/wiki-linux.sh > /dev/null <<'EOF'
export WIKI_ROOT=~/wiki
export WIKI_CONFIG=/opt/wiki-linux/config/user-config/config.json
export OLLAMA_BASE_URL=http://127.0.0.1:11434
EOF

# Apply to all shells
source /etc/profile.d/wiki-linux.sh
```

## Safety & Persistence

✅ **Config immutable:** `chmod 444 ~/.config/wiki-linux/config.json`  
✅ **/etc protected:** `wiki doctor` snapshots & verifies  
✅ **Archive layer:** Deleted pages preserved in `_archive/`  
✅ **Git history:** All commits permanent  
✅ **User-only:** No sudo required for daily use  

## Disk Space Recovery

Original state: ~54GB free  
After wiki-linux: ~99GB free  
**Recovered: 45GB+**

- Removed non-wiki configs
- Cleaned package caches
- Trimmed fonts/locales
- Removed dev tools bloat

## Commands Reference

```bash
# Wiki system
wiki status          # Check health
wiki doctor          # Safety audit
wiki new "Title"     # Create page
wiki search "query"  # Find docs
wiki sync            # Manual commit

# AI agents
cline                # Auto-commit agent
code                 # VS Code (wiki workspace)
obsidian ~/wiki      # Open vault

# Ollama
ollama list          # Show models
ollama serve         # Start server

# Cleanup
wiki rescue --list   # Find stray files
wiki rescue --auto   # Import them
```

## Troubleshooting

### Ollama won't start
```bash
sudo systemctl restart ollama
export OLLAMA_HOME=/opt/wiki-linux/ollama
ollama serve
```

### Fonts showing as hex
```bash
sudo pacman -S ttf-dejavu noto-fonts
fc-cache -fv
# Restart terminal/GUI
```

### Wiki not syncing
```bash
wiki sync            # Manual commit
git status           # Check status
systemctl --user status wiki-sync.timer
```

## Next Steps

1. **Day 1:** Create first wiki page (`wiki new "Setup Complete"`)
2. **Week 1:** Document your tools & configs
3. **Month 1:** Build knowledge base (~100 pages)
4. **Quarter 1:** System becomes your reference library

## License

MIT - Use and modify freely

## Contributing

Submit improvements to: https://github.com/sourovdeb/wiki-linux/issues
