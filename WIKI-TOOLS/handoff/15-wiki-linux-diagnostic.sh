#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
parent_root="/home/sourov/Documents/wiki-linux"
wiki_root="${WIKI_ROOT:-$HOME/wiki}"
report_dir="$repo_root/_meta/reports"
mkdir -p "$report_dir"
stamp="$(date -u +%Y%m%d-%H%M%S)"
report_file="$report_dir/wiki-linux-diagnostic-$stamp.md"

service_state() {
  local unit="$1"
  local state
  state="$(systemctl --user is-active "$unit" 2>/dev/null || true)"
  state="$(printf '%s' "$state" | tr -d '\n' | awk '{print $1}')"
  [[ -z "$state" ]] && state="inactive"
  echo "$state"
}

port_state() {
  local port="$1"
  if ss -ltn | awk '{print $4}' | grep -q ":$port$"; then
    echo listening
  else
    echo down
  fi
}

file_size() {
  local f="$1"
  [[ -f "$f" ]] && stat -c '%s' "$f" 2>/dev/null || echo 0
}

workspace_git_changes="$(git -C "$repo_root" status --porcelain | wc -l | tr -d ' ')"
workspace_branch="$(git -C "$repo_root" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"

wiki_git_changes="n/a"
wiki_branch="n/a"
if [[ -d "$wiki_root/.git" ]]; then
  wiki_git_changes="$(git -C "$wiki_root" status --porcelain | wc -l | tr -d ' ')"
  wiki_branch="$(git -C "$wiki_root" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
fi

canonical_db="$HOME/.local/share/wiki-linux/openwebui-data/webui.db"
legacy_db="$HOME/.config/open-webui/data/webui.db"
canonical_size="$(file_size "$canonical_db")"
legacy_size="$(file_size "$legacy_db")"

webui_processes="$(pgrep -af 'open-webui|app.asar' 2>/dev/null || true)"
extra_count=0
if echo "$webui_processes" | rg -q '/usr/lib/open-webui/app.asar|--port 8081'; then
  extra_count=1
fi

{
  echo "# Wiki-Linux Diagnostic"
  echo
  echo "- generated_utc: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "- parent_root_exists: $([[ -d "$parent_root" ]] && echo yes || echo no)"
  echo "- repo_root: $repo_root"
  echo "- wiki_root: $wiki_root"
  echo "- workspace_branch: $workspace_branch"
  echo "- workspace_pending_changes: $workspace_git_changes"
  echo "- wiki_branch: $wiki_branch"
  echo "- wiki_pending_changes: $wiki_git_changes"
  echo
  echo "## Services"
  echo "- wiki-ollama: $(service_state wiki-ollama.service)"
  echo "- wiki-openwebui: $(service_state wiki-openwebui.service)"
  echo "- wiki-monitor: $(service_state wiki-monitor.service)"
  echo "- wiki-sync.timer: $(service_state wiki-sync.timer)"
  echo "- wiki-wallpaper.timer: $(service_state wiki-wallpaper.timer)"
  echo "- wiki-screensaver-watch: $(service_state wiki-screensaver-watch.service)"
  echo
  echo "## Ports"
  echo "- 11434: $(port_state 11434)"
  echo "- 8080: $(port_state 8080)"
  echo
  echo "## Open WebUI State"
  echo "- canonical_db: $canonical_db"
  echo "- canonical_db_size: $canonical_size"
  echo "- legacy_db: $legacy_db"
  echo "- legacy_db_size: $legacy_size"
  echo "- extra_desktop_instance_detected: $([[ "$extra_count" -eq 1 ]] && echo yes || echo no)"
  echo
  echo "## Processes"
  if [[ -n "$webui_processes" ]]; then
    echo '```'
    echo "$webui_processes"
    echo '```'
  else
    echo "- (none)"
  fi
} > "$report_file"

echo "Diagnostic report: $report_file"
cat "$report_file"
