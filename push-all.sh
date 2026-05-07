#!/bin/bash
# push-all.sh — install new services, set permissions, commit, and push to GitHub
# Run once: bash /home/sourov/Documents/wiki-linux/wiki-linux/push-all.sh
set -euo pipefail

WIKI_DIR="$HOME/Documents/wiki-linux/wiki-linux"
SYSTEMD_USER="$HOME/.config/systemd/user"

echo "=== Step 1: Set permissions ==="
chmod +x "$WIKI_DIR/bin/wiki-auto-unzip"
chmod +x "$WIKI_DIR/bin/wiki-file-relocate"
chmod +x "$WIKI_DIR/bin/wiki-hover-assistant"
chmod +x "$WIKI_DIR/bin/wiki-wallpaper-set"
chmod +x "$WIKI_DIR/bin/wiki-wallpaper-gen"
chmod +x "$WIKI_DIR/install-new-services.sh"
echo "  ✓ Permissions set"

echo ""
echo "=== Step 2: Install systemd services ==="
mkdir -p "$SYSTEMD_USER"
for unit in wiki-wallpaper.service wiki-wallpaper.timer \
            wiki-auto-unzip.service wiki-auto-unzip.timer \
            wiki-file-relocate.service wiki-file-relocate.timer; do
  src="$WIKI_DIR/systemd/$unit"
  if [[ -f "$src" ]]; then
    cp "$src" "$SYSTEMD_USER/$unit"
    echo "  ✓ Installed: $unit"
  fi
done

systemctl --user daemon-reload

for timer in wiki-wallpaper.timer wiki-auto-unzip.timer wiki-file-relocate.timer; do
  systemctl --user enable --now "$timer" 2>/dev/null && echo "  ✓ Enabled: $timer" || echo "  ✗ Failed: $timer"
done

echo ""
echo "=== Step 3: Force wallpaper update ==="
systemctl --user start wiki-wallpaper.service 2>/dev/null && echo "  ✓ Wallpaper updated" || echo "  ✗ Wallpaper update failed (check journalctl --user -u wiki-wallpaper.service)"

echo ""
echo "=== Step 4: Git commit and push ==="
cd "$WIKI_DIR"
git add -A
git commit -m "feat: add hover assistant, file relocation, auto-unzip, wallpaper fix, tinyllama guide

- Fix extension sidebar: correct import paths, add memory.js
- Fix background.js: remove conflicting onClicked listener
- Fix wiki-wallpaper-gen: correct WIKI_ROOT default path
- Add wiki-auto-unzip: auto-extract zip files every 5min
- Add wiki-file-relocate: safe file relocation every 30min
- Add wiki-hover-assistant: screen region AI explanation on hotkey
- Add wallpaper systemd units: wiki-wallpaper.service + timer
- Add TINYLLM-MAINTENANCE-GUIDE.md: comprehensive guide for small LMs
- Add install-new-services.sh: one-command service setup
- Add markdown conversion docs via pandoc" 2>/dev/null || echo "  (nothing new to commit)"

git push && echo "  ✓ Pushed to GitHub" || echo "  ✗ Push failed — check: git remote -v"

echo ""
echo "=== Done ==="
echo ""
echo "Active timers:"
systemctl --user list-timers wiki-wallpaper.timer wiki-auto-unzip.timer wiki-file-relocate.timer --no-pager 2>/dev/null || true
echo ""
echo "Next steps:"
echo "  1. Install pandoc: sudo pacman -S pandoc"
echo "  2. Install hover deps: sudo pacman -S xdotool imagemagick libnotify"
echo "  3. Reload extension in chrome://extensions"
echo "  4. Set hotkey: Super+Alt+H → wiki-hover-assistant --once"
echo "  5. Pull llava for vision: ollama pull llava:7b  (or use tinyllama as fallback)"
