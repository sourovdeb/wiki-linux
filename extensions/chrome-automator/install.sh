#!/usr/bin/env bash
# install.sh — Set up the Wiki Automator server
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$SCRIPT_DIR/server"

echo "=== Wiki Automator Server Setup ==="

# Python venv
if [[ ! -d "$SERVER_DIR/.venv" ]]; then
  python3 -m venv "$SERVER_DIR/.venv"
  echo "Created venv at $SERVER_DIR/.venv"
fi

# Install dependencies
"$SERVER_DIR/.venv/bin/pip" install -q -r "$SERVER_DIR/requirements.txt"
echo "Python deps installed"

# Install Playwright browsers (Chromium)
"$SERVER_DIR/.venv/bin/playwright" install chromium
echo "Playwright Chromium installed"

# Generate placeholder icons (best effort; existing icons are already bundled)
python3 - <<'PYEOF'
import os

try:
    from PIL import Image, ImageDraw
except Exception:
    print("Pillow not installed; skipping icon generation.")
    raise SystemExit(0)

icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(icons_dir, exist_ok=True)

for size in [16, 48, 128]:
    img = Image.new("RGBA", (size, size), (2, 132, 199, 255))
    d = ImageDraw.Draw(img)
    margin = size // 5
    d.rectangle([margin, margin, size - margin, size - margin], fill=(255, 255, 255, 200))
    img.save(os.path.join(icons_dir, f"icon{size}.png"))
    print(f"  icon{size}.png created")
PYEOF
echo "Icons generated"

# Create systemd service for autostart (optional)
SERVICE_FILE="$HOME/.config/systemd/user/wiki-automator.service"
mkdir -p "$(dirname "$SERVICE_FILE")"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Wiki Automator Server
After=network.target

[Service]
Type=simple
WorkingDirectory=$SERVER_DIR
ExecStart=$SERVER_DIR/.venv/bin/python server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable wiki-automator
echo "systemd service installed: wiki-automator"
echo ""
echo "=== Done ==="
echo "Load the extension in Chrome/Chromium:"
echo "  chrome://extensions/ → Developer mode → Load unpacked → $SCRIPT_DIR"
echo ""
echo "Start the server manually:"
echo "  cd $SERVER_DIR && .venv/bin/python server.py"
echo ""
echo "Or start via systemd:"
echo "  systemctl --user start wiki-automator"
