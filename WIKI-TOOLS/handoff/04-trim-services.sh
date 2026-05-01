#!/usr/bin/env bash
# Disable non-essential background services. Review before answering 'y'.
set -euo pipefail

NONESSENTIAL_SYSTEM=(
  bluetooth.service
  cups.service
  cups.socket
  ModemManager.service
  packagekit.service
  geoclue.service
  avahi-daemon.service
  systemd-timesyncd.service  # NetworkManager handles this
)
NONESSENTIAL_USER=(
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

echo "=== System services to disable ==="
for s in "${NONESSENTIAL_SYSTEM[@]}"; do
  state=$(systemctl is-enabled "$s" 2>/dev/null || echo "absent")
  printf "  %-40s %s\n" "$s" "$state"
done

echo
echo "=== User services to mask ==="
for s in "${NONESSENTIAL_USER[@]}"; do
  state=$(systemctl --user is-enabled "$s" 2>/dev/null || echo "absent")
  printf "  %-45s %s\n" "$s" "$state"
done

echo
read -rp "Proceed with disabling these? [y/N] " ans
[[ "$ans" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

for s in "${NONESSENTIAL_SYSTEM[@]}"; do
  sudo systemctl disable --now "$s" 2>/dev/null || true
done
for s in "${NONESSENTIAL_USER[@]}"; do
  systemctl --user mask "$s" 2>/dev/null || true
done

echo
echo "✓ Done. Verify load: systemd-analyze blame | head -20"
