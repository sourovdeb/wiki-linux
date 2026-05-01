# 🌞 Brightness Control on Linux

## 📋 Overview

This guide explains how to control screen brightness on Linux systems, including troubleshooting when brightness sliders are missing or not working.

## 🔍 Common Brightness Control Methods

### 1. **Function Keys (Primary Method)**
- Most laptops have dedicated function keys for brightness control
- Typically `Fn + F5/F6` or `Fn + Up/Down` arrow keys
- Look for sun/screen icons on your function keys

### 2. **System Settings GUI**
- **GNOME**: Settings → Power → Brightness slider
- **KDE**: System Settings → Power Management → Energy Saving
- **XFCE**: Settings → Power Manager → Display tab

### 3. **Terminal Commands**

#### Check available brightness controls:
```bash
ls /sys/class/backlight/
```

#### View current brightness (0-max_value):
```bash
cat /sys/class/backlight/*/brightness
```

#### Set brightness (replace 500 with desired value):
```bash
echo 500 | sudo tee /sys/class/backlight/*/brightness
```

#### Find maximum brightness value:
```bash
cat /sys/class/backlight/*/max_brightness
```

### 4. **Command Line Tools**

Install brightness control utilities:
```bash
# For Arch Linux
sudo pacman -S brightnessctl

# For Debian/Ubuntu
sudo apt install brightnessctl
```

**Usage:**
```bash
# Increase brightness by 10%
brightnessctl set +10%

# Decrease brightness by 10%
brightnessctl set 10%-

# Set to 50% brightness
brightnessctl set 50%
```

## ⚠️ Troubleshooting Missing Brightness Slider

### Issue: No brightness slider in system settings

#### Common Causes:
1. **Missing backlight driver**
2. **Incorrect graphics driver**
3. **ACPI issues**
4. **Permission problems**

#### Solutions:

1. **Check if backlight interface exists:**
```bash
ls /sys/class/backlight/
```
   - If empty, your system may not have proper backlight support

2. **Check kernel modules:**
```bash
lsmod | grep -E 'video|backlight|acpi'
```

3. **Try loading backlight modules:**
```bash
sudo modprobe video
sudo modprobe backlight
```

4. **Check for alternative brightness controls:**
```bash
find /sys/class/backlight/ -name '*brightness*'
find /sys/devices/ -name '*brightness*'
```

5. **Check Xorg configuration:**
```bash
cat /var/log/Xorg.0.log | grep -i brightness
```

## 🛠️ Advanced Solutions

### 1. **Manual Brightness Control Script**

Create a script to control brightness:
```bash
#!/bin/bash
# Save as ~/bin/brightness

MAX_BRIGHTNESS=$(cat /sys/class/backlight/*/max_brightness)
CURRENT=$(cat /sys/class/backlight/*/brightness)

case "$1" in
    up)
        NEW=$((CURRENT + MAX_BRIGHTNESS/10))
        [[ $NEW -gt $MAX_BRIGHTNESS ]] && NEW=$MAX_BRIGHTNESS
        ;;
    down)
        NEW=$((CURRENT - MAX_BRIGHTNESS/10))
        [[ $NEW -lt 0 ]] && NEW=0
        ;;
    *)
        echo "Usage: $0 {up|down}"
        exit 1
        ;;
esac

echo $NEW | sudo tee /sys/class/backlight/*/brightness
```

Make it executable:
```bash
chmod +x ~/bin/brightness
```

### 2. **udev Rules for Non-root Access**

Create a udev rule to allow brightness control without sudo:
```bash
sudo nano /etc/udev/rules.d/90-backlight.rules
```

Add this content:
```
ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness"
ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness"
```

Then reload udev:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Add your user to the video group:
```bash
sudo usermod -aG video $USER
```

### 3. **Graphics Driver Solutions**

#### For Intel graphics:
```bash
sudo pacman -S xf86-video-intel
```

#### For NVIDIA graphics:
```bash
sudo pacman -S nvidia nvidia-utils nvidia-settings
```

#### For AMD graphics:
```bash
sudo pacman -S xf86-video-amdgpu
```

## 💡 Additional Tips

1. **Check your desktop environment settings** - Some DEs hide brightness controls
2. **Try different kernel parameters** - Add `acpi_backlight=vendor` or `acpi_backlight=native` to GRUB
3. **Check BIOS/UEFI settings** - Some systems disable brightness control in firmware
4. **Use external tools** like `redshift` for color temperature adjustment

## 🔗 Related Topics

- [[power-management]] - General power management settings
- [[graphics-drivers]] - Graphics driver configuration
- [[kernel-parameters]] - Boot parameter configuration

## 📝 Notes

If you're still having issues with brightness control, it may be helpful to:
1. Check your specific hardware model's Linux compatibility
2. Search for solutions for your particular laptop model
3. Consider using external monitor brightness controls if available