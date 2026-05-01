# 🌞 Brightness Troubleshooting Quick Guide

## 🚨 Issue: No Brightness Slider Visible

### Quick Fixes to Try First:

1. **Check Function Keys**
   - Try `Fn + F5/F6` or `Fn + Up/Down` arrow keys
   - Look for sun icons on your keyboard

2. **Check System Settings**
   - GNOME: Settings → Power → Brightness
   - KDE: System Settings → Power Management
   - XFCE: Settings → Power Manager → Display

3. **Install brightnessctl**
   ```bash
   sudo pacman -S brightnessctl
   brightnessctl set 50%  # Set to 50% brightness
   ```

### Common Solutions:

#### If `/sys/class/backlight/` is empty:
```bash
# Try loading backlight modules
sudo modprobe video
sudo modprobe backlight

# Check for alternative brightness controls
find /sys/devices/ -name '*brightness*'
```

#### For permission issues:
```bash
# Add user to video group
sudo usermod -aG video $USER

# Create udev rule for non-root access
echo 'ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness"' | sudo tee /etc/udev/rules.d/90-backlight.rules
echo 'ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness"' | sudo tee -a /etc/udev/rules.d/90-backlight.rules
sudo udevadm control --reload-rules
```

### Advanced Troubleshooting:

1. **Check loaded modules:**
   ```bash
   lsmod | grep -E 'video|backlight|acpi'
   ```

2. **Check Xorg logs:**
   ```bash
   cat /var/log/Xorg.0.log | grep -i brightness
   ```

3. **Try kernel parameters:**
   - Add `acpi_backlight=vendor` or `acpi_backlight=native` to GRUB
   - Edit `/etc/default/grub` and run `sudo update-grub`

### Quick Brightness Control Script:

```bash
#!/bin/bash
# Create as ~/bin/brightness and make executable

MAX=$(cat /sys/class/backlight/*/max_brightness)
CURRENT=$(cat /sys/class/backlight/*/brightness)

case "$1" in
    up) NEW=$((CURRENT + MAX/10));;
    down) NEW=$((CURRENT - MAX/10));;
    *) echo "Usage: brightness {up|down}"; exit 1;;
esac

[[ $NEW -gt $MAX ]] && NEW=$MAX
[[ $NEW -lt 0 ]] && NEW=0
echo $NEW | sudo tee /sys/class/backlight/*/brightness
```

### Related Resources:
- [[system/brightness-control]] - Full brightness control guide
- Check your specific laptop model + "Linux brightness" online
- Consider external tools like `redshift` for eye comfort

> 💡 **Tip**: If you're using a desktop with external monitors, check the monitor's physical buttons for brightness control.