#!/usr/bin/env bash
# Rich welcome/assistance popup at login.
set -euo pipefail

cat > ~/.local/bin/wiki-welcome <<'BASH'
#!/usr/bin/env bash
# Welcome popup — offers core wiki actions.
PAGES=$(find "$HOME/wiki" -name "*.md" 2>/dev/null | wc -l)
DAEMON=$(systemctl --user is-active wiki-monitor 2>/dev/null)
OLLAMA=$(systemctl is-active ollama 2>/dev/null)

choice=$(zenity --list \
  --title="Wiki — How can I help?" \
  --text="📚 $PAGES pages · daemon: $DAEMON · ollama: $OLLAMA" \
  --width=480 --height=420 \
  --column="Action" --column="Description" \
  "Open Obsidian"        "Browse and edit your wiki visually" \
  "Ask Ollama"           "Type a question, get an answer from your wiki" \
  "New Note"             "Create a new note in ~/wiki/user/notes/" \
  "Record + Transcribe"  "Record audio, save transcript as wiki page" \
  "OBS Screen Record"    "Launch OBS Studio" \
  "System Status"        "Show daemon, ollama, git stats" \
  "Sync to Git"          "Commit + push wiki right now" \
  --separator="|" 2>/dev/null) || exit 0

case "$choice" in
  "Open Obsidian")       obsidian --fullscreen "obsidian://open?vault=wiki" & ;;
  "Ask Ollama")
    q=$(zenity --entry --title="Ask Ollama" --text="Question:" --width=520) || exit 0
    ans=$(curl -s http://localhost:11434/api/generate \
      -d "{\"model\":\"mistral\",\"prompt\":$(printf '%s' "$q" | jq -Rs .),\"stream\":false}" \
      | jq -r '.response')
    echo "$ans" | zenity --text-info --title="Ollama" --width=720 --height=520
    ;;
  "New Note")
    title=$(zenity --entry --title="New Note" --text="Title:") || exit 0
    slug=$(echo "$title" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-')
    f="$HOME/wiki/user/notes/$slug.md"
    mkdir -p "$(dirname "$f")"
    printf -- "---\ntitle: %s\nupdated: %s\ntags: []\n---\n\n# %s\n\n" \
      "$title" "$(date +%Y-%m-%d)" "$title" > "$f"
    obsidian "obsidian://open?path=$f" &
    ;;
  "Record + Transcribe") xfce4-terminal -e wiki-transcribe & ;;
  "OBS Screen Record")   obs & ;;
  "System Status")
    info="Daemon:  $(systemctl --user is-active wiki-monitor)
Ollama:  $(systemctl is-active ollama)
Models:  $(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | paste -sd ', ')
Pages:   $(find "$HOME/wiki" -name "*.md" | wc -l)
Git:     $(git -C "$HOME/wiki" log --oneline | wc -l) commits
Latest:  $(git -C "$HOME/wiki" log -1 --pretty='%ar — %s')"
    zenity --info --title="Wiki Status" --text="$info" --width=520
    ;;
  "Sync to Git")
    out=$(cd "$HOME/wiki" && git add -A && git commit -m "manual sync $(date +%FT%T)" 2>&1 || true)
    zenity --info --title="Sync" --text="$out" --width=520
    ;;
esac
BASH
chmod +x ~/.local/bin/wiki-welcome

cat > ~/.config/autostart/wiki-welcome.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Wiki Welcome
Comment=Wiki assistance popup at login
Exec=$HOME/.local/bin/wiki-welcome
Hidden=false
X-GNOME-Autostart-enabled=true
X-XFCE-Autostart-Override=true
StartupNotify=false
EOF

echo "✓ Welcome popup installed and registered for autostart"
echo "  Test now: ~/.local/bin/wiki-welcome"
