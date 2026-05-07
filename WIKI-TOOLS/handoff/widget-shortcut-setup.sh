#!/usr/bin/env bash
# Setup keyboard shortcut for wiki-desktop-widget
set -euo pipefail

widget_script="/home/sourov/Documents/wiki-linux/wiki-linux/bin/wiki-desktop-widget"

cat <<'EOF'
╔════════════════════════════════════════════════════════════╗
║        Wiki-Linux Desktop Widget Shortcut Setup            ║
╚════════════════════════════════════════════════════════════╝

To add a keyboard shortcut for the desktop widget:

1. Open XFCE Settings → Keyboard → Application Shortcuts
   (or run: xfce4-keyboard-settings)

2. Click "Add" button

3. Enter command:
   /home/sourov/Documents/wiki-linux/wiki-linux/bin/wiki-desktop-widget

4. Press your desired key combination
   Recommended: Super+F1 or Super+H (for Help)

5. Click OK

The widget will now open with your chosen shortcut!

Alternative: Manual configuration
----------------------------------
Add this to ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml

    <property name="&lt;Super&gt;F1" type="string" value="/home/sourov/Documents/wiki-linux/wiki-linux/bin/wiki-desktop-widget"/>

Then run: xfce4-panel -r

EOF

read -p "Open keyboard settings now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    xfce4-keyboard-settings &
fi
