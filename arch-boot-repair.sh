#!/bin/bash
# arch-boot-repair.sh
# Repairs systemd-boot entry and initramfs for Arch Linux
# Adds systemd.unified_cgroup_hierarchy=1 to fix ERFKILL session creation failure
# Usage: sudo bash arch-boot-repair.sh

LOG="/root/arch-boot-repair-$(date +%Y%m%d-%H%M%S).txt"

log()   { echo "$1" | tee -a "$LOG"; }
info()  { echo "[INFO]  $1" | tee -a "$LOG"; }
pass()  { echo "[PASS]  $1" | tee -a "$LOG"; }
fail()  { echo "[FAIL]  $1" | tee -a "$LOG"; }
fixed() { echo "[FIXED] $1" | tee -a "$LOG"; }

if [ "$EUID" -ne 0 ]; then
    echo "Run as root: sudo bash arch-boot-repair.sh"
    exit 1
fi

log "========================================"
log "ARCH BOOT REPAIR — $(date)"
log "========================================"

# --- SECTION 1: MOUNT BOOT ---
log ""
log "--- SECTION 1: BOOT PARTITION ---"
if mountpoint -q /boot; then
    pass "/boot is mounted"
else
    info "Mounting /boot"
    if mount /boot 2>>"$LOG"; then
        fixed "/boot mounted"
    else
        fail "/boot failed to mount — cannot continue"
        exit 1
    fi
fi

log ""
info "Contents of /boot:"
ls /boot | tee -a "$LOG"

# --- SECTION 2: DETECT KERNEL AND MICROCODE ---
log ""
log "--- SECTION 2: KERNEL AND MICROCODE DETECTION ---"

VMLINUZ=""
if [ -f /boot/vmlinuz-linux ]; then
    VMLINUZ="/vmlinuz-linux"
    pass "Kernel found: vmlinuz-linux"
else
    fail "vmlinuz-linux not found in /boot"
    exit 1
fi

MICROCODE=""
if [ -f /boot/intel-ucode.img ]; then
    MICROCODE="initrd  /intel-ucode.img"
    pass "Intel microcode found"
elif [ -f /boot/amd-ucode.img ]; then
    MICROCODE="initrd  /amd-ucode.img"
    pass "AMD microcode found"
else
    info "No microcode image found — skipping"
fi

# --- SECTION 3: REGENERATE INITRAMFS ---
log ""
log "--- SECTION 3: INITRAMFS ---"

if [ -f /boot/initramfs-linux.img ]; then
    pass "initramfs-linux.img exists"
else
    info "initramfs-linux.img missing — regenerating"
    if mkinitcpio -p linux 2>>"$LOG"; then
        fixed "initramfs regenerated"
    else
        fail "mkinitcpio failed — check $LOG"
        exit 1
    fi
fi

if [ ! -f /boot/initramfs-linux-fallback.img ]; then
    info "Fallback initramfs missing — regenerating all presets"
    mkinitcpio -P 2>>"$LOG" && fixed "All initramfs images regenerated"
fi

# --- SECTION 4: ROOT UUID ---
log ""
log "--- SECTION 4: ROOT UUID ---"

ROOT_UUID=$(findmnt -n -o UUID /)
if [ -z "$ROOT_UUID" ]; then
    ROOT_UUID="035d3e52-0a9f-43aa-8b68-845cb9401cfc"
    info "Could not detect root UUID dynamically — using known UUID from fstab"
else
    pass "Root UUID detected: $ROOT_UUID"
fi

# --- SECTION 5: WRITE BOOT ENTRY ---
log ""
log "--- SECTION 5: SYSTEMD-BOOT ENTRY ---"

ENTRY="/boot/loader/entries/arch.conf"

if [ -f "$ENTRY" ] && [ -s "$ENTRY" ]; then
    cp "$ENTRY" "${ENTRY}.backup.$(date +%Y%m%d-%H%M%S)"
    info "Backed up existing arch.conf"
fi

cat > "$ENTRY" << BOOTENTRY
title   Arch Linux
linux   $VMLINUZ
$MICROCODE
initrd  /initramfs-linux.img
options root=UUID=$ROOT_UUID rw nouveau.modeset=0 nvidia-drm.modeset=1 snd-intel-dspcfg.dsp_driver=1 systemd.unified_cgroup_hierarchy=1
BOOTENTRY

pass "Written $ENTRY"
log ""
info "Final arch.conf content:"
cat "$ENTRY" | tee -a "$LOG"

# --- SECTION 6: LOADER.CONF ---
log ""
log "--- SECTION 6: LOADER.CONF ---"

cat > /boot/loader/loader.conf << LOADERCONF
timeout 3
default arch.conf
console-mode keep
LOADERCONF

fixed "Written /boot/loader/loader.conf"
cat /boot/loader/loader.conf | tee -a "$LOG"

# --- SECTION 7: VERIFY ---
log ""
log "--- SECTION 7: BOOTCTL STATUS ---"
bootctl status 2>>"$LOG" | head -20 | tee -a "$LOG" || info "bootctl not available"

# --- DONE ---
log ""
log "========================================"
log "COMPLETE — report saved to $LOG"
log "========================================"
log ""
log "Rebooting in 5 seconds..."
sleep 5
reboot
