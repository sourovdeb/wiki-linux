#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ext_dir="$repo_root/extensions/ollama-local-assistant"
out_dir="$repo_root/_meta/reports/extension-build"
mkdir -p "$out_dir"

if [[ ! -d "$ext_dir" ]]; then
  echo "Extension directory not found: $ext_dir"
  exit 1
fi

stamp="$(date -u +%Y%m%d-%H%M%S)"
out_zip="$out_dir/ollama-local-assistant-$stamp.zip"

(
  cd "$ext_dir"
  if command -v zip >/dev/null 2>&1; then
    zip -qr "$out_zip" .
  else
    python3 - <<PY
import os
import zipfile

ext_dir = os.path.abspath("$ext_dir")
out_zip = os.path.abspath("$out_zip")

with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk(ext_dir):
        for name in files:
            path = os.path.join(root, name)
            rel = os.path.relpath(path, ext_dir)
            zf.write(path, rel)
PY
  fi
)

echo "Built extension package: $out_zip"
echo "Manual load path: $ext_dir"
echo "Chromium: open chrome://extensions -> Developer mode -> Load unpacked -> select extension folder"
