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

PACMAN_PKGS=(git ripgrep glow ollama yad libnotify)
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
  ok "Obsidian vault directory created"
fi

# Copy Obsidian config templates (only if not already customised).
OBSIDIAN_TMPL="$PROJECT_ROOT/templates/obsidian"
for tmpl_file in app.json workspace.json community-plugins.json; do
  dest="$OBSIDIAN_DIR/$tmpl_file"
  if [[ ! -f "$dest" ]]; then
    cp "$OBSIDIAN_TMPL/$tmpl_file" "$dest"
    ok "Installed Obsidian $tmpl_file"
  else
    ok "Obsidian $tmpl_file already exists — skipping"
  fi
done

# CSS snippet for Arch Wiki link highlighting.
mkdir -p "$OBSIDIAN_DIR/snippets"
if [[ ! -f "$OBSIDIAN_DIR/snippets/wiki-linux.css" ]]; then
  cp "$OBSIDIAN_TMPL/snippets/wiki-linux.css" "$OBSIDIAN_DIR/snippets/wiki-linux.css"
  ok "Installed Obsidian CSS snippet (wiki-linux.css)"
fi

# Enable the CSS snippet in appearance.json.
APPEARANCE="$OBSIDIAN_DIR/appearance.json"
if [[ ! -f "$APPEARANCE" ]]; then
  cat > "$APPEARANCE" <<'JSON'
{
  "enabledCssSnippets": ["wiki-linux"],
  "cssTheme": "",
  "baseFontSize": 15,
  "textFontFamily": "",
  "monospaceFontFamily": ""
}
JSON
  ok "Enabled wiki-linux CSS snippet in Obsidian"
fi

# ── Obsidian community plugins (download from GitHub releases) ───────────────
step "Installing Obsidian community plugins"

PLUGIN_DIR="$OBSIDIAN_DIR/plugins"
mkdir -p "$PLUGIN_DIR"

# Map: plugin-id → GitHub owner/repo
declare -A PLUGIN_REPOS=(
  ["obsidian-git"]="denolehov/obsidian-git"
  ["dataview"]="blacksmithgu/obsidian-dataview"
  ["templater-obsidian"]="SilentVoid13/Templater"
)

for plugin_id in "${!PLUGIN_REPOS[@]}"; do
  repo="${PLUGIN_REPOS[$plugin_id]}"
  plugin_dest="$PLUGIN_DIR/$plugin_id"

  if [[ -f "$plugin_dest/main.js" ]]; then
    ok "Plugin $plugin_id already installed"
    continue
  fi

  warn "Fetching plugin $plugin_id from $repo..."
  mkdir -p "$plugin_dest"

  # Get the latest release download URL for main.js via GitHub API.
  api_url="https://api.github.com/repos/${repo}/releases/latest"
  release_json=$(curl -fsSL --max-time 15 "$api_url" 2>/dev/null || echo "")

  if [[ -z "$release_json" ]]; then
    warn "Could not reach GitHub API for $plugin_id — skipping"
    continue
  fi

  for asset in main.js manifest.json styles.css; do
    asset_url=$(echo "$release_json" \
      | python3 -c "
import sys, json
data = json.load(sys.stdin)
for a in data.get('assets', []):
    if a['name'] == sys.argv[1]:
        print(a['browser_download_url'])
        break
" "$asset" 2>/dev/null || true)

    if [[ -n "$asset_url" ]]; then
      curl -fsSL --max-time 30 -o "$plugin_dest/$asset" "$asset_url" 2>/dev/null \
        && ok "  Downloaded $plugin_id/$asset" \
        || warn "  Could not download $plugin_id/$asset"
    fi
  done

  # Copy plugin-specific settings template if present.
  TMPL_DATA="$OBSIDIAN_TMPL/plugins/$plugin_id/data.json"
  if [[ -f "$TMPL_DATA" && ! -f "$plugin_dest/data.json" ]]; then
    cp "$TMPL_DATA" "$plugin_dest/data.json"
    ok "  Applied default settings for $plugin_id"
  fi
done

# Register the Obsidian global vault so it opens ~/wiki at first launch.
OBSIDIAN_GLOBAL_CFG="$HOME/.config/obsidian/obsidian.json"
mkdir -p "$(dirname "$OBSIDIAN_GLOBAL_CFG")"
if [[ ! -f "$OBSIDIAN_GLOBAL_CFG" ]]; then
  ts_ms=$(date +%s%3N)
  cat > "$OBSIDIAN_GLOBAL_CFG" <<JSON
{
  "vaults": {
    "wiki": {
      "path": "$WIKI_ROOT",
      "ts": $ts_ms,
      "open": true
    }
  }
}
JSON
  ok "Registered ~/wiki as Obsidian vault in $OBSIDIAN_GLOBAL_CFG"
else
  ok "Obsidian global config already exists — vault registration skipped"
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
chmod +x "$PROJECT_ROOT/bin/wiki-notify"
chmod +x "$PROJECT_ROOT/bin/wiki-welcome"
chmod +x "$PROJECT_ROOT/bin/wiki-launcher"
chmod +x "$PROJECT_ROOT/bin/wiki-search-widget"

for _bin in wiki wiki-notify wiki-welcome wiki-launcher wiki-search-widget; do
  if [[ -L "$LOCAL_BIN/$_bin" ]]; then
    ok "$_bin symlink already exists"
  else
    ln -s "$PROJECT_ROOT/bin/$_bin" "$LOCAL_BIN/$_bin"
    ok "Symlinked bin/$_bin → $LOCAL_BIN/$_bin"
  fi
done

# wiki-welcome autostart
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"
if [[ -f "$AUTOSTART_DIR/wiki-welcome.desktop" ]]; then
  ok "wiki-welcome autostart already exists"
else
  cat > "$AUTOSTART_DIR/wiki-welcome.desktop" << DESKTOP
[Desktop Entry]
Type=Application
Name=Wiki-Linux Welcome
Comment=Shows wiki-linux quick-start popup at login
Exec=$LOCAL_BIN/wiki-welcome
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-XFCE-Autostart-Override=true
DESKTOP
  ok "Created wiki-welcome autostart entry"
fi

# wiki-launcher desktop file (panel shortcut / app-menu entry).
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"
if [[ -f "$DESKTOP_DIR/wiki-launcher.desktop" ]]; then
  ok "wiki-launcher.desktop already exists"
else
  cat > "$DESKTOP_DIR/wiki-launcher.desktop" << DESKTOP
[Desktop Entry]
Type=Application
Name=wiki-linux Launcher
GenericName=Wiki Launcher
Comment=Open the wiki-linux command grid
Exec=$LOCAL_BIN/wiki-launcher
Icon=accessories-text-editor
Terminal=false
Categories=Utility;Education;
Keywords=wiki;notes;knowledge;obsidian;llm;
StartupNotify=false
DESKTOP
  ok "Created wiki-launcher.desktop in $DESKTOP_DIR"
fi

# wiki-search-widget desktop file (bind to Super+W or similar).
if [[ -f "$DESKTOP_DIR/wiki-search-widget.desktop" ]]; then
  ok "wiki-search-widget.desktop already exists"
else
  cat > "$DESKTOP_DIR/wiki-search-widget.desktop" << DESKTOP
[Desktop Entry]
Type=Application
Name=wiki-linux Search
GenericName=Wiki LLM Search
Comment=Ask your wiki a question using the local LLM
Exec=$LOCAL_BIN/wiki-search-widget
Icon=system-search
Terminal=false
Categories=Utility;Education;
Keywords=wiki;search;llm;ask;notes;
StartupNotify=false
DESKTOP
  ok "Created wiki-search-widget.desktop in $DESKTOP_DIR"
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
echo "  2. Try the wiki CLI:"
echo "       wiki status"
echo "       wiki new \"My first page\""
echo "       wiki ask \"What does my pacman.conf do?\""
echo "       wiki fix \"wifi not connecting\""
echo "       wiki archwiki \"Network configuration\""
echo ""
echo "  3. Open the desktop launcher (grid of all wiki commands):"
echo "       wiki-launcher"
echo "     Or search via the floating LLM widget:"
echo "       wiki-search-widget"
echo "     (Bind either to a keyboard shortcut, e.g. Super+W)"
echo ""
echo "  4. Open in Obsidian:"
echo "       obsidian $WIKI_ROOT"
echo "     Community plugins installed: obsidian-git, dataview, templater"
echo "     Enable plugins inside Obsidian: Settings → Community plugins → Enable"
echo ""
echo "  5. Check the daemon log:"
echo "       journalctl --user -u wiki-monitor -f"
