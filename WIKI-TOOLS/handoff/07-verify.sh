#!/usr/bin/env bash
# Final verification — all green = done.
set +e
ok=0; fail=0
check() {
  if eval "$2" >/dev/null 2>&1; then
    printf "  ✓ %s\n" "$1"; ok=$((ok+1))
  else
    printf "  ✗ %s\n" "$1"; fail=$((fail+1))
  fi
}

echo "=== Wiki-Linux Final Verification ==="
check "Obsidian installed"         "command -v obsidian"
check "OBS Studio installed"       "command -v obs"
check "whisper installed"          "command -v whisper"
check "wiki-monitor active"        "systemctl --user is-active wiki-monitor | grep -q active"
check "ollama active"              "systemctl is-active ollama | grep -q active"
check "Toleria removed"            "! command -v tolaria"
check "Obsidian autostart"         "test -f $HOME/.config/autostart/obsidian-wiki.desktop"
check "Welcome popup autostart"    "test -x $HOME/.local/bin/wiki-welcome"
check "wiki-transcribe present"    "test -x $HOME/.local/bin/wiki-transcribe"
check "ask-ollama present"         "test -x $HOME/.local/bin/ask-ollama"
check "BMO plugin in vault"        "test -f $HOME/wiki/.obsidian/plugins/bmo-chatbot/main.js"
check "Default vault registered"   "grep -q '/home/sourov/wiki' $HOME/.config/obsidian/obsidian.json"
check "Desktop = wiki symlink"     "test -L $HOME/Desktop && [ \"\$(readlink $HOME/Desktop)\" = \"$HOME/wiki\" ]"
check "xfdesktop folder = wiki"    "xfconf-query -c xfce4-desktop -p /desktop-icons/desktop-folder | grep -q wiki"
check "Ollama models loaded"       "curl -sf http://localhost:11434/api/tags | jq -e '.models|length>=4'"
check "Firefox AI prefs"           "ls $HOME/.mozilla/firefox/*.default*/user.js 2>/dev/null | head -1 | xargs grep -q ml.chat.enabled"
echo
echo "  $ok ok  /  $fail failing"
[ "$fail" -eq 0 ] && echo "  🎉 All green — ready to commit." \
                  || echo "  Fix the failing items above, then re-run."
