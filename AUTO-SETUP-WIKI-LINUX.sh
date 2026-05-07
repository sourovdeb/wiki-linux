#!/bin/bash
# AUTO-SETUP-WIKI-LINUX.sh
# Automatically configure wiki-linux optimal settings
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

set -e

echo "🚀 Wiki-Linux Auto-Setup"
echo "========================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Enable core services only (disable optional)
echo -e "${GREEN}1️⃣ Optimizing boot services...${NC}"
systemctl --user enable wiki-monitor.service 2>/dev/null || true
systemctl --user enable wiki-ollama.service 2>/dev/null || true
systemctl --user enable wiki-openwebui.service 2>/dev/null || true
systemctl --user enable wiki-sync.timer 2>/dev/null || true

# Disable optional services
echo -e "${YELLOW}   Disabling optional services...${NC}"
systemctl --user disable aeon-habits.service 2>/dev/null || true
systemctl --user disable aeon-log-translator.service 2>/dev/null || true
systemctl --user disable aeon-notification.service 2>/dev/null || true
systemctl --user disable wiki-boot-health.service 2>/dev/null || true
systemctl --user disable wiki-screensaver-watch.service 2>/dev/null || true

echo -e "${GREEN}✅ Core services enabled, optional services disabled${NC}"

# 2. Set up keyboard shortcut (XFCE)
echo ""
echo -e "${GREEN}2️⃣ Configuring keyboard shortcuts...${NC}"
if command -v xfconf-query &>/dev/null; then
    # Try to create or update the keyboard shortcut
    xfconf-query -c xfce4-keyboard-shortcuts -p '/commands/custom/<Super>space' \
        -n -t string -s 'wiki-search-dialog' 2>/dev/null || \
    xfconf-query -c xfce4-keyboard-shortcuts -p '/commands/custom/<Super>space' \
        -s 'wiki-search-dialog' 2>/dev/null || \
    echo -e "${YELLOW}⚠️ Couldn't set keyboard shortcut automatically. Set manually in XFCE Keyboard Settings.${NC}"
    
    if xfconf-query -c xfce4-keyboard-shortcuts -p '/commands/custom/<Super>space' 2>/dev/null | grep -q "wiki-search"; then
        echo -e "${GREEN}✅ Keyboard shortcut: Super+Space → wiki-search${NC}"
    else
        echo -e "${YELLOW}⚠️ Keyboard shortcut not set. Manual setup required.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ XFCE not detected, skipping keyboard shortcut${NC}"
fi

# 3. Create desktop shortcuts
echo ""
echo -e "${GREEN}3️⃣ Creating desktop shortcuts...${NC}"
mkdir -p ~/Desktop

TOOLS_DIR=~/Documents/wiki-linux/wiki-linux/WIKI-TOOLS
if [[ -d "$TOOLS_DIR" ]]; then
    cp "$TOOLS_DIR/1-SEARCH-BOX.desktop" ~/Desktop/ 2>/dev/null && chmod +x ~/Desktop/1-SEARCH-BOX.desktop || true
    cp "$TOOLS_DIR/7-CHROMIUM-AI.desktop" ~/Desktop/ 2>/dev/null && chmod +x ~/Desktop/7-CHROMIUM-AI.desktop || true
    cp "$TOOLS_DIR/9-DASHBOARD.desktop" ~/Desktop/ 2>/dev/null && chmod +x ~/Desktop/9-DASHBOARD.desktop || true
    echo -e "${GREEN}✅ Desktop shortcuts created${NC}"
else
    echo -e "${YELLOW}⚠️ WIKI-TOOLS directory not found${NC}"
fi

# 4. Verify Ollama models
echo ""
echo -e "${GREEN}4️⃣ Checking Ollama models...${NC}"
if command -v ollama &>/dev/null; then
    if ollama list 2>/dev/null | grep -E "mistral|llama3.2|qwen2.5-coder|phi3" >/dev/null; then
        MODEL_COUNT=$(ollama list 2>/dev/null | grep -E "mistral|llama3.2|qwen2.5-coder|phi3" | wc -l)
        echo -e "${GREEN}✅ Ollama models detected ($MODEL_COUNT models)${NC}"
    else
        echo -e "${YELLOW}⚠️ No common Ollama models found. Install with:${NC}"
        echo "   ollama pull mistral"
    fi
else
    echo -e "${RED}❌ Ollama command not found${NC}"
fi

# 5. Test Web UI
echo ""
echo -e "${GREEN}5️⃣ Testing Web UI...${NC}"
if curl -s --max-time 2 http://127.0.0.1:8080 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Web UI accessible: http://127.0.0.1:8080${NC}"
else
    echo -e "${YELLOW}⚠️ Web UI not responding. Check wiki-openwebui.service${NC}"
    echo "   systemctl --user status wiki-openwebui.service"
fi

# 6. Configure git auto-sync
echo ""
echo -e "${GREEN}6️⃣ Configuring git auto-sync...${NC}"
WIKI_DIR=~/Documents/wiki-linux/wiki-linux
if [[ -d "$WIKI_DIR/.git" ]]; then
    cd "$WIKI_DIR"
    if git remote -v 2>/dev/null | grep -q "origin"; then
        REMOTE_URL=$(git remote get-url origin 2>/dev/null)
        echo -e "${GREEN}✅ Git remote configured: $REMOTE_URL${NC}"
    else
        echo -e "${YELLOW}⚠️ No git remote found. Add with:${NC}"
        echo "   cd $WIKI_DIR"
        echo "   git remote add origin <your-repo-url>"
    fi
else
    echo -e "${YELLOW}⚠️ Git repository not initialized${NC}"
fi

# 7. Check Python environment
echo ""
echo -e "${GREEN}7️⃣ Checking Python environment...${NC}"
if [[ -d "$WIKI_DIR/.venv" ]]; then
    echo -e "${GREEN}✅ Python virtualenv exists${NC}"
    if [[ -f "$WIKI_DIR/.venv/bin/activate" ]]; then
        source "$WIKI_DIR/.venv/bin/activate"
        python --version 2>/dev/null
        deactivate
    fi
else
    echo -e "${YELLOW}⚠️ Python virtualenv not found${NC}"
fi

# 8. Start/restart services
echo ""
echo -e "${GREEN}8️⃣ Starting core services...${NC}"
systemctl --user restart wiki-monitor.service 2>/dev/null || echo -e "${YELLOW}⚠️ Couldn't restart wiki-monitor${NC}"
systemctl --user restart wiki-ollama.service 2>/dev/null || echo -e "${YELLOW}⚠️ Couldn't restart wiki-ollama${NC}"
systemctl --user restart wiki-openwebui.service 2>/dev/null || echo -e "${YELLOW}⚠️ Couldn't restart wiki-openwebui${NC}"
systemctl --user restart wiki-sync.timer 2>/dev/null || echo -e "${YELLOW}⚠️ Couldn't restart wiki-sync.timer${NC}"

sleep 2

# 9. Verify services are running
echo ""
echo -e "${GREEN}9️⃣ Verifying services...${NC}"
WIKI_SERVICES=(wiki-monitor.service wiki-ollama.service wiki-openwebui.service)
for svc in "${WIKI_SERVICES[@]}"; do
    if systemctl --user is-active "$svc" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $svc is active${NC}"
    else
        echo -e "${RED}❌ $svc is not active${NC}"
    fi
done

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Auto-setup complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 Next Manual Steps:${NC}"
echo "   1. Configure git remote (if not done)"
echo "   2. Test keyboard shortcut: Press Super+Space"
echo "   3. Open Web UI: http://127.0.0.1:8080"
echo "   4. Review services: systemctl --user status wiki-*"
echo "   5. Read guide: ~/Desktop/WIKI-LINUX-SETUP-AND-WORKFLOW-GUIDE.md"
echo ""
echo -e "${GREEN}🎯 Your system is ready to use!${NC}"
echo ""
