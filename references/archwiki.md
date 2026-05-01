# 📚 Arch Wiki Reference Guide

## 🌞 Brightness Control (Arch Wiki Summary)

### Basic Brightness Control

**Check available backlight devices:**
```bash
ls /sys/class/backlight/
```

**View current brightness:**
```bash
cat /sys/class/backlight/*/brightness
```

**Set brightness (requires root):**
```bash
echo 500 | sudo tee /sys/class/backlight/*/brightness
```

### Backlight Utilities

**Install brightnessctl:**
```bash
sudo pacman -S brightnessctl
```

**Usage:**
```bash
# Increase by 10%
brightnessctl set +10%

# Decrease by 10%
brightnessctl set 10%-

# Set to specific percentage
brightnessctl set 50%

# Get info
brightnessctl info
```

### udev Rules for Non-root Access

Create `/etc/udev/rules.d/backlight.rules`:
```
ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness"
ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness"
```

Then reload udev:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Add user to video group:
```bash
sudo usermod -aG video $USER
```

### Kernel Parameters

For systems with backlight issues, try adding to kernel command line:

- `acpi_backlight=vendor`
- `acpi_backlight=native`
- `acpi_backlight=video`

Edit `/etc/default/grub` and run `sudo update-grub` after changes.

### Graphics Driver Specific Solutions

**Intel:**
```bash
sudo pacman -S xf86-video-intel
```

**NVIDIA:**
```bash
sudo pacman -S nvidia nvidia-utils nvidia-settings
```

**AMD:**
```bash
sudo pacman -S xf86-video-amdgpu
```

### Xorg Configuration

Check Xorg logs for backlight issues:
```bash
grep -i backlight /var/log/Xorg.0.log
```

### Alternative Methods

**xbacklight (for Xorg with Intel drivers):**
```bash
sudo pacman -S xorg-xbacklight
xbacklight -set 50
```

**ddcutil (for external monitors):**
```bash
sudo pacman -S ddcutil
ddcutil setvcp 10 50  # Set brightness to 50
```

## 🔧 General Arch Linux Troubleshooting

### Pacman Package Management

**Update system:**
```bash
sudo pacman -Syu
```

**Search packages:**
```bash
pacman -Ss search_term
```

**Install packages:**
```bash
sudo pacman -S package_name
```

### Systemd Services

**Enable service:**
```bash
sudo systemctl enable service_name
```

**Start service:**
```bash
sudo systemctl start service_name
```

**Check status:**
```bash
sudo systemctl status service_name
```

### Journalctl Logs

**View system logs:**
```bash
journalctl -xe
```

**Follow logs:**
```bash
journalctl -f
```

**Filter by service:**
```bash
journalctl -u service_name
```

## 📂 Arch Wiki Online Resources

- **Official Arch Wiki**: https://wiki.archlinux.org/
- **Brightness Control**: https://wiki.archlinux.org/title/backlight
- **Intel Graphics**: https://wiki.archlinux.org/title/Intel_graphics
- **NVIDIA**: https://wiki.archlinux.org/title/NVIDIA
- **AMD Graphics**: https://wiki.archlinux.org/title/AMDGPU

## 💡 Arch Linux Best Practices

1. **Regular updates**: `sudo pacman -Syu`
2. **Check for orphaned packages**: `pacman -Qdt`
3. **Clean package cache**: `pacman -Sc
4. **Use AUR helper**: `yay` or `paru` for AUR packages
5. **Backup configurations**: `/etc/` files before major changes

## 🔗 Related Wiki Pages

- [[system/brightness-control]] - Local brightness control guide
- [[user/notes/brightness-troubleshooting]] - Quick troubleshooting
- [[system/power-management]] - Power management settings