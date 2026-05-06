#!/usr/bin/env bash
# cleanup-keep-policy.sh
# Enforces the wiki-linux keep/remove policy:
#   KEEP: Chromium, Chrome-related, Python deps, fonts, essential tools
#   DISABLE: autoupdate, tracker, packagekit, bluetooth (if unused), avahi
#   REMOVE: nothing is force-removed — script only DISABLES or MASKS services
#           and prints a removal candidate list for manual review.
# Run as regular user (no root required for service ops; sudo only for pacman).
set -euo pipefail

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          Wiki-Linux Keep/Remove Policy Enforcer              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── SECTION 1: KEEP LIST (packages that must remain) ──────────────────────────
KEEP_PACKAGES=(
  # Browsers
  chromium
  firefox
  # Python
  python
  python-pip
  python-pipx
  # Fonts
  noto-fonts
  ttf-liberation
  ttf-dejavu
  ttf-inconsolata
  adobe-source-code-pro-fonts
  adobe-source-sans-fonts
  ttf-cantarell
  # Essential system tools
  base-devel
  git
  curl
  wget
  ripgrep
  jq
  vim
  neovim
  bash
  zsh
  coreutils
  # Wiki-linux stack
  ollama
  obsidian
  code
  # Audio/transcription
  python-openai-whisper
  ffmpeg
  # Desktop
  xfce4
  xfce4-goodies
  xfce4-terminal
  thunar
  # Fonts rendering
  freetype2
  fontconfig
  cairo
)

# ── SECTION 2: SERVICES TO DISABLE (autoupdate / clutter) ─────────────────────
DISABLE_SYSTEM=(
  packagekit.service
  packagekit.socket
  ModemManager.service
  geoclue.service
  avahi-daemon.service
  avahi-daemon.socket
  bluetooth.service
)

MASK_USER=(
  tracker-extract-3.service
  tracker-miner-fs-3.service
  tracker-miner-fs-control-3.service
  tracker-miner-rss-3.service
  tracker-writeback-3.service
  evolution-source-registry.service
  evolution-calendar-factory.service
  evolution-addressbook-factory.service
  goa-daemon.service
  gvfs-goa-volume-monitor.service
)

# ── SECTION 3: PACKAGES TO REVIEW (print only, no auto-remove) ────────────────
REVIEW_PACKAGES=(
  # These are candidates for removal — review and run pacman -Rns manually
  libreoffice-fresh
  libreoffice-still
  gnome-software
  pamac-gtk
  pamac-cli
  discover
  baobab
  gnome-disk-utility
  cheese
  rhythmbox
  totem
  shotwell
  simple-scan
  orca
  speech-dispatcher
  brltty
)

echo "=== KEEP LIST (will not be touched) ==="
for p in "${KEEP_PACKAGES[@]}"; do
  state=$(pacman -Qi "$p" 2>/dev/null | grep -m1 "^Version" | awk '{print $3}' || echo "not installed")
  printf "  %-40s %s\n" "$p" "$state"
done

echo ""
echo "=== SYSTEM SERVICES TO DISABLE ==="
for s in "${DISABLE_SYSTEM[@]}"; do
  state=$(systemctl is-enabled "$s" 2>/dev/null || echo "absent")
  printf "  %-45s %s\n" "$s" "$state"
done

echo ""
echo "=== USER SERVICES TO MASK ==="
for s in "${MASK_USER[@]}"; do
  state=$(systemctl --user is-enabled "$s" 2>/dev/null || echo "absent")
  printf "  %-50s %s\n" "$s" "$state"
done

echo ""
echo "=== PACKAGES TO REVIEW FOR REMOVAL (not auto-removed) ==="
for p in "${REVIEW_PACKAGES[@]}"; do
  if pacman -Qi "$p" &>/dev/null; then
    echo "  INSTALLED  $p  (run: sudo pacman -Rns $p)"
  else
    echo "  absent     $p"
  fi
done

echo ""
echo "=== AUTOUPDATE STATUS ==="
for svc in packagekit pamac-daemon dnf-automatic unattended-upgrades apt-daily; do
  st=$(systemctl is-enabled "$svc" 2>/dev/null || systemctl is-enabled "${svc}.service" 2>/dev/null || echo "absent")
  printf "  %-35s %s\n" "$svc" "$st"
done

echo ""
read -rp "Apply: disable system services + mask user services? [y/N] " ans
[[ "$ans" =~ ^[Yy]$ ]] || { echo "Aborted — nothing changed."; exit 0; }

echo ""
echo "Disabling system services (requires sudo)..."
for s in "${DISABLE_SYSTEM[@]}"; do
  if systemctl is-enabled "$s" &>/dev/null; then
    sudo systemctl disable --now "$s" 2>/dev/null && echo "  disabled: $s" || echo "  skip: $s"
  fi
done

echo ""
echo "Masking user services..."
for s in "${MASK_USER[@]}"; do
  systemctl --user mask "$s" 2>/dev/null && echo "  masked: $s" || echo "  skip: $s"
done

echo ""
echo "✓ Policy enforced."
echo "  Review packages printed above must be removed manually with: sudo pacman -Rns <name>"
echo "  Run 'systemd-analyze blame | head -20' to verify boot time improved."
