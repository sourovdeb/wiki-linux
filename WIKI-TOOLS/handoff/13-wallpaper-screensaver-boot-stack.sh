#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
user_systemd_dir="$HOME/.config/systemd/user"
autostart_dir="$HOME/.config/autostart"
mkdir -p "$user_systemd_dir" "$autostart_dir"

install_user_unit() {
  local name="$1"
  local content="$2"
  printf '%s\n' "$content" > "$user_systemd_dir/$name"
}

# 1) Link scripts into ~/.local/bin for stable runtime path.
mkdir -p "$HOME/.local/bin"
for f in \
  wiki-wallpaper-gen \
  wiki-wallpaper-set \
  wiki-screensaver-interactive \
  wiki-screensaver-watch \
  wiki-auto-sync \
  wiki-health-check \
  wiki-safe-shutdown; do
  ln -sf "$repo_root/bin/$f" "$HOME/.local/bin/$f"
  chmod +x "$repo_root/bin/$f"
done

# 2) User-level wallpaper timer.
install_user_unit "wiki-wallpaper.service" "[Unit]
Description=Wiki-Linux live wallpaper update
After=graphical-session.target

[Service]
Type=oneshot
Environment=WIKI_ROOT=%h/wiki
ExecStart=%h/.local/bin/wiki-wallpaper-set
"

install_user_unit "wiki-wallpaper.timer" "[Unit]
Description=Wiki-Linux wallpaper update timer

[Timer]
OnBootSec=15sec
OnUnitActiveSec=45sec
Unit=wiki-wallpaper.service
Persistent=true

[Install]
WantedBy=timers.target
"

# 3) User-level sync timer.
install_user_unit "wiki-sync.service" "[Unit]
Description=Wiki-Linux git auto-sync
After=network-online.target

[Service]
Type=oneshot
Environment=WIKI_ROOT=%h/wiki
ExecStart=%h/.local/bin/wiki-auto-sync
"

install_user_unit "wiki-sync.timer" "[Unit]
Description=Wiki-Linux sync timer

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Unit=wiki-sync.service
Persistent=true

[Install]
WantedBy=timers.target
"

# 4) Screensaver watcher service.
install_user_unit "wiki-screensaver-watch.service" "[Unit]
Description=Wiki-Linux screensaver interactive watcher
After=graphical-session.target

[Service]
Type=simple
ExecStart=%h/.local/bin/wiki-screensaver-watch
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
"

# 5) Boot health check service (user session boot).
install_user_unit "wiki-boot-health.service" "[Unit]
Description=Wiki-Linux boot health check
After=default.target

[Service]
Type=oneshot
Environment=WIKI_ROOT=%h/wiki
Environment=WIKI_REPO_ROOT=$repo_root
ExecStart=%h/.local/bin/wiki-health-check

[Install]
WantedBy=default.target
"

# 6) Live desktop widget autostart.
cat > "$autostart_dir/wiki-desktop-live.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Wiki Desktop Live Widget
Comment=Persistent desktop overlay showing wiki status
Exec=/home/sourov/Documents/wiki-linux/wiki-linux/bin/wiki-desktop-live
Terminal=false
StartupNotify=false
Hidden=false
X-GNOME-Autostart-enabled=true
EOF

# 7) Root-level scripts and units.
sudo install -m 0755 "$repo_root/bin/wiki-root-boot-sync" /usr/local/bin/wiki-root-boot-sync
sudo install -m 0755 "$repo_root/bin/wiki-pre-shutdown-health" /usr/local/bin/wiki-pre-shutdown-health
sudo install -m 0644 "$repo_root/system/config/systemd/wiki-root-boot-sync.service" /etc/systemd/system/wiki-root-boot-sync.service
sudo install -m 0644 "$repo_root/system/config/systemd/wiki-pre-shutdown-health.service" /etc/systemd/system/wiki-pre-shutdown-health.service

# 8) Enable and start services/timers.
systemctl --user daemon-reload
systemctl --user enable --now wiki-wallpaper.timer wiki-sync.timer wiki-screensaver-watch.service wiki-boot-health.service
systemctl --user start wiki-wallpaper.service wiki-sync.service wiki-boot-health.service || true

sudo systemctl daemon-reload
sudo systemctl enable wiki-root-boot-sync.service wiki-pre-shutdown-health.service
sudo systemctl start wiki-root-boot-sync.service || true

echo "Setup complete"
systemctl --user is-active wiki-wallpaper.timer wiki-sync.timer wiki-screensaver-watch.service wiki-boot-health.service || true
sudo systemctl is-enabled wiki-root-boot-sync.service wiki-pre-shutdown-health.service || true
