#!/bin/bash
# 01-xfce-desktop-as-wiki.sh
# Make XFCE desktop show wiki folder contents

set -euo pipefail

echo "📁 Configuring XFCE desktop to show wiki folder..."

# Create symlink to wiki on desktop
if [[ -e ~/Desktop/wiki ]]; then
    echo "⚠️  ~/Desktop/wiki already exists"
else
    echo "🔗 Creating symlink: ~/Desktop/wiki → ~/wiki"
    ln -s ~/wiki ~/Desktop/wiki
fi

# Configure xfdesktop to show folder contents
XFDESKTOP_CONFIG=~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml

if [[ ! -f "$XFDESKTOP_CONFIG" ]]; then
    echo "⚠️  xfdesktop config not found, creating default..."
    mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml
    echo '<?xml version="1.0" encoding="UTF-8"?>

<channel name="xfce4-desktop" version="1.0">
  <property name="desktop-icons" type="empty">
    <property name="file-icons" type="empty">
      <property name="show-filesystem" type="bool" value="false"/>
      <property name="show-home" type="bool" value="false"/>
      <property name="show-trash" type="bool" value="false"/>
      <property name="show-removable" type="bool" value="false"/>
    </property>
    <property name="show-thumbnails" type="bool" value="true"/>
    <property name="thumbnail-size" type="uint" value="96"/>
  </property>
</channel>' > "$XFDESKTOP_CONFIG"
fi

# Configure desktop to show folder contents
echo "📝 Configuring xfdesktop for folder view..."
xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-filesystem -s false
xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-home -s false
xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-trash -s false
xfconf-query -c xfce4-desktop -p /desktop-icons/file-icons/show-removable -s false
xfconf-query -c xfce4-desktop -p /desktop-icons/show-thumbnails -s true
xfconf-query -c xfce4-desktop -p /desktop-icons/thumbnail-size -s 96

# Add Thunar custom action for wiki operations
THUNAR_UCA=~/.config/Thunar/uca.xml
mkdir -p ~/.config/Thunar

if [[ ! -f "$THUNAR_UCA" ]]; then
    echo "📝 Creating Thunar custom actions..."
    echo '<?xml version="1.0" encoding="UTF-8"?>
<actions>
  <action>
    <icon>text-x-markdown</icon>
    <name>Open in Obsidian</name>
    <command>flatpak run md.obsidian.Obsidian --vault %f</command>
    <description>Open this folder in Obsidian</description>
    <patterns>*</patterns>
    <directories/>
    <audio-files/>
    <image-files/>
    <other-files/>
    <text-files/>
    <video-files/>
  </action>
  <action>
    <icon>utilities-terminal</icon>
    <name>Open Terminal Here</name>
    <command>xfce4-terminal --working-directory=%f</command>
    <description>Open terminal in this folder</description>
    <patterns>*</patterns>
    <directories/>
  </action>
  <action>
    <icon>document-new</icon>
    <name>New Wiki Note</name>
    <command>wiki new "Note about %n"</command>
    <description>Create new wiki note about this file</description>
    <patterns>*</patterns>
    <other-files/>
    <text-files/>
  </action>
</actions>' > "$THUNAR_UCA"
else
    echo "⚠️  Thunar custom actions already exist"
fi

# Restart xfdesktop to apply changes
echo "🔄 Restarting xfdesktop..."
xfdesktop --reload

echo "✅ Desktop configuration complete!"
echo ""
echo "Your XFCE desktop now shows wiki folder contents."
echo "Right-click files for wiki-specific actions."