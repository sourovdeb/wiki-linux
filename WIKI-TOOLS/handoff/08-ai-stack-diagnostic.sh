#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
report_dir="$root_dir/_meta/reports"
stamp="$(date -u +%Y%m%d-%H%M%S)"
report_file="$report_dir/ai-stack-diagnostic-$stamp.md"
mkdir -p "$report_dir"

status_line() {
  local name="$1"
  local cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    printf -- "- %s: PASS\n" "$name"
  else
    printf -- "- %s: FAIL\n" "$name"
  fi
}

ollama_models_json="$(curl -fsS --max-time 5 http://127.0.0.1:11434/api/tags 2>/dev/null || true)"
model_count="$(printf '%s' "$ollama_models_json" | grep -o '"name"' | wc -l | tr -d ' ')"
model_list="$(printf '%s' "$ollama_models_json" | grep -o '"name":"[^"]*"' | cut -d':' -f2- | tr -d '"' | paste -sd ', ' - || true)"

if [[ -z "$model_list" ]]; then
  model_list="(none detected)"
fi

{
  printf "# AI Stack Diagnostic\n\n"
  printf -- "- generated_utc: %s\n" "$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  printf -- "- repo_root: %s\n\n" "$root_dir"

  printf "## Binaries\n"
  status_line "ollama binary" "command -v ollama"
  status_line "open-webui binary" "command -v open-webui"
  status_line "ollama-view command" "command -v ollama-view"
  status_line "repo ollama-view script" "test -x '$root_dir/bin/ollama-view'"
  printf "\n"

  printf "## Services\n"
  status_line "system ollama active" "systemctl is-active ollama | grep -q active"
  status_line "user wiki-ollama active" "systemctl --user is-active wiki-ollama.service | grep -q active"
  status_line "user wiki-openwebui active" "systemctl --user is-active wiki-openwebui.service | grep -q active"
  printf "\n"

  printf "## HTTP Endpoints\n"
  status_line "Ollama API (11434)" "curl -fsS --max-time 4 http://127.0.0.1:11434/api/tags"
  status_line "Open WebUI (8080)" "curl -fsS --max-time 4 http://127.0.0.1:8080"
  printf "\n"

  printf "## Tiny Models\n"
  printf -- "- model_count: %s\n" "${model_count:-0}"
  printf -- "- models: %s\n" "$model_list"
  status_line "llama3.2:3b present" "printf '%s' '$model_list' | grep -q 'llama3.2:3b'"
  status_line "qwen2.5-coder:3b present" "printf '%s' '$model_list' | grep -q 'qwen2.5-coder:3b'"
  status_line "nomic-embed-text present" "printf '%s' '$model_list' | grep -q 'nomic-embed-text'"
  printf "\n"

  printf "## Launchers\n"
  status_line "Ollama launcher desktop" "test -f '$root_dir/WIKI-TOOLS/OLLAMA-CHAT.desktop'"
  status_line "Chromium AI desktop" "test -f '$root_dir/WIKI-TOOLS/7-CHROMIUM-AI.desktop'"
  status_line "Firefox AI desktop" "test -f '$root_dir/WIKI-TOOLS/8-FIREFOX-AI.desktop'"
  status_line "Wiki explainer desktop" "test -f '$root_dir/WIKI-TOOLS/12-WIKI-HOW-IT-WORKS.desktop'"
  status_line "autostart quick-check" "test -f '$HOME/.config/autostart/wiki-ai-boot-check.desktop'"
} > "$report_file"

printf "AI diagnostic report written: %s\n" "$report_file"
cat "$report_file"
