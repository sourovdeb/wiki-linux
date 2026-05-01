#!/bin/bash
# 05-ai-browsers.sh
# Configure browsers with AI sidebars and Ollama integration

set -euo pipefail

echo "🌐 Configuring AI-enhanced browsers..."

# Create browser scripts directory
mkdir -p ~/bin/browser-ai

# 1. Firefox AI Sidebar
echo "🦊 Setting up Firefox AI sidebar..."
FIREFOX_SCRIPT=~/bin/browser-ai/firefox-ai-sidebar
cat > "$FIREFOX_SCRIPT" << 'EOF'
#!/bin/bash
# Firefox AI sidebar launcher with Ollama integration

# Launch Firefox with AI sidebar extensions
flatpak run org.mozilla.firefox \
    --new-window \
    "about:addons" \
    "https://addons.mozilla.org/en-US/firefox/addon/merlin/" \
    "https://addons.mozilla.org/en-US/firefox/addon/ai-sidebar/" 2>/dev/null || true
EOF

chmod +x "$FIREFOX_SCRIPT"

# Create Firefox desktop entry
cat > ~/.local/share/applications/firefox-ai.desktop << 'EOF'
[Desktop Entry]
Name=Firefox AI
Comment=Firefox with AI Sidebar
Exec=/home/sourov/bin/browser-ai/firefox-ai-sidebar
Icon=firefox
Terminal=false
Type=Application
Categories=Network;WebBrowser;
StartupWMClass=Firefox
EOF

# 2. Chromium Side Panel
echo "🌍 Setting up Chromium side panel..."
CHROMIUM_SCRIPT=~/bin/browser-ai/chromium-ai
cat > "$CHROMIUM_SCRIPT" << 'EOF'
#!/bin/bash
# Chromium with AI side panel

# Launch Chromium with AI extensions
chromium \
    --new-window \
    "chrome://extensions" \
    "https://chrome.google.com/webstore/detail/ai-sidekick/abcdef1234567890" \
    "https://chrome.google.com/webstore/detail/ollama-chat/ghijkl9876543210" 2>/dev/null || true
EOF

chmod +x "$CHROMIUM_SCRIPT"

# Create Chromium desktop entry
cat > ~/.local/share/applications/chromium-ai.desktop << 'EOF'
[Desktop Entry]
Name=Chromium AI
Comment=Chromium with AI Side Panel
Exec=/home/sourov/bin/browser-ai/chromium-ai
Icon=chromium
Terminal=false
Type=Application
Categories=Network;WebBrowser;
StartupWMClass=Chromium
EOF

# 3. Ask-Ollama Bridge
echo "🤖 Setting up ask-ollama bridge..."
OLLAMA_BRIDGE=~/bin/ask-ollama
cat > "$OLLAMA_BRIDGE" << 'EOF'
#!/bin/bash
# ask-ollama - Bridge between browsers and Ollama

# Check if Ollama is running
if ! systemctl is-active ollama > /dev/null 2>&1; then
    zenity --error --text="Ollama service is not running!" --width=300 2>/dev/null
    exit 1
fi

# Get question from user
QUESTION=$(zenity --entry \
    --title="Ask Ollama" \
    --text="Enter your question:" \
    --width=500 \
    2>/dev/null) || exit 0

if [[ -z "$QUESTION" ]]; then
    exit 0
fi

# Show thinking dialog
(
    echo "10" ; echo "# Contacting Ollama..."
    echo "30" ; echo "# Processing request..."
    RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
        -H "Content-Type: application/json" \
        -d "{\"model\": \"mistral\", \"prompt\": \"$QUESTION\"}" | \
        jq -r '.response' 2>/dev/null || echo "Error getting response")
    echo "80" ; echo "# Formatting response..."
    echo "100" ; echo "# Done!"
) | zenity --progress \
    --title="Ollama Thinking..." \
    --text="Processing your question..." \
    --percentage=0 \
    --auto-close \
    --width=400 2>/dev/null || true

# Show response
zenity --info \
    --title="Ollama Response" \
    --text="<b>Question:</b> $QUESTION

<b>Answer:</b>
$RESPONSE" \
    --width=600 \
    --height=400 \
    --html \
    2>/dev/null || true
EOF

chmod +x "$OLLAMA_BRIDGE"

# Create ask-ollama desktop entry
cat > ~/.local/share/applications/ask-ollama.desktop << 'EOF'
[Desktop Entry]
Name=Ask Ollama
Comment=Quick Ollama Query
Exec=/home/sourov/bin/ask-ollama
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;AI;
StartupWMClass=AskOllama
EOF

# 4. Optional Brave Browser
echo "🦁 Checking for Brave browser..."
if ! command -v brave &> /dev/null; then
    echo "📦 Brave not found, creating installer..."
    BRAVE_INSTALLER=~/bin/install-brave
    cat > "$BRAVE_INSTALLER" << 'BRAVE'
#!/bin/bash
# Brave browser installer

zenity --question \
    --title="Install Brave Browser" \
    --text="Brave browser not found. Install it for enhanced privacy and AI features?" \
    --width=400 2>/dev/null || exit 0

sudo pacman -S --needed brave-browser
EOF
    chmod +x "$BRAVE_INSTALLER"
else
    echo "✅ Brave browser already installed"
fi

# Create browser AI menu
BROWSER_MENU=~/.local/share/applications/browser-ai.desktop
cat > "$BROWSER_MENU" << 'EOF'
[Desktop Entry]
Name=AI Browsers
Comment=Browser AI Tools
Exec=zenity --list --title="AI Browser Tools" --column="Tool" --column="Description" "Firefox AI" "Firefox with AI sidebar" "Chromium AI" "Chromium with side panel" "Ask Ollama" "Direct Ollama queries" --width=400 --height=300 2>/dev/null || true
Icon=web-browser
Terminal=false
Type=Application
Categories=Network;
StartupWMClass=BrowserAI
EOF

echo "✅ AI browser configuration complete!"
echo ""
echo "Available tools:"
echo "  - Firefox AI (with Merlin extension)"
echo "  - Chromium AI (with side panel)"
echo "  - Ask Ollama (direct queries)"
echo "  - Brave Browser (optional)"
echo ""
echo "All tools are available in your applications menu."