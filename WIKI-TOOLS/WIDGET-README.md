# Wiki-Linux Desktop Widget

## Overview
A beautiful, helpful desktop widget that provides:
- Real-time system status
- Quick action buttons  
- Guided workflows
- Keyboard shortcuts reference

## Usage

### Launch Widget
```bash
wiki-desktop-widget
```

Or click the **📚 Wiki Guide** desktop icon in WIKI-TOOLS/

### Features

#### System Status Display
- Wiki page count
- Service status (monitor, ollama, webui)
- Color-coded indicators

#### Quick Actions
- 🔍 Search wiki
- 📝 Create new note
- 📊 View full status
- 🌐 Open WebUI
- 📁 Open vault folder
- 🔄 Restart monitor service

#### Getting Started Guide
- File drop instructions
- Keyboard shortcuts
- Web interface URLs
- Common workflows

## Keyboard Shortcut (Recommended)

Set up a global keyboard shortcut:

1. Open **Settings** → **Keyboard** → **Application Shortcuts**
2. Add new shortcut:
   - **Command**: `/home/sourov/Documents/wiki-linux/wiki-linux/bin/wiki-desktop-widget`
   - **Key**: `Super+F1` (or your preference)

## Customization

Edit the script to:
- Change colors and styling
- Add/remove quick actions
- Modify status checks
- Adjust window size

## Files

- Script: `bin/wiki-desktop-widget`
- Launcher: `WIKI-TOOLS/WIDGET-GUIDE.desktop`
- Helper: `bin/wiki-new-note` (note creation)

## Technical Details

- Uses Python 3 with zenity for GUI
- Falls back gracefully if services unavailable
- Non-blocking execution
- Auto-detects WIKI_ROOT environment variable
