#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

open_doc() {
  local path="$1"
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$path" >/dev/null 2>&1 &
  fi
}

open_doc "$root_dir/WIKI-TOOLS/START-HERE.md"
open_doc "$root_dir/WIKI-TOOLS/DAILY-GUIDE.md"
open_doc "$root_dir/README.md"

if command -v notify-send >/dev/null 2>&1; then
  notify-send "Wiki-Linux" "Opened Start Here, Guide, and README."
fi

echo "Opened wiki intro docs:"
echo "- $root_dir/WIKI-TOOLS/START-HERE.md"
echo "- $root_dir/WIKI-TOOLS/DAILY-GUIDE.md"
echo "- $root_dir/README.md"
