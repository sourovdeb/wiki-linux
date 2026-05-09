# i3 Window Manager Preparation Guide

> Migrating from XFCE/KDE to i3 while preserving the wiki-linux LLM system integrity.

## Overview

This guide prepares the wiki-linux system for migration to **i3 window manager** (a lightweight, keyboard-driven tiling window manager). The goal is to maintain the Karpathy 3-layer LLM wiki architecture while simplifying the desktop environment to reduce memory footprint and improve responsiveness.

---

## Pre-Migration Checklist

**Run these checks before starting migration to i3:**

- [ ] System disk space is healthy: `df -h /` ≥ 10GB free
- [ ] All maintenance timers are active: `systemctl --user list-timers`
- [ ] OpenWebUI is running: `curl http://127.0.0.1:8080 -s | head -c 50`
- [ ] Ollama is accessible: `curl http://127.0.0.1:11434/api/tags -s`
- [ ] Git sync is current: `cd ~/wiki && git status` (clean)
- [ ] Backup `~/.config` and `~/.local` (optional but recommended)

### Quick Health Check

```bash
# All-in-one pre-migration check
df -h / && \
  systemctl --user list-timers | grep wiki && \
  systemctl --user status wiki-system-maintenance.timer && \
  pgrep -la "ollama|python.*openwebui" && \
  echo "✓ All systems ready for i3 migration"
```

---

## i3 Installation & Setup

### Step 1: Install i3 and Dependencies

```bash
# Install i3 and essential tools (as sudo)
sudo apt update
sudo apt install -y \
  i3-wm \
  i3status \
  dmenu \
  xterm \
  xset \
  xrandr \
  feh \
  picom \
  dunst

# Optional: add-ons for productivity
sudo apt install -y \
  alacritty \        # Fast terminal
  rofi \             # App launcher (alternative to dmenu)
  libnotify-bin \    # Notification support
  pulseaudio \
  pavucontrol
```

### Step 2: Verify Installation

```bash
i3 --version
which i3
ls ~/.config/i3/ 2>/dev/null || echo "i3 config will be created at first login"
```

---

## Safe Migration Path

### Phase 1: Prepare Current Session (XFCE/KDE → i3)

**Do NOT remove XFCE/KDE** — keep them as fallback.

1. **Install i3 alongside existing DE:**
   ```bash
   # i3 will appear in login screen
   # Keep XFCE/KDE selected until i3 is fully tested
   ```

2. **Test i3 in a separate session** (if your login manager supports it):
   ```bash
   # Log out, click session selector, choose i3
   # Or boot a live VM to test first
   ```

3. **Disable heavyweight services** before first i3 login:
   ```bash
   # Run the existing trim script to reduce background load
   bash ~/Documents/wiki-linux/wiki-linux/WIKI-TOOLS/handoff/04-trim-services.sh
   ```

### Phase 2: Configure i3 for wiki-linux

When you first log into i3, it will create a default config at `~/.config/i3/config`. Edit it with these wiki-linux-specific additions:

```bash
# Edit the i3 config
$EDITOR ~/.config/i3/config
```

**Add these lines to `~/.config/i3/config`:**

```ini
# ─── Wiki-Linux Auto-Start ───────────────────────────────────────────────────
exec_always --no-startup-id feh --bg-fill /home/sourov/wiki/_meta/wallpaper.png

# Launch wiki monitor (file watcher)
exec --no-startup-id ~/.local/bin/wiki-monitor

# Launch wiki-sync (git sync timer user session)
exec --no-startup-id systemctl --user start wiki-sync.timer

# Launch OpenWebUI in background (optional; can start manually)
# exec --no-startup-id ~/.local/bin/wiki-openwebui-start

# Launch notification daemon (for wiki reminders)
exec_always --no-startup-id dunst

# Launch compositor (for smooth rendering and transparency)
exec_always --no-startup-id picom -f

# ─── Wiki Status Bar Binding ──────────────────────────────────────────────────
# Quick status check: Super+Shift+W
bindsym $mod+Shift+w exec xterm -e bash -c '\
  echo "=== Wiki-Linux Status ==="; \
  wiki-quick-check; \
  read -p "Press ENTER to close..."'

# ─── Wiki App Launcher ─────────────────────────────────────────────────────────
# Open Obsidian with wiki: Super+O
bindsym $mod+o exec obsidian

# Open OpenWebUI browser: Super+W
bindsym $mod+w exec firefox http://127.0.0.1:8080

# Open terminal in wiki root: Super+Shift+T
bindsym $mod+Shift+t exec alacritty --working-directory ~/wiki

# ─── System Maintenance Shortcuts ──────────────────────────────────────────────
# Run health check: Super+H
bindsym $mod+h exec xterm -e bash -c '\
  systemctl --user status wiki-system-maintenance.timer && \
  read -p "Press ENTER to close..."'

# Run manual maintenance: Super+Shift+M (careful!)
bindsym $mod+Shift+m exec xterm -e ~/.local/bin/wiki-system-maintenance

# ─── Wallpaper & Screensaver ───────────────────────────────────────────────────
# Regenerate wallpaper: Super+Shift+W (set manually)
# bindsym $mod+Shift+w exec ~/.local/bin/wiki-wallpaper-gen

# ─── Notification Settings ─────────────────────────────────────────────────────
# Dunst uses right-click or keyboard to dismiss
# Configure at ~/.config/dunst/dunstrc
```

### Phase 3: Disable i3-specific Desktop Features (Not Needed in i3)

The following systemd services become redundant in i3 and can be masked to save resources:

```bash
# Mask these in i3 (they are XFCE/KDE specific)
systemctl --user mask \
  wiki-wallpaper.timer \      # i3 doesn't use wallpaper manager
  wiki-desktop-live.service   # i3 has no desktop widget overlay

# Keep these active (they work in any DE/WM)
systemctl --user enable --now \
  wiki-system-maintenance.timer \
  wiki-sync.timer \
  wiki-monitor.service
```

---

## i3 Configuration Best Practices

### Essential i3 Keybindings for wiki-linux

Add to `~/.config/i3/config`:

| Shortcut | Action |
|----------|--------|
| `$mod+Enter` | Open terminal (default) |
| `$mod+d` | Open app menu (dmenu/rofi) |
| `$mod+h/j/k/l` | Navigate tiles (Vim-like) |
| `$mod+Shift+h/j/k/l` | Move window (Vim-like) |
| `$mod+1` to `$mod+0` | Switch workspace 1–10 |
| `$mod+Shift+1` | Move window to workspace 1 |
| `$mod+v` | Split vertical |
| `$mod+h` | Split horizontal |
| `$mod+f` | Toggle fullscreen |
| `$mod+Shift+f` | Toggle floating mode |
| `$mod+Space` | Toggle layout (tiling/floating) |
| `$mod+e` | Toggle layout (default/stacked) |
| `$mod+s` | Toggle layout (tabbed) |
| `$mod+Shift+e` | Exit i3 (with prompt) |
| `$mod+Shift+r` | Reload i3 config |
| `$mod+r` | Enter resize mode |

### Workspaces for wiki-linux

```ini
# Suggested workspace layout
workspace 1 output primary  # Main work area
workspace 2 output primary  # Terminal / wiki root
workspace 3 output primary  # OpenWebUI / browser
workspace 4 output primary  # Obsidian / notes
workspace 5 output primary  # System monitoring / status
```

### i3bar Status Configuration

Create or edit `~/.config/i3status/config`:

```ini
general {
    colors = true
    interval = 5
}

order += "disk /"
order += "memory"
order += "cpu_usage"
order += "tztime local"

disk "/" {
    format = "💾 %avail"
    threshold_type = "gbytes_avail"
    low_threshold = 2
}

memory {
    format = "🧠 %used / %total"
    threshold_degraded = "10%"
}

cpu_usage {
    format = "⚙️ %usage"
}

tztime local {
    format = "%Y-%m-%d %H:%M"
}
```

---

## Desktop Files & Application Launchers

Create desktop entry files for quick access to wiki apps in i3:

### `~/.local/share/applications/wiki-quick-check.desktop`
```ini
[Desktop Entry]
Type=Application
Name=Wiki Quick Check
Comment=Show wiki-linux system status
Exec=xterm -e ~/.local/bin/wiki-quick-check
Terminal=false
Categories=Utility;
```

### `~/.local/share/applications/wiki-openwebui.desktop`
```ini
[Desktop Entry]
Type=Application
Name=Wiki OpenWebUI
Comment=Open OpenWebUI knowledge base interface
Exec=firefox http://127.0.0.1:8080
Terminal=false
Categories=Utility;Network;
```

### `~/.local/share/applications/wiki-obsidian.desktop`
```ini
[Desktop Entry]
Type=Application
Name=Wiki Obsidian
Comment=Open Obsidian with wiki vault
Exec=obsidian
Terminal=false
Categories=Office;
```

---

## Preserving wiki-linux Features in i3

### 1. Wallpaper & Background

i3 has no built-in wallpaper manager. Use `feh` to set background:

```bash
# Add to ~/.config/i3/config
exec_always --no-startup-id \
  feh --bg-fill /home/sourov/wiki/_meta/wallpaper.png

# Or generate fresh wallpaper on each login:
exec --no-startup-id ~/.local/bin/wiki-wallpaper-gen && \
  feh --bg-fill /home/sourov/wiki/_meta/wallpaper.png
```

### 2. Notifications & Reminders

i3 relies on **dunst** for notifications. Configure it:

```bash
mkdir -p ~/.config/dunst
cat > ~/.config/dunst/dunstrc <<'EOF'
[global]
    monitor = 0
    follow = mouse
    geometry = "300x5-10+10"
    indicate_hidden = yes
    shrink = no
    transparency = 0
    notification_height = 0
    separator_height = 2
    padding = 8
    horizontal_padding = 8
    frame_width = 2
    frame_color = "#888888"
    separator_color = frame
    sort = yes
    idle_threshold = 120

[urgency_low]
    background = "#222222"
    foreground = "#888888"
    timeout = 10

[urgency_normal]
    background = "#1e1e1e"
    foreground = "#ffffff"
    timeout = 10

[urgency_critical]
    background = "#900000"
    foreground = "#ffffff"
    timeout = 0
EOF
```

### 3. Auto-sync & File Monitoring

These already run as systemd user services and will work in i3 without changes:

```bash
# Verify they're still active after switching to i3
systemctl --user status wiki-monitor.service
systemctl --user status wiki-sync.timer
systemctl --user status wiki-system-maintenance.timer
```

### 4. Startup Scripts

Create a script to launch all wiki tools on i3 startup:

```bash
cat > ~/.config/i3/startup.sh <<'EOF'
#!/bin/bash
# Launch wiki-linux services on i3 startup

# Start file monitor
systemctl --user start wiki-monitor.service

# Start notification daemon
dunst -config ~/.config/dunst/dunstrc &

# Start compositor for smooth rendering
picom -f &

# Set background
feh --bg-fill ~/wiki/_meta/wallpaper.png

# Start wiki status reminder (optional)
# systemctl --user start wiki-sticky-reminder.service

echo "Wiki-Linux i3 startup complete"
EOF

chmod +x ~/.config/i3/startup.sh
```

Add to `~/.config/i3/config`:
```ini
exec_always --no-startup-id ~/.config/i3/startup.sh
```

---

## Memory & Performance Optimization

### i3 vs XFCE/KDE

| Metric | XFCE | KDE | i3 |
|--------|------|-----|-----|
| Base memory | ~300MB | ~450MB | ~30MB |
| Idle CPU | 3-5% | 5-8% | <1% |
| Responsiveness | Good | Good | Excellent |
| Customization | Limited | Extensive | Extensive |

### Recommended Lightweight Alternatives

```bash
# Instead of XFCE Terminal → use Alacritty or xterm
sudo apt install alacritty

# Instead of XFCE file manager → use PCManFM or ranger
sudo apt install pcmanfm ranger

# Instead of Evolution/Thunderbird → use mutt or web-based
# (Keep browser for OpenWebUI)

# Disable these heavy services
systemctl --user mask \
  tracker-extract-3.service \
  tracker-miner-fs-3.service \
  gvfs-udisks2-volume-monitor.service
```

---

## Switching to i3: Step-by-Step

### 1. Test First (Recommended)

```bash
# Option A: Virtual Machine
# Spin up a Debian/Ubuntu VM and test i3 config there first

# Option B: Live USB
# Boot from a live i3 desktop ISO to try it out

# Option C: Single Session (On Current Machine)
# Log out, select i3 session at login screen, test, then log back to XFCE/KDE
```

### 2. Install & Configure

```bash
# 1. Install packages
sudo apt install -y i3-wm i3status dmenu feh picom dunst

# 2. Log out and select i3 at login
# (If no i3 option, restart display manager: systemctl restart display-manager)

# 3. First login will generate ~/.config/i3/config
# Modify it per the recommendations above

# 4. Reload i3: Super+Shift+R
```

### 3. Verify wiki-linux Still Works

```bash
# After first i3 login, verify:
curl http://127.0.0.1:8080 -s | head -c 50  # OpenWebUI
curl http://127.0.0.1:11434/api/tags -s      # Ollama
ls ~/wiki/user/ | head -5                     # Wiki root
systemctl --user list-timers | grep wiki      # Timers
```

### 4. Migrate Completely (Optional)

Once confident:

```bash
# Remove the old DE (keep as backup initially)
# sudo apt remove xfce4 kde-plasma-desktop

# Make i3 the default on logout
# (Usually in login screen settings)
```

---

## Troubleshooting i3 Migration

### "i3 won't start"
```bash
# Check X server
echo $DISPLAY

# Verify i3 installation
i3 --version

# Check for config errors
i3 -C  # Validates ~/.config/i3/config
```

### "Services aren't running"
```bash
# After logging into i3, manually start them:
systemctl --user restart wiki-monitor.service
systemctl --user restart wiki-sync.timer

# Check logs
journalctl --user -u wiki-monitor.service -n 20
```

### "Wallpaper isn't showing"
```bash
# Ensure feh is installed
which feh || sudo apt install feh

# Test wallpaper manually
feh --bg-fill ~/wiki/_meta/wallpaper.png

# Verify i3 config has: exec_always --no-startup-id feh...
grep "feh" ~/.config/i3/config
```

### "OpenWebUI not accessible"
```bash
# Check if service is running
systemctl --user status wiki-openwebui.service

# Restart it
systemctl --user restart wiki-openwebui.service

# Test endpoint
curl http://127.0.0.1:8080 -v
```

### "Keyboard shortcuts not working"
```bash
# Reload i3 config: Super+Shift+R

# Check for config syntax errors
i3 -C

# See active keybindings
i3-msg -t get_config | grep bindsym | head -20
```

---

## Rollback Plan

If i3 doesn't work out, fallback is simple:

```bash
# 1. Log out from i3
# 2. At login screen, select XFCE (or KDE)
# 3. All settings preserved; nothing lost

# To completely remove i3 (if needed):
# sudo apt remove i3-wm i3status dmenu
```

---

## Post-Migration Maintenance

### Daily Checks in i3

Create a simple monitoring script:

```bash
cat > ~/.local/bin/wiki-i3-check <<'EOF'
#!/bin/bash
echo "=== Wiki-Linux + i3 Status ==="
echo
echo "Disk:"
df -h / | tail -1 | awk '{print "  Used: " $3 " / " $2 " (" $5 ")"}'
echo
echo "Memory:"
free -h | grep Mem | awk '{print "  Used: " $3 " / " $2}'
echo
echo "Services:"
systemctl --user is-active wiki-monitor.service wiki-sync.timer wiki-system-maintenance.timer
echo
echo "OpenWebUI:"
curl -s http://127.0.0.1:8080/api/health | grep -q "ok" && echo "  ✓ Running" || echo "  ✗ Down"
echo
echo "Last sync:"
cd ~/wiki && git log -1 --pretty=format:"  %ai %s"
EOF

chmod +x ~/.local/bin/wiki-i3-check

# Bind to Super+H in i3
# bindsym $mod+h exec xterm -e ~/.local/bin/wiki-i3-check
```

### Weekly Cleanup

```bash
# Keep i3 lightweight — periodically check:
systemctl --user list-timers
systemctl --user list-units --type=service --state=running
du -sh ~/.cache/*
```

---

## Reference Documentation

After migrating to i3, keep these docs accessible:

1. **[KDE-DESIGN-PREP.md](KDE-DESIGN-PREP.md)** — System architecture overview
2. **[SYSTEM-ARCHITECTURE.md](SYSTEM-ARCHITECTURE.md)** — Karpathy 3-layer design
3. **[MAINTENANCE-GUIDE.md](../MAINTENANCE-GUIDE.md)** — System maintenance (unchanged)
4. **[MAINTENANCE-RULES-TINY.md](../MAINTENANCE-RULES-TINY.md)** — i3 is tiny-friendly!
5. **[i3 Official Docs](https://i3wm.org/docs/)** — Keybindings, configuration reference

---

## Summary

| Step | Action | Impact |
|------|--------|--------|
| Install i3 | `sudo apt install i3-wm` | Adds lightweight WM |
| Test in session | Log into i3 before committing | Low risk |
| Configure | Add wiki-linux keybindings & services | Enables workflows |
| Mask unused services | `systemctl --user mask wiki-wallpaper.timer` | Frees ~50MB memory |
| Verify systems | `curl http://localhost:8080` | Confirms operation |
| Daily use | Use Super keybindings for wiki tools | Seamless workflow |

---

## Final Checklist Before Committing to i3

- [ ] i3 installed and tested
- [ ] i3 config created at `~/.config/i3/config`
- [ ] Wiki keybindings added (Super+O, Super+W, etc.)
- [ ] OpenWebUI, Ollama, wiki monitor all responsive
- [ ] Disk space healthy (`df -h /` ≥ 10GB)
- [ ] Maintenance timers active (`systemctl --user list-timers`)
- [ ] Wallpaper set with `feh` or `wiki-wallpaper-gen`
- [ ] Notifications working (dunst daemon running)
- [ ] Startup script created and integrated
- [ ] Old DE (XFCE/KDE) kept as fallback

---

**Good luck with i3!** Keep this guide bookmarked for reference during and after migration. The system is designed to work equally well in i3, XFCE, KDE, or any other environment.
