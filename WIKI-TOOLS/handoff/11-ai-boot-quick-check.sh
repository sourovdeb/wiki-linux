#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
report_dir="$root_dir/_meta/reports"
mkdir -p "$report_dir"
stamp="$(date -u +%Y%m%d-%H%M%S)"
report_file="$report_dir/ai-boot-check-$stamp.md"

quiet="no"
start="no"
for arg in "${@:-}"; do
  case "$arg" in
    --quiet) quiet="yes" ;;
    --start) start="yes" ;;
  esac
done

start_user_service_if_present() {
  local unit="$1"
  if systemctl --user list-unit-files "$unit" >/dev/null 2>&1; then
    systemctl --user start "$unit" >/dev/null 2>&1 || true
  fi
}

wait_http() {
  local url="$1"
  local retries="${2:-15}"
  local i
  for i in $(seq 1 "$retries"); do
    if curl -fsS --max-time 3 "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

if [[ "$start" == "yes" ]]; then
  start_user_service_if_present "wiki-ollama.service"
  start_user_service_if_present "wiki-openwebui.service"
fi

wait_http "http://127.0.0.1:11434/api/tags" 12 || true
wait_http "http://127.0.0.1:8080" 8 || true

ollama_ok="no"
webui_ok="no"
model_count="0"

if curl -fsS --max-time 4 http://127.0.0.1:11434/api/tags >/tmp/wiki-ai-tags.json 2>/dev/null; then
  ollama_ok="yes"
  model_count="$(grep -o '"name"' /tmp/wiki-ai-tags.json | wc -l | tr -d ' ')"
fi

if curl -fsS --max-time 4 http://127.0.0.1:8080 >/dev/null 2>&1; then
  webui_ok="yes"
fi

{
  printf "# AI Boot Quick Check\n\n"
  printf -- "- generated_utc: %s\n" "$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  printf -- "- repo_root: %s\n\n" "$root_dir"
  printf -- "- attempted_start: %s\n" "$start"
  printf -- "- ollama_api_ok: %s\n" "$ollama_ok"
  printf -- "- open_webui_http_ok: %s\n" "$webui_ok"
  printf -- "- model_count: %s\n" "$model_count"
  printf -- "- note: open_webui_http_ok=no can still mean desktop app mode is available.\n"
  printf -- "- tip: pass '--start' to request systemd user service start (never spawns background daemons).\n"
} > "$report_file"

if command -v notify-send >/dev/null 2>&1; then
  notify-send "Wiki AI Boot Check" "Ollama: $ollama_ok | Open WebUI HTTP: $webui_ok | Models: $model_count"
fi

if [[ "$quiet" != "yes" ]]; then
  echo "AI boot quick check complete."
  echo "Report: $report_file"
  cat "$report_file"
fi
