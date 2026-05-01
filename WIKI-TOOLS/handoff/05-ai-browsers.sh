#!/usr/bin/env bash
# Configure Firefox + Chromium to feel like Comet (AI sidebar + ollama bridge).
set -euo pipefail

# === Shared CLI bridge: ask-ollama ===
cat > ~/.local/bin/ask-ollama <<'BASH'
#!/usr/bin/env bash
# Usage: ask-ollama "<question>"  → prints answer to stdout.
q="${*:-$(cat)}"
curl -s http://localhost:11434/api/generate \
  -d "$(jq -n --arg p "$q" '{model:"mistral",prompt:$p,stream:false}')" \
  | jq -r '.response'
BASH
chmod +x ~/.local/bin/ask-ollama

# === FIREFOX ===
FF_PROFILE=$(find ~/.mozilla/firefox -maxdepth 1 -type d -name "*.default*" 2>/dev/null | head -1 || true)
if [ -n "$FF_PROFILE" ]; then
  cat > "$FF_PROFILE/user.js" <<'EOF'
// Built-in AI chat sidebar
user_pref("browser.ml.chat.enabled", true);
user_pref("browser.ml.chat.sidebar", true);
user_pref("browser.ml.chat.shortcuts", true);
user_pref("browser.ml.chat.provider", "http://localhost:11434");
// Quick AI from selected text
user_pref("browser.ml.chat.menu", true);
EOF
  echo "✓ Firefox AI sidebar prefs written to: $FF_PROFILE/user.js"
else
  echo "⚠ No Firefox profile found — open Firefox once, then re-run."
fi

# === CHROMIUM ===
mkdir -p ~/.config/chromium-flags.conf.d
cat > ~/.config/chromium-flags.conf <<'EOF'
--enable-features=SidePanelPinning,ReadAnything
--password-store=basic
EOF

cat > ~/.local/share/applications/chromium-ai.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Chromium (Wiki AI)
Exec=chromium --side-panel-enabled
Icon=chromium
Categories=Network;WebBrowser;
EOF

# === Optional: Brave (closest free Comet equivalent) ===
echo
read -rp "Install Brave Browser (Leo AI uses Ollama)? [y/N] " ans
if [[ "$ans" =~ ^[Yy]$ ]]; then
  if command -v yay >/dev/null; then
    yay -S --noconfirm brave-bin
  else
    echo "⚠ yay not installed. Install with: sudo pacman -S yay-bin (or build from AUR)."
  fi
fi

echo
echo "✓ Browser AI configured."
echo "  Firefox: open → click sidebar icon → AI Chat panel."
echo "  Chromium: launch via 'Chromium (Wiki AI)' menu entry."
echo "  CLI:    echo 'summarise this page' | ask-ollama"
