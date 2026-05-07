# MACOS_AGENT_TASKS.md — Concrete Setup Steps for macOS Agents

> Companion to **WIKI_AGENT.md**. The agent reads `WIKI_AGENT.md` first for
> the philosophy and invariants, then this file for the actual macOS shell
> commands. Targets macOS 13 Ventura and newer (works on Apple Silicon and
> Intel).

---

## Pre-Flight Checks

The agent MUST verify before doing anything:

```bash
# 1. Confirm macOS version
sw_vers -productVersion

# 2. Confirm we're not running as root
[ "$EUID" -ne 0 ] || { echo "Do not run as root"; exit 1; }

# 3. Confirm Homebrew is available (install if not)
command -v brew >/dev/null 2>&1 || /bin/bash -c \
  "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 4. Confirm Xcode Command Line Tools
xcode-select --print-path >/dev/null 2>&1 || xcode-select --install
```

If any check fails, the agent stops and reports the failure — it does NOT
silently proceed.

---

## Phase 1 — Vault Initialisation

```bash
# Create vault structure
WIKI_ROOT="$HOME/wiki"
mkdir -p "$WIKI_ROOT"/{system,user/{notes,projects,research},_meta,_tmp,raw}
mkdir -p "$WIKI_ROOT"/system/{config,docs,logs}

# Initialise git
cd "$WIKI_ROOT"
git init -b main
cat > .gitignore <<'EOF'
_tmp/
*.log
.DS_Store
.obsidian/workspace.json
.obsidian/workspace-mobile.json
EOF
git add .gitignore
git commit -m "init: vault initialised by wiki agent"
```

---

## Phase 2 — Tool Installation

```bash
# Core tools — agent installs all
brew install git ripgrep glow ollama

# Optional but recommended
brew install --cask obsidian
brew install terminal-notifier   # for wiki-notify with action buttons

# Start Ollama service
brew services start ollama

# Pull the chosen model (default: mistral, ~4GB)
ollama pull mistral
```

Agent confirms each install succeeded:

```bash
for cmd in git rg glow ollama; do
  command -v "$cmd" >/dev/null && echo "✓ $cmd" || echo "✗ $cmd MISSING"
done
```

---

## Phase 3 — Vault Display & Discovery (macOS-Specific)

Unlike Linux's XDG dirs, macOS uses fixed `~/Documents`, `~/Downloads`, etc.
The agent does NOT rename these (Spotlight, iCloud, and Finder rely on them).
Instead, the agent makes the wiki **first-class in Finder**:

```bash
# 1. Add ~/wiki to Finder sidebar (uses sfltool, available since macOS 10.11)
# Note: requires user confirmation — Finder may prompt
mysides add "Wiki" "file://$HOME/wiki/" 2>/dev/null || \
  brew install mysides && mysides add "Wiki" "file://$HOME/wiki/"

# 2. Tag the wiki folder with a colour for visibility
xattr -w com.apple.metadata:_kMDItemUserTags '("Wiki\n6")' "$HOME/wiki"

# 3. Pin to Dock (optional — adds wiki folder as Dock stack)
defaults write com.apple.dock persistent-others -array-add \
  "<dict><key>tile-data</key><dict><key>file-data</key><dict>\
  <key>_CFURLString</key><string>file://$HOME/wiki/</string>\
  <key>_CFURLStringType</key><integer>15</integer></dict></dict></dict>"
killall Dock
```

---

## Phase 4 — Obsidian Integration

```bash
# Register the vault with Obsidian (creates the ~/Library/Application Support entry)
OBSIDIAN_CONFIG="$HOME/Library/Application Support/obsidian"
mkdir -p "$OBSIDIAN_CONFIG"

# Add vault to Obsidian's known list
python3 - <<EOF
import json, os, hashlib, time
from pathlib import Path

config = Path.home() / "Library/Application Support/obsidian/obsidian.json"
config.parent.mkdir(parents=True, exist_ok=True)

vault_path = str(Path.home() / "wiki")
vault_id = hashlib.md5(vault_path.encode()).hexdigest()[:16]

data = {}
if config.exists():
    data = json.loads(config.read_text())

data.setdefault("vaults", {})[vault_id] = {
    "path": vault_path,
    "ts": int(time.time() * 1000),
    "open": True,
}

config.write_text(json.dumps(data, indent=2))
print(f"✓ Registered vault: {vault_path}")
EOF

# Also register the URI scheme so obsidian://open?vault=wiki works
defaults write com.apple.LaunchServices LSHandlers -array-add \
  '{LSHandlerURLScheme="obsidian";LSHandlerRoleAll="md.obsidian";}'
```

---

## Phase 5 — Tool Audit (Bloatware Check)

The agent scans for unused apps and **proposes** removals — never auto-removes:

```bash
# List all user-installed apps (excludes Apple system apps)
mdfind "kMDItemKind == 'Application' && kMDItemAppStoreCategory != ''" 2>/dev/null

# Common macOS bloat candidates the agent may propose:
#   - GarageBand (~2GB)
#   - iMovie (~3GB)
#   - Trial software left from previous installations
#   - Adware browser extensions
#
# Agent presents them in JSON proposal format from WIKI_AGENT.md and
# WAITS for user confirmation. Never executes `sudo rm -rf /Applications/*`.
```

JSON proposal example the agent emits:

```json
{
  "action": "uninstall",
  "target": "/Applications/GarageBand.app",
  "size_freed_mb": 2048,
  "reason": "User confirmed they don't make music",
  "reversible": true,
  "reverse_command": "Reinstall via App Store (free)"
}
```

---

## Phase 6 — Daemon Setup (LaunchAgent, Not systemd)

macOS uses `launchd`, not `systemd`. The agent creates a LaunchAgent:

```bash
PLIST="$HOME/Library/LaunchAgents/com.wikilinux.monitor.plist"
mkdir -p "$(dirname "$PLIST")"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.wikilinux.monitor</string>
  <key>ProgramArguments</key>
  <array>
    <string>$HOME/wiki-linux/.venv/bin/python3</string>
    <string>-m</string>
    <string>src.monitor</string>
  </array>
  <key>WorkingDirectory</key><string>$HOME/wiki-linux</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>WIKI_OS_CONFIG</key><string>$HOME/.config/wiki-linux/config.json</string>
    <key>PYTHONPATH</key><string>$HOME/wiki-linux</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$HOME/wiki/_meta/daemon.log</string>
  <key>StandardErrorPath</key><string>$HOME/wiki/_meta/daemon.err</string>
</dict>
</plist>
EOF

launchctl load -w "$PLIST"
launchctl list | grep wikilinux
```

**Filesystem watch on macOS:** The Linux `monitor.py` uses `inotify_simple`,
which doesn't exist on macOS. The agent installs `watchdog` instead and
patches `monitor.py` to use it via the FSEvents backend:

```bash
$HOME/wiki-linux/.venv/bin/pip install watchdog
```

A `monitor_macos.py` shim is provided in `src/` (or the agent generates it
from the abstract interface defined in WIKI_AGENT.md).

---

## Phase 7 — Notification Helper (wiki-notify)

See `SUPPORT_POPUP.md` for the full implementation. Quick install:

```bash
sudo install -m 755 "$HOME/wiki-linux/bin/wiki-notify-macos" /usr/local/bin/wiki-notify

# Test
wiki-notify "Wiki Setup Complete" "Vault is ready at ~/wiki" --level info
```

---

## Phase 8 — Steady State

Agent reports completion in a wiki page:

```bash
cat > "$HOME/wiki/_meta/setup-complete.md" <<EOF
---
title: Wiki Agent — macOS Setup Complete
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
agent: $AGENT_NAME
host: $(hostname)
os: macOS $(sw_vers -productVersion)
arch: $(uname -m)
---

# Setup Complete

The wiki agent finished initial setup on $(date).

## What Was Installed
- Homebrew packages: git, ripgrep, glow, ollama
- Apps: Obsidian
- LaunchAgent: com.wikilinux.monitor
- Vault: ~/wiki (registered with Obsidian + Finder sidebar)

## What Was NOT Touched
- /System (SIP-protected)
- /Library (system libraries)
- ~/Documents, ~/Downloads (Spotlight & iCloud rely on these)
- Any app installed by the user

## Next Steps
Run \`wiki ask "<question>"\` to query the wiki.
Run \`wiki status\` to see daemon health.
EOF

git -C "$HOME/wiki" add . && git -C "$HOME/wiki" commit -m "agent: setup complete"
```

---

## Rollback

If anything goes wrong, the agent runs:

```bash
# Stop and remove daemon
launchctl unload "$HOME/Library/LaunchAgents/com.wikilinux.monitor.plist" 2>/dev/null
rm -f "$HOME/Library/LaunchAgents/com.wikilinux.monitor.plist"

# Remove from Finder sidebar
mysides remove Wiki 2>/dev/null

# Wiki itself is preserved — never auto-deleted
echo "Daemon removed. Vault preserved at ~/wiki."
echo "To remove vault: rm -rf ~/wiki  (manual confirmation required)"
```

---

## What the Agent Will NEVER Do on macOS

1. Disable SIP (System Integrity Protection)
2. Modify anything under `/System` or `/Library`
3. Rename `~/Documents`, `~/Downloads`, `~/Desktop`, etc.
4. Touch `/Applications` without explicit JSON proposal + confirmation
5. Install kernel extensions
6. Modify `Info.plist` of any Apple-signed application
7. Run `csrutil` or `spctl` commands
8. Access Keychain without user prompt
9. Request Full Disk Access without explaining why

These are non-negotiable invariants from `WIKI_AGENT.md`, scoped to macOS.
