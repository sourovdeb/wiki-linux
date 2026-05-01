#!/usr/bin/env bash
# install-udev.sh — installs the HDD backup udev rule (requires sudo)
#
# Run once: sudo bash etc/install-udev.sh

set -euo pipefail
RULE_SRC="$(cd "$(dirname "$0")" && pwd)/udev-wiki-hdd-backup.rules"
RULE_DEST="/etc/udev/rules.d/99-wiki-hdd-backup.rules"

echo "Installing udev rule for HDD backup popup..."
cp "$RULE_SRC" "$RULE_DEST"
udevadm control --reload-rules
echo "✓ Rule installed at $RULE_DEST"
echo "Now enable the service:"
echo "  systemctl --user enable --now wiki-hdd-backup.service"
