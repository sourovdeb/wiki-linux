# Wiki Desktop Live Widget

## Overview
Persistent desktop overlay that displays wiki system status, keyboard shortcuts, and quick commands. Updates every 30 seconds.

## Features
- Beautiful ASCII box design with ANSI colors
- Real-time status monitoring:
  - Page count
  - wiki-monitor daemon status
  - Ollama API status
  - WebUI status
  - Last git update time
- Keyboard shortcuts reference
- Web interface URLs
- Common commands

## Usage

### Start Widget
```bash
wiki-desktop-live
# Or from menu: WIKI-TOOLS → Desktop Live Widget
```

### Stop Widget
```bash
wiki-desktop-live-stop
# Or: pkill -f "Wiki-Linux Guide"
```

### Configuration
- **Position**: Top-left corner (10px from left, 60px from top)
- **Size**: 40 columns × 25 rows
- **Font**: Monospace Bold 10pt
- **Refresh**: Every 30 seconds
- **Window Properties**:
  - Sticky (visible on all workspaces)
  - Below other windows (desktop layer)
  - Skip taskbar
  - Skip pager
  - Optional transparency (if compositor running)

## Autostart
Widget auto-starts on login via `~/.config/autostart/wiki-desktop-live.desktop`.

To disable autostart:
```bash
rm ~/.config/autostart/wiki-desktop-live.desktop
```

## Requirements
- xfce4-terminal
- wmctrl (for window management)
- curl (for API health checks)
- git (for update info)

## Customization

### Change Position
Edit `--geometry` flag in `bin/wiki-desktop-live`:
```bash
--geometry=40x25+LEFT+TOP
```
- LEFT: pixels from left edge
- TOP: pixels from top edge

### Change Update Frequency
Edit `sleep 30` line to desired seconds.

### Change Colors
ANSI color codes used:
- `[1;36m` = bright cyan (borders)
- `[1;33m` = bright yellow (title)
- `[1;32m` = bright green (active status)
- `[1;31m` = bright red (inactive status)
- `[1;35m` = bright magenta (shortcuts)
- `[1;34m` = bright blue (URLs)
- `[0;32m` = green (commands)
- `[0;90m` = dark gray (timestamp)

## Troubleshooting

### Widget Not Appearing
1. Check if running: `cat /tmp/wiki-desktop-live.pid`
2. Kill and restart: `wiki-desktop-live-stop && wiki-desktop-live`
3. Check xfce4-terminal: `which xfce4-terminal`

### Window Position Wrong
Use wmctrl to manually position:
```bash
wmctrl -r "Wiki-Linux Guide" -e 0,10,60,420,550
```

### No Transparency
Transparency requires compositor (picom/compton):
```bash
picom -b  # Start compositor in background
```

## Files
- `bin/wiki-desktop-live` - Main widget script
- `bin/wiki-desktop-live-stop` - Stop script
- `~/.config/autostart/wiki-desktop-live.desktop` - Autostart config
- `/tmp/wiki-desktop-live.pid` - PID file

## Related
- [wiki-desktop-widget](../bin/wiki-desktop-widget) - Dialog-based interactive widget
- [wiki-startup-report](../bin/wiki-startup-report) - Session startup report
- [wiki-status-panel](../bin/wiki-status-panel) - Full status dashboard
