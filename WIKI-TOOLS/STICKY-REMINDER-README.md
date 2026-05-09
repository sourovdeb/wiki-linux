# Wiki-Linux Sticky Reminder

A desktop sticky note reminder system that overlays your reminders on your desktop wallpaper.

## Features

- **Visual Sticky Notes**: Shows reminders as yellow sticky notes on your desktop wallpaper
- **Automatic Updates**: Can run as a daemon to check reminders every 5 minutes
- **Wallpaper Integration**: Overlays sticky notes on your existing wallpaper
- **Desktop Notifications**: Shows pop-up notifications when reminders are due
- **OpenWebUI Integration**: Works with the existing Wiki-Linux reminder system

## Installation

The sticky reminder is already installed as part of the Wiki-Linux system.

## Usage

### Basic Usage

```bash
# Show sticky reminders once
./bin/wiki-sticky-reminder

# Run as daemon (checks every 5 minutes)
./bin/wiki-sticky-reminder --daemon
```

### Systemd Service

To run the sticky reminder as a system service:

```bash
# Copy the service file
cp systemd/wiki-sticky-reminder.service ~/.config/systemd/user/

# Enable and start the service
systemctl --user enable wiki-sticky-reminder.service
systemctl --user start wiki-sticky-reminder.service

# Check status
systemctl --user status wiki-sticky-reminder.service
```

### Desktop Shortcut

A desktop shortcut is available at `WIKI-TOOLS/14-STICKY-REMINDER.desktop`. You can copy this to your desktop or applications menu.

## How It Works

1. **Loads Reminders**: Reads from `_meta/reminders.jsonl` (same as the OpenWebUI reminder system)
2. **Filters Due Reminders**: Shows only reminders that are due or pending
3. **Creates Sticky Note**: Generates a yellow sticky note image with your reminders
4. **Overlays on Wallpaper**: Combines the sticky note with your current wallpaper
5. **Updates Desktop**: Sets the combined image as your new wallpaper
6. **Shows Notification**: Displays a desktop notification about due reminders

## Customization

You can customize the appearance by modifying the `bin/wiki-sticky-reminder` script:

- **Sticky Note Size**: Change the `400x300` dimensions
- **Colors**: Modify the hex color codes (`#fff9c4`, `#f9f1a5`, `#5d4037`)
- **Position**: Adjust the `-geometry "+20+20"` parameters
- **Font**: Change the font name and size

## Requirements

- Python 3.6+
- ImageMagick (`magick` or `convert` command)
- `notify-send` for desktop notifications
- One of the following for wallpaper setting:
  - `gsettings` (GNOME)
  - `feh` (lightweight)
  - `nitrogen` (multi-monitor)
  - `xfconf-query` (XFCE)

## Troubleshooting

- **No reminders found**: Make sure you have reminders in `_meta/reminders.jsonl`
- **Wallpaper not updating**: Try manually setting the wallpaper using your desktop environment's settings
- **ImageMagick not found**: Install ImageMagick (`sudo apt install imagemagick` on Debian/Ubuntu)
- **Font not found**: Install DejaVu fonts (`sudo apt install fonts-dejavu`)

## Integration with OpenWebUI

The sticky reminder integrates seamlessly with the OpenWebUI reminder system:

1. Add reminders using the OpenWebUI interface or CLI
2. The sticky reminder automatically picks up due reminders
3. When you complete a reminder, it gets marked as "fired" and disappears from the sticky note

## Examples

```bash
# Add a reminder using the CLI
python3 copilot/06_reminder.py add "Finish project report" "tomorrow 9am"

# List all reminders
python3 copilot/06_reminder.py list

# Check due reminders (this is what the sticky reminder does automatically)
python3 copilot/06_reminder.py check_due

# Then run the sticky reminder to see them on your desktop
./bin/wiki-sticky-reminder
```

## Files

- `bin/wiki-sticky-reminder` - Main application script
- `systemd/wiki-sticky-reminder.service` - Systemd service file
- `WIKI-TOOLS/14-STICKY-REMINDER.desktop` - Desktop shortcut
- `_meta/reminders.jsonl` - Reminder data file (shared with OpenWebUI)
- `~/.cache/wiki-sticky/` - Cache directory for generated images