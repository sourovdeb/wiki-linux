# Wiki-Linux Productivity Wallpaper & Screensaver

**Added:** May 2, 2026  
**Status:** ✅ Active & Running  
**Purpose:** Transform empty desktop into productivity dashboard showing live wiki metrics

---

## Overview

Instead of static wallpaper, this system displays **live wiki statistics** that update every 30 seconds:

- 📊 Page count in vault
- 📝 Total commits in git history
- 💾 Disk space available
- 🤖 Ollama models loaded
- ⏰ Time since last update
- 🕐 Current date & time

The wallpaper is generated dynamically using Python + ImageMagick, ensuring it always shows current metrics.

---

## Components

### 1. Wallpaper Generator

**File:** `~/.local/bin/wiki-wallpaper-gen`  
**Type:** Python 3 script  
**Purpose:** Query wiki stats, generate PNG image

**What it does:**
```python
# Get statistics
pages = count(~/wiki/**/*.md)
commits = git rev-list --count HEAD
disk = df -h / | available space
ollama = curl http://127.0.0.1:11434/api/tags | count models
updated = git log -1 --format=%ar

# Create image
1. Start with dark gradient (1920x1080)
2. Add white text with statistics
3. Add green footer text
4. Save as PNG
```

**Output:** `~/.cache/wiki-wallpaper/wiki-wallpaper.png`

### 2. Wallpaper Setter

**File:** `~/.local/bin/wiki-wallpaper-set`  
**Type:** Bash script  
**Purpose:** Apply generated wallpaper to XFCE desktop

**What it does:**
```bash
# Generate fresh wallpaper
python3 wiki-wallpaper-gen

# Apply to XFCE desktop (all monitors)
xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor*/image-path -s <wallpaper>

# Tries multiple monitor names for compatibility
```

### 3. Systemd Timer & Service

**Timer:** `~/.config/systemd/user/wiki-wallpaper.timer`  
**Service:** `~/.config/systemd/user/wiki-wallpaper.service`

**Configuration:**
```ini
[Timer]
OnBootSec=5sec           # Start 5 seconds after boot
OnUnitActiveSec=30sec    # Update every 30 seconds
```

**Status:**
```bash
systemctl --user status wiki-wallpaper.timer
systemctl --user status wiki-wallpaper.service
```

---

## How to Use

### Automatic (Recommended)

The wallpaper updates **every 30 seconds automatically** via systemd timer.

```bash
# Check it's running
systemctl --user is-active wiki-wallpaper.timer
✓ active

# View recent updates
journalctl --user -u wiki-wallpaper.service -n 5
```

### Manual Update

```bash
# Force immediate wallpaper update
~/.local/bin/wiki-wallpaper-set

# Or just generate (don't apply)
~/.local/bin/wiki-wallpaper-gen
# Output: /home/sourov/.cache/wiki-wallpaper/wiki-wallpaper.png
```

### Enable/Disable

```bash
# Enable wallpaper updates (on boot and every 30s)
systemctl --user enable wiki-wallpaper.timer
systemctl --user start wiki-wallpaper.timer

# Disable wallpaper updates
systemctl --user stop wiki-wallpaper.timer
systemctl --user disable wiki-wallpaper.timer
```

---

## Screensaver Integration

### Terminal Screensaver

**File:** `~/.local/bin/wiki-screensaver-daemon`  
**Type:** Bash script  
**Purpose:** Display wiki dashboard in terminal when idle

**What it shows:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                    WIKI-LINUX PRODUCTIVITY SCREENSAVER                     ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 Pages: 77
📝 Commits: 38
💾 Disk Available: 99G
🤖 Ollama: 3 models
⏰ Updated: 2 hours ago
🕐 Time: 2026-05-02 15:30:45

✓ System Online | ✓ All Services Running | ✓ Wiki Synced
```

**Run manually:**
```bash
~/.local/bin/wiki-screensaver-daemon

# Press Ctrl+C to stop
```

---

## Wallpaper Customization

### Change Update Frequency

Edit `~/.config/systemd/user/wiki-wallpaper.timer`:

```ini
[Timer]
OnUnitActiveSec=60sec    # Change from 30sec to 60sec
```

Then reload:
```bash
systemctl --user daemon-reload
systemctl --user restart wiki-wallpaper.timer
```

### Change Wallpaper Style

Edit `~/.local/bin/wiki-wallpaper-gen` Python script:

```python
# Modify colors
"gradient:#1a1a2e-#16213e"  # Change gradient colors

# Modify text style
"-font", "DejaVu-Sans-Mono"  # Change font
"-pointsize", "32"           # Change size
"-fill", "white"             # Change text color
```

Then regenerate:
```bash
~/.local/bin/wiki-wallpaper-set
```

### Change Displayed Metrics

Edit `~/.local/bin/wiki-wallpaper-gen` to add/remove statistics:

```python
stats = {
    "pages": get_page_count(),      # Show page count
    "commits": get_commit_count(),  # Show commits
    "disk": get_disk_available(),   # Show disk space
    "ollama": get_ollama_models(),  # Show model count
    # Add more...
}
```

---

## Troubleshooting

### Wallpaper Not Updating

**Check timer status:**
```bash
systemctl --user status wiki-wallpaper.timer
# Should show: "active (running)"
```

**Check service logs:**
```bash
journalctl --user -u wiki-wallpaper.service -n 10
```

**Manually run:**
```bash
~/.local/bin/wiki-wallpaper-set
# Should print: ✓ Wallpaper updated: /home/sourov/.cache/wiki-wallpaper/wiki-wallpaper.png
```

### Generator Errors

**Python issues:**
```bash
python3 ~/.local/bin/wiki-wallpaper-gen
# Should output: /home/sourov/.cache/wiki-wallpaper/wiki-wallpaper.png
```

**ImageMagick issues:**
```bash
# Check convert is available
which magick convert

# Test image creation
convert -size 1920x1080 "gradient:#1a1a2e-#16213e" /tmp/test.png
```

### Wallpaper Not Showing

**Check XFCE is receiving it:**
```bash
xfconf-query -c xfce4-desktop -l | grep image-path
# Should list wallpaper paths
```

**Manually set via XFCE GUI:**
- Right-click desktop
- Desktop Settings
- Background tab
- Select wallpaper file: `~/.cache/wiki-wallpaper/wiki-wallpaper.png`

---

## Performance Impact

- **CPU:** Negligible (Python script runs every 30s for ~2 seconds)
- **Memory:** ~50MB for image generation + caching
- **Disk:** ~200KB per wallpaper (old ones auto-cleaned)

**Auto-cleanup:**
```bash
# Old frames deleted after 2 minutes
find ~/.cache/wiki-screensaver -name "frame-*.txt" -mmin +2 -delete
```

---

## Integration with Cline Maintenance

When Cline runs maintenance, wallpaper is **not** stopped or disrupted:

```bash
cline          # Runs maintenance
# Wallpaper continues updating in background
wiki doctor    # Safety check
# Wallpaper still running
```

The wallpaper is **independent** and safe to leave running during system operations.

---

## Reproduction on New System

When deploying wiki-linux to a new Arch machine:

1. **Install scripts:**
   ```bash
   cp ~/.local/bin/wiki-wallpaper-* /new-system/~/.local/bin/
   ```

2. **Install systemd units:**
   ```bash
   cp ~/.config/systemd/user/wiki-wallpaper.* /new-system/~/.config/systemd/user/
   systemctl --user daemon-reload
   ```

3. **Enable on new system:**
   ```bash
   systemctl --user enable wiki-wallpaper.timer
   systemctl --user start wiki-wallpaper.timer
   ```

**All configured in:** `install-reproducible.sh` + `config.portable.json`

---

## Files Summary

| File | Type | Purpose |
|------|------|---------|
| `~/.local/bin/wiki-wallpaper-gen` | Python | Generate wallpaper image |
| `~/.local/bin/wiki-wallpaper-set` | Bash | Apply wallpaper to desktop |
| `~/.local/bin/wiki-screensaver-daemon` | Bash | Terminal screensaver |
| `~/.config/systemd/user/wiki-wallpaper.service` | Systemd | Service definition |
| `~/.config/systemd/user/wiki-wallpaper.timer` | Systemd | Timer trigger (every 30s) |
| `~/.cache/wiki-wallpaper/` | Dir | Generated wallpaper images |

---

## References

- **FINAL-SYSTEM-STATUS.md** — System overview
- **OBSIDIAN-SYSTEM-BLUEPRINT.md** — Complete system blueprint
- **SYSTEM-REPRODUCIBLE.md** — Deployment procedure
- **CLINE-INSTRUCTIONS.md** — Maintenance manual

---

**Status:** ✅ Fully implemented and tested  
**Last updated:** May 2, 2026  
**Maintained by:** Claude Code  
