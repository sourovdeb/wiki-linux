#!/usr/bin/env bash
# install_linux.sh — Install wiki_ingestor as a systemd user service on Linux/Arch
# Usage: bash install_linux.sh [--uninstall]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="wiki-ingestor"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/$SERVICE_NAME.service"
VENV_DIR="$SCRIPT_DIR/.venv"
WIKI_DIR="$HOME/wiki"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[info]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[warn]${NC}  $*"; }
error() { echo -e "${RED}[error]${NC} $*" >&2; exit 1; }

# Uninstall
if [[ "${1:-}" == "--uninstall" ]]; then
    info "Stopping and disabling $SERVICE_NAME..."
    systemctl --user stop  "$SERVICE_NAME" 2>/dev/null || true
    systemctl --user disable "$SERVICE_NAME" 2>/dev/null || true
    rm -f "$SERVICE_FILE"
    systemctl --user daemon-reload
    info "Uninstalled. Virtualenv kept at $VENV_DIR"
    exit 0
fi

# Prerequisites
command -v python3 &>/dev/null || error "python3 not found. Install it first."
python3 -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10+ required'" || error "Python 3.10 or higher is required."

# Virtual environment
if [[ ! -d "$VENV_DIR" ]]; then
    info "Creating virtualenv at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

info "Installing/upgrading dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet markitdown[all] watchdog openai

# Default config
mkdir -p "$WIKI_DIR"
CONFIG="$WIKI_DIR/wiki_ingestor_config.json"

WIKI_LINUX_CONFIG="$HOME/.config/wiki-linux/config.json"
if [[ -f "$WIKI_LINUX_CONFIG" ]]; then
    info "Found wiki-linux config at $WIKI_LINUX_CONFIG"
    info "wiki_ingestor will automatically use its watch_dirs setting"
fi

if [[ ! -f "$CONFIG" ]]; then
    info "Writing default config to $CONFIG..."
    "$VENV_DIR/bin/python" -m wiki_ingestor init
else
    warn "Config already exists at $CONFIG — not overwriting."
fi

# systemd user service
mkdir -p "$SERVICE_DIR"
cat > "$SERVICE_FILE" <<'SERVICEEOF'
[Unit]
Description=wiki_ingestor — MarkItDown file-to-Markdown daemon
After=network.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/python -m wiki_ingestor watch
WorkingDirectory=$SCRIPT_DIR
Restart=on-failure
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
SERVICEEOF

systemctl --user daemon-reload
systemctl --user enable  "$SERVICE_NAME"
systemctl --user start   "$SERVICE_NAME"

info "Service status:"
systemctl --user status "$SERVICE_NAME" --no-pager || true

echo ""
info "wiki_ingestor is running as a systemd user service."
info "  Logs  : journalctl --user -u $SERVICE_NAME -f"
info "  Stop  : systemctl --user stop $SERVICE_NAME"
info "  Config: $CONFIG"
info "  Output: $WIKI_DIR/converted/"
