#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
canonical_data_dir="$HOME/.local/share/wiki-linux/openwebui-data"
legacy_data_dir="$HOME/.config/open-webui/data"
override_dir="$HOME/.config/systemd/user/wiki-openwebui.service.d"
backup_root="$HOME/.local/share/wiki-linux/openwebui-data-backups"
report_dir="$repo_root/_meta/reports"
stamp="$(date -u +%Y%m%d-%H%M%S)"
report_file="$report_dir/openwebui-profile-repair-$stamp.md"

mkdir -p "$canonical_data_dir" "$backup_root" "$override_dir" "$report_dir"

canonical_db="$canonical_data_dir/webui.db"
legacy_db="$legacy_data_dir/webui.db"

size_of() {
  local f="$1"
  if [[ -f "$f" ]]; then
    stat -c '%s' "$f" 2>/dev/null || echo 0
  else
    echo 0
  fi
}

mtime_of() {
  local f="$1"
  if [[ -f "$f" ]]; then
    stat -c '%Y' "$f" 2>/dev/null || echo 0
  else
    echo 0
  fi
}

copy_state_set() {
  local src_dir="$1"
  local dst_dir="$2"

  mkdir -p "$dst_dir"
  if [[ -f "$src_dir/webui.db" ]]; then
    cp -f "$src_dir/webui.db" "$dst_dir/webui.db"
  fi
  [[ -f "$src_dir/webui.db-wal" ]] && cp -f "$src_dir/webui.db-wal" "$dst_dir/webui.db-wal" || true
  [[ -f "$src_dir/webui.db-shm" ]] && cp -f "$src_dir/webui.db-shm" "$dst_dir/webui.db-shm" || true

  for d in vector_db uploads cache; do
    if [[ -d "$src_dir/$d" ]]; then
      mkdir -p "$dst_dir/$d"
      rsync -a "$src_dir/$d/" "$dst_dir/$d/"
    fi
  done
}

systemctl --user stop wiki-openwebui.service >/dev/null 2>&1 || true
pkill -f '/usr/lib/open-webui/app.asar' >/dev/null 2>&1 || true
pkill -f 'open-webui serve --host 127.0.0.1 --port 8081' >/dev/null 2>&1 || true

canonical_size="$(size_of "$canonical_db")"
legacy_size="$(size_of "$legacy_db")"
canonical_mtime="$(mtime_of "$canonical_db")"
legacy_mtime="$(mtime_of "$legacy_db")"

selected_src="canonical"
if [[ "$legacy_size" -gt 0 && "$canonical_size" -eq 0 ]]; then
  selected_src="legacy"
elif [[ "$legacy_mtime" -gt "$canonical_mtime" && "$legacy_size" -gt 0 ]]; then
  selected_src="legacy"
elif [[ "$legacy_size" -gt "$canonical_size" && "$legacy_size" -gt 0 ]]; then
  selected_src="legacy"
fi

if [[ "$selected_src" == "legacy" ]]; then
  backup_dir="$backup_root/pre-legacy-merge-$stamp"
  mkdir -p "$backup_dir"
  if [[ -f "$canonical_db" ]]; then
    copy_state_set "$canonical_data_dir" "$backup_dir"
  fi
  copy_state_set "$legacy_data_dir" "$canonical_data_dir"
fi

if [[ -e "$legacy_data_dir" && ! -L "$legacy_data_dir" ]]; then
  moved_legacy="$backup_root/legacy-data-dir-$stamp"
  mv "$legacy_data_dir" "$moved_legacy"
  ln -s "$canonical_data_dir" "$legacy_data_dir"
elif [[ -L "$legacy_data_dir" ]]; then
  rm -f "$legacy_data_dir"
  ln -s "$canonical_data_dir" "$legacy_data_dir"
else
  ln -s "$canonical_data_dir" "$legacy_data_dir"
fi

cat > "$override_dir/10-data-dir.conf" <<EOF
[Service]
Environment="DATA_DIR=$canonical_data_dir"
EOF

systemctl --user daemon-reload
systemctl --user start wiki-openwebui.service >/dev/null 2>&1 || true

webui_ok="no"
for _ in $(seq 1 15); do
  if curl -fsS --max-time 2 http://127.0.0.1:8080 >/dev/null 2>&1; then
    webui_ok="yes"
    break
  fi
  sleep 1
done

extra_instances="$(pgrep -af '/usr/lib/open-webui/app.asar|open-webui serve --host 127.0.0.1 --port 8081' 2>/dev/null || true)"

{
  echo "# Open WebUI Single Profile Repair"
  echo
  echo "- generated_utc: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "- canonical_data_dir: $canonical_data_dir"
  echo "- selected_source: $selected_src"
  echo "- canonical_db_size_before: $canonical_size"
  echo "- legacy_db_size_before: $legacy_size"
  echo "- webui_http_8080: $webui_ok"
  if [[ -n "$extra_instances" ]]; then
    echo "- extra_desktop_instances_detected: yes"
  else
    echo "- extra_desktop_instances_detected: no"
  fi
} > "$report_file"

echo "Open WebUI profile repair complete"
echo "Report: $report_file"
cat "$report_file"
