#!/bin/bash
# 02-welcome-popup.sh
# Create login welcome popup with zenity

set -euo pipefail

echo "🎉 Setting up welcome popup..."

# Create welcome script
WELCOME_SCRIPT=~/bin/welcome-popup
cat > "$WELCOME_SCRIPT" << 'EOF'
#!/bin/bash

# Check if Obsidian is running
if pgrep -f "obsidian" > /dev/null; then
    OBSIDIAN_STATUS="✅ Obsidian running"
else
    OBSIDIAN_STATUS="❌ Obsidian not running"
fi

# Check wiki daemon status
if systemctl --user is-active wiki-monitor > /dev/null 2>&1; then
    WIKI_STATUS="✅ Wiki daemon active"
else
    WIKI_STATUS="❌ Wiki daemon inactive"
fi

# Check Ollama status
if systemctl is-active ollama > /dev/null 2>&1; then
    OLLAMA_STATUS="✅ Ollama running"
else
    OLLAMA_STATUS="❌ Ollama stopped"
fi

# Get wiki stats
PAGE_COUNT=$(find ~/wiki -name '*.md' 2>/dev/null | wc -l)
WIKI_SIZE=$(du -sh ~/wiki 2>/dev/null | cut -f1)

# Show welcome dialog
zenity --info \
    --title="🌅 Wiki-Linux Welcome" \
    --text="Good morning! Your wiki system is ready.

📊 System Status:
$OBSIDIAN_STATUS
$WIKI_STATUS
$OLLAMA_STATUS

📚 Wiki Stats:
$PAGE_COUNT pages | $WIKI_SIZE

🚀 Quick Actions:
- Press Super+Space for search
- Click desktop files to edit
- Plug in USB for backup

💡 Tip of the Day:
$(shuf -n 1 <<< $'
Use "wiki ask" to query your knowledge base
Create daily notes with "wiki new"
Review recent.md for daily summary
Use Obsidian graph view to see connections
Backup regularly with USB drives
')

📖 Documentation:
/wiki/HOW-TO-USE-DAILY.md
/wiki/INTEGRATION-GUIDE.md
/wiki/GITHUB-SETUP.md" \
    --width=500 \
    --height=400 \
    --ok-label="Start Working" \
    --cancel-label="Dismiss" 2>/dev/null || true
EOF

chmod +x "$WELCOME_SCRIPT"

# Add to startup applications
STARTUP_DIR=~/.config/autostart
mkdir -p "$STARTUP_DIR"

STARTUP_DESKTOP="$STARTUP_DIR/welcome-popup.desktop"
cat > "$STARTUP_DESKTOP" << EOF
[Desktop Entry]
Type=Application
Name=Wiki Welcome Popup
Comment=Show welcome message on login
Exec=/home/sourov/bin/welcome-popup
OnlyShowIn=XFCE;
StartupNotify=false
Terminal=false
Hidden=false
EOF

echo "✅ Welcome popup configured!"
echo ""
echo "A friendly welcome dialog will appear on your next login."
echo "It shows system status and quick action reminders."