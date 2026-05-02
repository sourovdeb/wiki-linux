#!/bin/bash
# Wiki-Linux: Reproducible System Installer
# Usage: sudo bash install-reproducible.sh
# Creates a complete wiki-native development environment on Arch Linux

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use: sudo bash $0)"
   exit 1
fi

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║             Wiki-Linux: Reproducible Arch System Setup                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"

# PHASE 1: Core packages
echo ""
echo "PHASE 1: Installing core packages..."
pacman -S --noconfirm --needed \
  git python python-pip base-devel \
  ollama obsidian code \
  ripgrep jq vim glow \
  noto-fonts ttf-liberation ttf-inconsolata ttf-dejavu \
  adobe-source-code-pro-fonts \
  2>&1 | tail -5

# PHASE 2: Directory structure
echo ""
echo "PHASE 2: Creating system directories..."
mkdir -p /opt/wiki-linux/{config,tools,ollama/{data,models}}
mkdir -p /etc/systemd/system/ollama.service.d
chown -R 1000:1000 /opt/wiki-linux

# PHASE 3: Ollama system service
echo ""
echo "PHASE 3: Configuring Ollama..."
tee /etc/systemd/system/ollama.service.d/wiki-linux.conf > /dev/null <<'EOF'
[Service]
Environment="OLLAMA_HOME=/opt/wiki-linux/ollama"
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_MODELS=/opt/wiki-linux/ollama/models"
Environment="OLLAMA_NUM_PARALLEL=1"
EOF

systemctl daemon-reload
systemctl restart ollama
systemctl enable ollama
echo "✓ Ollama configured and enabled"

# PHASE 4: System-wide environment
echo ""
echo "PHASE 4: Setting up global environment..."
tee /etc/profile.d/wiki-linux.sh > /dev/null <<'EOF'
export WIKI_ROOT="${WIKI_ROOT:-$HOME/wiki}"
export WIKI_CONFIG="${WIKI_CONFIG:-$HOME/.config/wiki-linux/config.json}"
export OLLAMA_BASE_URL="http://127.0.0.1:11434"
export PYTHONPATH="${PYTHONPATH:-}$HOME/Documents/wiki-linux/wiki-linux:$PYTHONPATH"
EOF

chmod 644 /etc/profile.d/wiki-linux.sh
echo "✓ Global environment configured"

# PHASE 5: Font configuration
echo ""
echo "PHASE 5: Configuring fonts..."
fc-cache -fv 2>&1 | tail -2
echo "✓ Font cache rebuilt"

# PHASE 6: Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ INSTALLATION COMPLETE                               ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "NEXT STEPS (as regular user):"
echo ""
echo "1. Configure Obsidian:"
echo "   mkdir -p ~/.config/obsidian"
echo "   echo '{\"vaults\":{\"wiki\":{\"path\":\"~/wiki\"}}}' > ~/.config/obsidian/obsidian.json"
echo ""
echo "2. Setup Cline/AI environment:"
echo "   mkdir -p ~/.cline"
echo "   source /etc/profile.d/wiki-linux.sh"
echo ""
echo "3. Create VS Code workspace:"
echo "   mkdir -p ~/Documents/wiki-linux/.vscode"
echo "   # See SYSTEM-REPRODUCIBLE.md for example"
echo ""
echo "4. Initialize wiki:"
echo "   mkdir -p ~/wiki"
echo "   cd ~/wiki && git init"
echo "   git config user.email 'your@email.com'"
echo "   git config user.name 'Your Name'"
echo ""
echo "5. Start using:"
echo "   ollama pull mistral:latest"
echo "   obsidian ~/wiki"
echo "   code ~/Documents/wiki-linux/wiki-linux"
echo ""
echo "Full documentation: ~/wiki/SYSTEM-REPRODUCIBLE.md"
