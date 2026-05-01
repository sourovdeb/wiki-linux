#!/usr/bin/env bash
# install.sh — Idempotent installer for Wiki-OS.
#
# This script can be run multiple times safely. It checks for each
# dependency and skips steps that are already complete. It never requires
# sudo except for pacman installs; all service setup uses systemctl --user.
#
# Usage: bash install.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/wiki-linux"
CONFIG_FILE="$CONFIG_DIR/config.json"
SYSTEMD_DIR="$HOME/.config/systemd/user"
WIKI_ROOT="$HOME/wiki"
VENV="$PROJECT_ROOT/.venv"

# ── Colours ───────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}!${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*" >&2; exit 1; }
step() { echo -e "\n${YELLOW}▶${NC} $*"; }

# ── Uninstall ─────────────────────────────────────────────────────────────────
uninstall() {
  step "Uninstalling wiki-linux"
  systemctl --user stop wiki-monitor.service wiki-sync.timer
  systemctl --user disable wiki-monitor.service wiki-sync.timer
  rm -f "$SYSTEMD_DIR/wiki-monitor.service"
  rm -f "$SYSTEMD_DIR/wiki-sync.service"
  rm -f "$SYSTEMD_DIR/wiki-sync.timer"
  systemctl --user daemon-reload
  ok "Systemd units removed"

  rm -rf "$CONFIG_DIR"
  ok "Config directory removed: $CONFIG_DIR"

  # We don't remove the wiki itself, just the code and config.
  warn "The wiki at $WIKI_ROOT has not been touched."
  warn "To remove it, delete the directory manually."

  ok "Uninstall complete."
  exit 0
}

# ── Reconfigure ───────────────────────────────────────────────────────────────
reconfigure() {
  step "Reconfiguring wiki-linux"
  rm -f "$CONFIG_FILE"
  ok "Removed config file: $CONFIG_FILE"
  # The rest of the script will now run as if it's a first install.
}


# --- Main install logic ---
if [[ "${1:-}" == "--uninstall" ]]; then
  uninstall
fi
if [[ "${1:-}" == "--reconfigure" ]]; then
  reconfigure
fi

# ── 1. System packages ────────────────────────────────────────────────────────
step "Checking system packages"

PACMAN_PKGS=(git ripgrep glow ollama)
MISSING_PKGS=()
for pkg in "${PACMAN_PKGS[@]}"; do
  if ! pacman -Qi "$pkg" &>/dev/null; then
    MISSING_PKGS+=("$pkg")
  else
    ok "$pkg already installed"
  fi
done

if [[ ${#MISSING_PKGS[@]} -gt 0 ]]; then
  warn "Installing: ${MISSING_PKGS[*]}"
  sudo pacman -Sy --needed --noconfirm "${MISSING_PKGS[@]}"
  ok "System packages installed"
fi

# mdt is AUR-only; check for yay/paru.
if ! command -v mdt &>/dev/null; then
  if command -v yay &>/dev/null; then
    warn "Installing md-tui-bin (AUR) via yay..."
    yay -S --needed --noconfirm md-tui-bin
  elif command -v paru &>/dev/null; then
    warn "Installing md-tui-bin (AUR) via paru..."
    paru -S --needed --noconfirm md-tui-bin
  else
    warn "mdt not found and no AUR helper available."
    warn "Install md-tui manually: https://github.com/henriklovhaug/md-tui"
    warn "Or: cargo install md-tui"
  fi
else
  ok "mdt already installed"
fi

# Check if Ollama is running (non-fatal — may not be installed on this OS)
step "Checking Ollama service"
if command -v ollama &>/dev/null; then
  if ollama ps &>/dev/null 2>&1; then
    ok "Ollama is running."
  else
    warn "Ollama is installed but not running."
    warn "Start it with: systemctl --user enable --now ollama"
    warn "Then pull your model: ollama pull mistral"
  fi
else
  warn "Ollama not found. Install from https://ollama.com"
  warn "After install, run: ollama pull mistral"
fi

# ── 2. Python virtual environment ─────────────────────────────────────────────
step "Setting up Python virtual environment"

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
  ok "Virtual environment created at $VENV"
else
  ok "Virtual environment already exists"
fi

"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet \
  "ollama>=0.4.0" \
  "inotify_simple>=1.3" \
  "pyyaml>=6.0" \
  "jinja2>=3.1"

ok "Python dependencies installed"

# ── 3. Configuration ──────────────────────────────────────────────────────────
step "Setting up configuration"

mkdir -p "$CONFIG_DIR"

if [[ -f "$CONFIG_FILE" ]]; then
  ok "Config already exists at $CONFIG_FILE"
else
  cp "$PROJECT_ROOT/config.json" "$CONFIG_FILE"
  # Patch WIKI_ROOT to use the actual home directory path.
  sed -i "s|~/wiki|$WIKI_ROOT|g" "$CONFIG_FILE"
  chmod 0444 "$CONFIG_FILE"  # lock per EXPECTATIONS Guarantee 1
  ok "Config copied to $CONFIG_FILE (read-only — use --reconfigure to edit)"
  warn "Review $CONFIG_FILE and adjust ollama.model, git.remote, etc."
  warn "To edit: bash install.sh --reconfigure"
fi

# ── 4. Wiki directory structure ───────────────────────────────────────────────
step "Creating wiki directory structure"

mkdir -p \
  "$WIKI_ROOT/system/config" \
  "$WIKI_ROOT/system/logs" \
  "$WIKI_ROOT/system/docs" \
  "$WIKI_ROOT/user/notes" \
  "$WIKI_ROOT/user/projects" \
  "$WIKI_ROOT/user/research" \
  "$WIKI_ROOT/_meta" \
  "$WIKI_ROOT/_meta/tasks" \
  "$WIKI_ROOT/_tmp" \
  "$WIKI_ROOT/_archive"

ok "Wiki structure created at $WIKI_ROOT"

# Initialise git repo if not already done.
if [[ ! -d "$WIKI_ROOT/.git" ]]; then
  git -C "$WIKI_ROOT" init -b main
  echo "_tmp/" > "$WIKI_ROOT/.gitignore"
  echo "*.log"  >> "$WIKI_ROOT/.gitignore"
  git -C "$WIKI_ROOT" add .gitignore
  git -C "$WIKI_ROOT" commit -m "init: wiki-linux initial commit"
  ok "Git repository initialised in $WIKI_ROOT"
else
  ok "Git repository already exists"
fi

# Create an Obsidian vault settings stub so Obsidian recognises the directory.
OBSIDIAN_DIR="$WIKI_ROOT/.obsidian"
if [[ ! -d "$OBSIDIAN_DIR" ]]; then
  mkdir -p "$OBSIDIAN_DIR"
  cat > "$OBSIDIAN_DIR/app.json" <<'JSON'
{
  "legacyEditor": false,
  "livePreview": true,
  "defaultViewMode": "preview",
  "attachmentFolderPath": "_tmp"
}
JSON
  ok "Obsidian vault stub created"
fi

# ── 5. systemd user services ──────────────────────────────────────────────────
step "Installing systemd user services"

mkdir -p "$SYSTEMD_DIR"

for unit in wiki-monitor.service wiki-sync.service wiki-sync.timer; do
  cp "$PROJECT_ROOT/systemd/$unit" "$SYSTEMD_DIR/$unit"
  # Patch the placeholder path to the actual project root.
  # Source files use %h/wiki-linux; the repo may live anywhere under $HOME.
  sed -i "s|%h/wiki-linux|$PROJECT_ROOT|g" "$SYSTEMD_DIR/$unit"
  ok "Installed $unit → patched paths to $PROJECT_ROOT"
done

systemctl --user daemon-reload
ok "systemd daemon reloaded"

# ── 6. CLI symlink ────────────────────────────────────────────────────────────
step "Installing wiki CLI"

LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"
chmod +x "$PROJECT_ROOT/bin/wiki"

if [[ -L "$LOCAL_BIN/wiki" ]]; then
  ok "wiki symlink already exists"
else
  ln -s "$PROJECT_ROOT/bin/wiki" "$LOCAL_BIN/wiki"
  ok "Symlinked bin/wiki → $LOCAL_BIN/wiki"
fi

# Warn if ~/.local/bin is not in PATH.
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
  warn "$LOCAL_BIN is not in your PATH."
  warn "Add this to ~/.bashrc or ~/.zshrc:"
  warn "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# ── 7. Ollama model ───────────────────────────────────────────────────────────
step "Checking Ollama model"

# Read the configured model from config.
MODEL="$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    c = json.load(f)
print(c.get('ollama', {}).get('model', 'mistral'))
" 2>/dev/null || echo "mistral")"

if systemctl is-active --quiet ollama; then
  if ollama list 2>/dev/null | grep -q "^${MODEL}"; then
    ok "Model '$MODEL' is already pulled"
  else
    warn "Pulling model '$MODEL' (this may take several minutes)..."
    ollama pull "$MODEL"
    ok "Model '$MODEL' pulled"
  fi
else
  warn "Ollama service is not running."
  warn "Start it with: systemctl enable --now ollama"
  warn "Then pull your model: ollama pull $MODEL"
fi

# ── 8. Done ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN} wiki-linux installation complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "  1. Enable services:"
echo "       systemctl --user enable --now wiki-monitor"
echo "       systemctl --user enable --now wiki-sync.timer"
echo ""
echo "  2. Try the wiki:"
echo "       wiki status"
echo "       wiki new \"My first page\""
echo "       wiki ask \"What does my pacman.conf do?\""
echo ""
echo "  3. Open in Obsidian (optional):"
echo "       obsidian $WIKI_ROOT"
echo ""
echo "  4. Check the daemon log:"
echo "       journalctl --user -u wiki-monitor -f"
