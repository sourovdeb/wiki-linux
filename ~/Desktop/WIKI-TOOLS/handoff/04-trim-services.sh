#!/bin/bash
# 04-trim-services.sh
# Disable unnecessary services (user-level only)

set -euo pipefail

echo "✂️  Trimming unnecessary services..."

# Services to disable (user-level only)
SERVICES_TO_DISABLE=(
    "bluetooth.service"
    "cups.service"
    "tracker-miner-fs-3.service"
    "tracker-miner-rss-3.service"
    "tracker-store.service"
    "tracker-miner-apps-3.service"
    "tracker-extract-3.service"
)

# Services to keep (DO NOT DISABLE)
PROTECTED_SERVICES=(
    "wiki-monitor.service"
    "ollama.service"
    "NetworkManager.service"
)

echo "🔍 Checking current service status..."

# Disable unnecessary services
for service in "${SERVICES_TO_DISABLE[@]}"; do
    if systemctl --user is-enabled "$service" 2>/dev/null; then
        echo "🚫 Disabling $service..."
        systemctl --user disable "$service"
        systemctl --user stop "$service"
    else
        echo "✅ $service already disabled or not found"
    fi
done

# Verify protected services are still running
for service in "${PROTECTED_SERVICES[@]}"; do
    if systemctl --user is-enabled "$service" 2>/dev/null; then
        echo "🛡️  $service protected and active"
    else
        echo "⚠️  $service not found (may be system-level)"
    fi
done

# Clean up old service files
echo "🧹 Cleaning up old service files..."
find ~/.config/systemd/user -name "*.service~" -delete 2>/dev/null || true
find ~/.config/systemd/user -name "*.socket~" -delete 2>/dev/null || true

# Reload systemd user daemon
echo "🔄 Reloading systemd user daemon..."
systemctl --user daemon-reload

echo "✅ Service trimming complete!"
echo ""
echo "Disabled services:"
for service in "${SERVICES_TO_DISABLE[@]}"; do
    echo "  - $service"
done
echo ""
echo "Protected services (still active):"
for service in "${PROTECTED_SERVICES[@]}"; do
    echo "  - $service"
done