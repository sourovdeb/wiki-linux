#!/usr/bin/env bash
# Make the XFCE desktop point at ~/wiki so the wiki contents ARE the desktop.
set -euo pipefail
WIKI="$HOME/wiki"

# 1. Tell xfdesktop to use ~/wiki as its desktop folder
xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-home -s false || true
xfconf-query -c xfce4-desktop -p /desktop-icons/style -s 2 || true   # 2 = file/launcher icons
# The folder shown on the desktop:
xfconf-query -c xfce4-desktop -np /desktop-icons/desktop-folder -t string -s "$WIKI" 2>/dev/null \
  || xfconf-query -c xfce4-desktop -p /desktop-icons/desktop-folder -s "$WIKI"

# 2. Symlink XDG Desktop dir to ~/wiki so apps that drop files on Desktop land in wiki
if [ -d "$HOME/Desktop" ] && [ ! -L "$HOME/Desktop" ]; then
  mv "$HOME/Desktop" "$HOME/Desktop.bak.$(date +%s)"
fi
ln -sfn "$WIKI" "$HOME/Desktop"

# 3. Thunar custom action: "Open in Obsidian"
UCA="$HOME/.config/Thunar/uca.xml"
mkdir -p "$(dirname "$UCA")"
if [ ! -f "$UCA" ] || ! grep -q "Open in Obsidian" "$UCA"; then
  cat > "$UCA" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<actions>
  <action>
    <icon>obsidian</icon>
    <name>Open in Obsidian</name>
    <unique-id>obsidian-1</unique-id>
    <command>obsidian "obsidian://open?path=%f"</command>
    <description>Open the selected note in Obsidian</description>
    <patterns>*.md</patterns>
    <startup-notify/>
    <text-files/>
  </action>
</actions>
EOF
fi

# 4. Reload xfdesktop to pick up changes
xfdesktop --reload >/dev/null 2>&1 || true

echo "✓ Desktop now mirrors ~/wiki"
echo "  Verify: log out, log back in. Or run: xfdesktop --reload"
