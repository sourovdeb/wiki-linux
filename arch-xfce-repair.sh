#!/bin/bash
# arch-xfce-repair.sh
# Arch Linux XFCE/LightDM comprehensive diagnostic and auto-repair
# Covers: home mount, .local symlink race, pam_systemd, stale locks,
#         fstab corruption, systemd ordering, .dmrc, package integrity
# Usage: sudo bash arch-xfce-repair.sh
# Fetch:  sudo bash <(curl -fsSL https://raw.githubusercontent.com/YOURUSER/YOURREPO/main/arch-xfce-repair.sh)

LOG="/root/arch-repair-$(date +%Y%m%d-%H%M%S).txt"
USER_NAME="sourov"
USER_ID="1000"
PASS=0
FAIL=0
FIXED=0

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
BLU='\033[0;34m'
RST='\033[0m'

log()     { echo "$1" | tee -a "$LOG"; }
pass()    { echo -e "${GRN}[PASS]${RST}  $1" | tee -a "$LOG"; ((PASS++)); }
fail()    { echo -e "${RED}[FAIL]${RST}  $1" | tee -a "$LOG"; ((FAIL++)); }
fixed()   { echo -e "${YLW}[FIXED]${RST} $1" | tee -a "$LOG"; ((FIXED++)); }
info()    { echo -e "${BLU}[INFO]${RST}  $1" | tee -a "$LOG"; }
section() { log ""; log "════════════════════════════════════════"; log "  $1"; log "════════════════════════════════════════"; }

if [ "$EUID" -ne 0 ]; then
    echo "Run as root: sudo bash arch-xfce-repair.sh"
    exit 1
fi

log "========================================"
log "ARCH XFCE REPAIR — $(date)"
log "User: $USER_NAME  UID: $USER_ID"
log "Log: $LOG"
log "========================================"


# ─────────────────────────────────────────
# SECTION 1: MOUNTS
# ─────────────────────────────────────────
section "SECTION 1: MOUNTS"

if mountpoint -q /home; then
    pass "/home is mounted"
else
    info "/home not mounted — mounting now"
    if mount /home 2>>"$LOG"; then
        fixed "/home mounted successfully"
    else
        fail "/home failed to mount — check LVM and fstab UUID"
    fi
fi

if mountpoint -q /mnt/sourov-database; then
    pass "/mnt/sourov-database is mounted"
else
    info "/mnt/sourov-database not mounted — mounting now"
    if mount /mnt/sourov-database 2>>"$LOG"; then
        fixed "/mnt/sourov-database mounted successfully"
    else
        fail "/mnt/sourov-database failed to mount — nofail will skip at boot"
    fi
fi

log ""
info "Current relevant mounts:"
mount | grep -E "home|sourov|mnt" | tee -a "$LOG" || true


# ─────────────────────────────────────────
# SECTION 2: HOME DIRECTORY PERMISSIONS
# ─────────────────────────────────────────
section "SECTION 2: PERMISSIONS"

HOME_DIR="/home/$USER_NAME"

if [ ! -d "$HOME_DIR" ]; then
    fail "$HOME_DIR does not exist — /home may not be mounted"
else
    OWNER=$(stat -c '%U' "$HOME_DIR")
    PERMS=$(stat -c '%a' "$HOME_DIR")
    info "$HOME_DIR  owner=$OWNER  perms=$PERMS"

    if [ "$OWNER" != "$USER_NAME" ]; then
        chown "$USER_NAME:$USER_NAME" "$HOME_DIR"
        fixed "Ownership corrected on $HOME_DIR"
    else
        pass "$HOME_DIR ownership correct"
    fi

    if [ "$PERMS" != "700" ]; then
        chmod 700 "$HOME_DIR"
        fixed "Permissions corrected to 700 on $HOME_DIR"
    else
        pass "$HOME_DIR permissions correct (700)"
    fi
fi


# ─────────────────────────────────────────
# SECTION 3: STALE LOCKS AND SOCKETS
# ─────────────────────────────────────────
section "SECTION 3: STALE LOCKS"

if ls /home/$USER_NAME/.Xauthority* 2>/dev/null | grep -q .; then
    rm -f /home/$USER_NAME/.Xauthority*
    fixed "Removed stale .Xauthority files"
else
    pass "No stale .Xauthority files"
fi

if ls /tmp/.X*-lock 2>/dev/null | grep -q .; then
    rm -f /tmp/.X*-lock
    fixed "Removed /tmp/.X*-lock files"
else
    pass "No /tmp X lock files"
fi

if ls /tmp/.X11-unix/X* 2>/dev/null | grep -q .; then
    rm -f /tmp/.X11-unix/X*
    fixed "Removed stale X11 unix sockets"
else
    pass "No stale X11 unix sockets"
fi


# ─────────────────────────────────────────
# SECTION 4: .local SYMLINK
# ─────────────────────────────────────────
section "SECTION 4: .local SYMLINK"

LOCAL="$HOME_DIR/.local"

if [ -L "$LOCAL" ]; then
    TARGET=$(readlink "$LOCAL")
    info ".local is a symlink pointing to: $TARGET"

    if [ -d "$TARGET" ]; then
        pass "Symlink target exists and is accessible"
        mkdir -p "$TARGET/share/xorg"
        TOWNER=$(stat -c '%U' "$TARGET")
        if [ "$TOWNER" != "$USER_NAME" ]; then
            chown -R "$USER_NAME:$USER_NAME" "$TARGET"
            fixed "Ownership corrected on symlink target"
        else
            pass "Symlink target ownership correct"
        fi
    else
        fail "CRITICAL: Symlink target $TARGET is not accessible"
        info "Emergency fallback: replacing broken symlink with real directory"
        rm "$LOCAL"
        mkdir -p "$LOCAL/share/xorg"
        chown -R "$USER_NAME:$USER_NAME" "$LOCAL"
        fixed ".local replaced with real directory (data from database partition disconnected)"
    fi
elif [ -d "$LOCAL" ]; then
    pass ".local is a real directory"
    mkdir -p "$LOCAL/share/xorg"
    chown -R "$USER_NAME:$USER_NAME" "$LOCAL"
else
    info ".local does not exist — creating"
    mkdir -p "$LOCAL/share/xorg"
    chown -R "$USER_NAME:$USER_NAME" "$LOCAL"
    fixed "Created $LOCAL/share/xorg"
fi


# ─────────────────────────────────────────
# SECTION 5: REQUIRED PACKAGES
# ─────────────────────────────────────────
section "SECTION 5: PACKAGE INTEGRITY"

MISSING_PKGS=()
for pkg in xorg-server xfce4-session xfwm4 xfdesktop xfce4-panel \
           lightdm lightdm-gtk-greeter pam; do
    if pacman -Q "$pkg" &>/dev/null; then
        VER=$(pacman -Q "$pkg" | awk '{print $2}')
        pass "$pkg $VER"
    else
        fail "MISSING: $pkg"
        MISSING_PKGS+=("$pkg")
    fi
done

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    info "Installing missing packages: ${MISSING_PKGS[*]}"
    if pacman -Sy --noconfirm "${MISSING_PKGS[@]}" 2>>"$LOG"; then
        fixed "Installed: ${MISSING_PKGS[*]}"
    else
        fail "Package installation failed — check network and pacman"
    fi
fi


# ─────────────────────────────────────────
# SECTION 6: PAM CONFIGURATION
# ─────────────────────────────────────────
section "SECTION 6: PAM CONFIGURATION"

info "--- /etc/pam.d/lightdm ---"
cat /etc/pam.d/lightdm 2>/dev/null | tee -a "$LOG" || fail "/etc/pam.d/lightdm not found"

info "--- pam_systemd check in /etc/pam.d/system-login ---"
if grep -q "pam_systemd" /etc/pam.d/system-login 2>/dev/null; then
    pass "pam_systemd present in /etc/pam.d/system-login"
else
    fail "pam_systemd NOT found in /etc/pam.d/system-login — XDG_RUNTIME_DIR will not be created on login"
    info "Reinstalling pam package to restore default PAM configuration"
    if pacman -S --noconfirm pam 2>>"$LOG"; then
        fixed "pam package reinstalled"
        if grep -q "pam_systemd" /etc/pam.d/system-login 2>/dev/null; then
            pass "pam_systemd now present after reinstall"
        else
            fail "pam_systemd still missing after reinstall — manual intervention required"
        fi
    else
        fail "pam reinstall failed"
    fi
fi


# ─────────────────────────────────────────
# SECTION 7: FSTAB VALIDATION AND REPAIR
# ─────────────────────────────────────────
section "SECTION 7: FSTAB"

info "Current /etc/fstab:"
cat /etc/fstab | tee -a "$LOG"

FSTAB_NEEDS_FIX=0

if grep -q "But problems persist" /etc/fstab; then
    fail "CORRUPTED OPTIONS in /etc/fstab — text injected into options field"
    FSTAB_NEEDS_FIX=1
fi

if ! grep -E "^\s*UUID.*\s/home\s" /etc/fstab | grep -q "x-systemd.automount"; then
    fail "/home entry missing x-systemd.automount"
    FSTAB_NEEDS_FIX=1
fi

if grep -E "^\s*LABEL=Sourov-database" /etc/fstab | grep -q "x-systemd.automount"; then
    fail "Sourov-database has x-systemd.automount — causes .local symlink race condition"
    FSTAB_NEEDS_FIX=1
fi

if grep -E "^\s*UUID=EB9F-E3D2" /etc/fstab | grep -qE "\bsync\b|\bflush\b"; then
    fail "exFAT entry has invalid options (sync/flush) for in-kernel exfat driver"
    FSTAB_NEEDS_FIX=1
fi

if [ "$FSTAB_NEEDS_FIX" -eq 1 ]; then
    BACKUP="/root/fstab.backup.$(date +%Y%m%d-%H%M%S)"
    cp /etc/fstab "$BACKUP"
    info "Backed up current fstab to $BACKUP"

    cat > /etc/fstab << 'FSTAB'
# <file system>                                 <dir>                 <type>  <options>                                                                                               <dump> <pass>

# Root — LVM
UUID=035d3e52-0a9f-43aa-8b68-845cb9401cfc       /                     ext4    rw,noatime,commit=30                                                                                    0      1

# Home — LVM, automount ensures availability before session services
UUID=226abcde-7690-4011-aec2-cd3f4ead9dbf       /home                 ext4    rw,noatime,commit=30,x-systemd.automount,x-systemd.device-timeout=30                                   0      2

# Boot — EFI vfat
UUID=3C03-6C50                                  /boot                 vfat    rw,noatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro    0      2

# Database — direct mount, no automount (required for .local symlink resolution before display-manager)
LABEL=Sourov-database                           /mnt/sourov-database  ext4    defaults,noatime,nofail,x-systemd.device-timeout=30,x-gvfs-show                                        0      0

# Swap
/swapfile                                       none                  swap    defaults                                                                                                0      0

# exFAT storage
UUID=EB9F-E3D2                                  /mnt/sourov-exfat     exfat   defaults,uid=1000,gid=1000,umask=022,noatime,nofail,x-systemd.device-timeout=30,x-gvfs-show            0      0
FSTAB

    if findmnt --verify 2>>"$LOG"; then
        fixed "fstab rewritten and verified — backup at $BACKUP"
    else
        fail "fstab verify failed after rewrite — restoring backup"
        cp "$BACKUP" /etc/fstab
        fail "Backup restored — manual correction required"
    fi
else
    pass "fstab has no detected issues"
fi


# ─────────────────────────────────────────
# SECTION 8: SYSTEMD DISPLAY-MANAGER OVERRIDE
# ─────────────────────────────────────────
section "SECTION 8: SYSTEMD ORDERING OVERRIDE"

OVERRIDE_DIR="/etc/systemd/system/display-manager.service.d"
OVERRIDE_FILE="$OVERRIDE_DIR/require-database.conf"

mkdir -p "$OVERRIDE_DIR"

NEEDS_OVERRIDE=0
if [ ! -f "$OVERRIDE_FILE" ]; then
    fail "Override file missing: $OVERRIDE_FILE"
    NEEDS_OVERRIDE=1
elif ! grep -q "mnt-sourov" "$OVERRIDE_FILE"; then
    fail "Override file exists but content is incorrect"
    NEEDS_OVERRIDE=1
else
    pass "display-manager.service override exists with correct content"
fi

if [ "$NEEDS_OVERRIDE" -eq 1 ]; then
    printf '[Unit]\nAfter=mnt-sourov\\x2ddatabase.mount\nWants=mnt-sourov\\x2ddatabase.mount\n' > "$OVERRIDE_FILE"
    fixed "Written $OVERRIDE_FILE"
fi

info "Override file content:"
cat "$OVERRIDE_FILE" | tee -a "$LOG"


# ─────────────────────────────────────────
# SECTION 9: LIGHTDM SESSION CONFIGURATION
# ─────────────────────────────────────────
section "SECTION 9: LIGHTDM SESSION"

info "Available sessions:"
ls /usr/share/xsessions/ 2>/dev/null | tee -a "$LOG" || fail "No sessions in /usr/share/xsessions/"

if [ -f /usr/share/xsessions/xfce.desktop ]; then
    SESSION_NAME="xfce"
    pass "xfce.desktop found"
elif [ -f /usr/share/xsessions/xfce4.desktop ]; then
    SESSION_NAME="xfce4"
    pass "xfce4.desktop found"
else
    fail "No XFCE session desktop file found"
    SESSION_NAME="xfce"
fi

cat > "$HOME_DIR/.dmrc" << DMRC
[Desktop]
Session=$SESSION_NAME
DMRC
chown "$USER_NAME:$USER_NAME" "$HOME_DIR/.dmrc"
chmod 644 "$HOME_DIR/.dmrc"
fixed "Written $HOME_DIR/.dmrc — Session=$SESSION_NAME"

info "--- /etc/lightdm/lightdm.conf (active lines only) ---"
grep -v "^#" /etc/lightdm/lightdm.conf 2>/dev/null | grep -v "^$" | tee -a "$LOG" \
    || fail "lightdm.conf not found"


# ─────────────────────────────────────────
# SECTION 10: RUNTIME DIRECTORY STATE
# ─────────────────────────────────────────
section "SECTION 10: XDG_RUNTIME_DIR STATE"

info "/run/user contents:"
ls -la /run/user/ 2>/dev/null | tee -a "$LOG" || info "/run/user is empty"

if [ -d "/run/user/$USER_ID" ]; then
    pass "/run/user/$USER_ID exists"
else
    info "/run/user/$USER_ID absent — expected before login; pam_systemd creates it on successful login"
fi


# ─────────────────────────────────────────
# SECTION 11: LIGHTDM LOG
# ─────────────────────────────────────────
section "SECTION 11: LIGHTDM LOG"

if [ -f /var/log/lightdm/lightdm.log ]; then
    pass "LightDM log exists"
    info "--- Last 60 lines ---"
    tail -60 /var/log/lightdm/lightdm.log | tee -a "$LOG"
else
    fail "No LightDM log at /var/log/lightdm/lightdm.log"
fi


# ─────────────────────────────────────────
# SECTION 12: JOURNAL ERRORS
# ─────────────────────────────────────────
section "SECTION 12: JOURNAL ERRORS"

info "--- systemd journal errors this boot ---"
journalctl -b -p err --no-pager 2>/dev/null | tail -40 | tee -a "$LOG" \
    || info "journalctl unavailable"


# ─────────────────────────────────────────
# FINAL SUMMARY AND RESTART
# ─────────────────────────────────────────
section "FINAL SUMMARY"

echo -e "${GRN}PASS${RST}  : $PASS" | tee -a "$LOG"
echo -e "${YLW}FIXED${RST} : $FIXED" | tee -a "$LOG"
echo -e "${RED}FAIL${RST}  : $FAIL" | tee -a "$LOG"
log ""
log "Full report saved to: $LOG"
log ""

systemctl daemon-reload

if [ "$FAIL" -eq 0 ]; then
    log "No unresolved failures — restarting LightDM"
    systemctl restart lightdm
else
    log "Unresolved failures detected."
    log "Review: cat $LOG"
    log "Then restart manually: sudo systemctl restart lightdm"
fi
