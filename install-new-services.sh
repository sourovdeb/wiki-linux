#!/bin/bash
# install-new-services.sh — install and enable all new wiki-linux systemd user services
# Run once after pulling changes.
set -euo pipefail

WIKI_DIR="$HOME/Documents/wiki-linux/wiki-linux"
SYSTEMD_USER="$HOME/.config/systemd/user"
SERVICES_SRC="$WIKI_DIR/systemd"

echo "→ Installing new wiki-linux systemd services..."

mkdir -p "$SYSTEMD_USER"

# Copy new service/timer files
for unit in wiki-wallpaper.service wiki-wallpaper.timer \
            wiki-auto-unzip.service wiki-auto-unzip.timer \
            wiki-file-relocate.service wiki-file-relocate.timer; do
  if [[ -f "$SERVICES_SRC/$unit" ]]; then
    cp "$SERVICES_SRC/$unit" "$SYSTEMD_USER/$unit"
    echo "  ✓ Installed: $unit"
  fi
done

# Make bin scripts executable
chmod +x "$WIKI_DIR/bin/wiki-auto-unzip"
chmod +x "$WIKI_DIR/bin/wiki-file-relocate"
chmod +x "$WIKI_DIR/bin/wiki-wallpaper-set"
chmod +x "$WIKI_DIR/bin/wiki-wallpaper-gen"
chmod +x "$WIKI_DIR/bin/wiki-hover-assistant"

# Reload systemd user daemon
systemctl --user daemon-reload

# Enable and start timers
for timer in wiki-wallpaper.timer wiki-auto-unzip.timer wiki-file-relocate.timer; do
  systemctl --user enable --now "$timer" && echo "  ✓ Enabled: $timer" || echo "  ✗ Failed: $timer"
done

echo ""
echo "→ Service status:"
systemctl --user is-active wiki-wallpaper.timer wiki-auto-unzip.timer wiki-file-relocate.timer

echo ""
echo "→ Force wallpaper update now..."
systemctl --user start wiki-wallpaper.service || true

echo ""
echo "✅ Done. New services active:"
echo "   wiki-wallpaper.timer    — wallpaper updates every 30s"
echo "   wiki-auto-unzip.timer   — auto-unzip in wiki dir every 5min"
echo "   wiki-file-relocate.timer — relocate files every 30min"
echo ""
echo "Hover assistant: configure hotkey Super+Alt+H to run:"
echo "  $WIKI_DIR/bin/wiki-hover-assistant --once"
echo ""
echo "Install pandoc for markdown conversion: sudo pacman -S pandoc"
