#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
service_dir="$HOME/.config/systemd/user"
autostart_dir="$HOME/.config/autostart"
local_bin_dir="$HOME/.local/bin"
venv_dir="$HOME/.local/share/wiki-linux/openwebui-venv"
install_log="$root_dir/.openwebui-install.log"
boot_check_script="$root_dir/WIKI-TOOLS/handoff/11-ai-boot-quick-check.sh"
ollama_view_script="$root_dir/bin/ollama-view"

mkdir -p "$service_dir" "$autostart_dir" "$local_bin_dir"

cat > "$service_dir/wiki-ollama.service" <<'EOF'
[Unit]
Description=Wiki Ollama Local Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_NUM_PARALLEL=1"
ExecStart=/usr/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

python_for_webui="python3"
if [[ -x "$HOME/.config/open-webui/python/bin/python3.12" ]]; then
  python_for_webui="$HOME/.config/open-webui/python/bin/python3.12"
fi

if [[ ! -x "$venv_dir/bin/python" ]]; then
  "$python_for_webui" -m venv "$venv_dir"
fi

openwebui_ready="no"
openwebui_cmd=""
"$venv_dir/bin/python" -m pip install --upgrade pip wheel >"$install_log" 2>&1 || true
if "$venv_dir/bin/python" -m pip install --upgrade open-webui >>"$install_log" 2>&1; then
  if [[ -x "$venv_dir/bin/open-webui" ]]; then
    openwebui_ready="yes"
    openwebui_cmd="$venv_dir/bin/open-webui"
  fi
fi

if [[ "$openwebui_ready" != "yes" ]] && [[ -x "$HOME/.config/open-webui/python/bin/python3.12" ]]; then
  rm -rf "$venv_dir"
  "$HOME/.config/open-webui/python/bin/python3.12" -m venv "$venv_dir"
  "$venv_dir/bin/python" -m pip install --upgrade pip wheel >"$install_log" 2>&1 || true
  if "$venv_dir/bin/python" -m pip install --upgrade open-webui >>"$install_log" 2>&1; then
    if [[ -x "$venv_dir/bin/open-webui" ]]; then
      openwebui_ready="yes"
      openwebui_cmd="$venv_dir/bin/open-webui"
    fi
  fi
fi

if [[ "$openwebui_ready" != "yes" ]] && [[ -x "$HOME/.config/open-webui/python/bin/open-webui" ]]; then
  openwebui_ready="yes"
  openwebui_cmd="$HOME/.config/open-webui/python/bin/open-webui"
fi

if [[ "$openwebui_ready" == "yes" ]]; then
  cat > "$service_dir/wiki-openwebui.service" <<EOF
[Unit]
Description=Wiki Open WebUI Local Service
After=wiki-ollama.service
Requires=wiki-ollama.service

[Service]
Type=simple
Environment="OLLAMA_BASE_URL=http://127.0.0.1:11434"
Environment="DATA_DIR=%h/.local/share/wiki-linux/openwebui-data"
ExecStart=$openwebui_cmd serve --host 127.0.0.1 --port 8080
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF
fi

cat > "$autostart_dir/wiki-ai-boot-check.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Wiki AI Boot Quick Check
Comment=Runs a fast Ollama/Open WebUI health check at login
Exec=bash $boot_check_script --quiet
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

if [[ -x "$ollama_view_script" ]]; then
  ln -sf "$ollama_view_script" "$local_bin_dir/ollama-view"
fi

systemctl --user daemon-reload
systemctl --user enable --now wiki-ollama.service

for _ in $(seq 1 20); do
  if curl -fsS --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

for model in llama3.2:3b qwen2.5-coder:3b nomic-embed-text; do
  if ollama list 2>/dev/null | awk 'NR>1 {print $1}' | grep -qx "$model"; then
    echo "Model already present: $model"
  else
    echo "Pulling model: $model"
    ollama pull "$model" || true
  fi
done

if [[ "$openwebui_ready" == "yes" ]]; then
  systemctl --user enable --now wiki-openwebui.service
  for _ in $(seq 1 20); do
    if curl -fsS --max-time 3 http://127.0.0.1:8080 >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
else
  echo "Open WebUI server install did not complete. Desktop app fallback remains available via /usr/bin/open-webui."
  echo "Install log: $install_log"
fi

if [[ -x "$boot_check_script" ]]; then
  "$boot_check_script" --quiet || true
fi

echo "AI stack configuration complete."
echo "Ollama API: http://127.0.0.1:11434"
echo "Open WebUI: http://127.0.0.1:8080 (if server mode is available)"
