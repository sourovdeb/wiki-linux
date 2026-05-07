#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

"$repo_root/WIKI-TOOLS/handoff/15-wiki-linux-diagnostic.sh"
"$repo_root/WIKI-TOOLS/handoff/14-openwebui-single-profile-repair.sh"
"$repo_root/WIKI-TOOLS/handoff/15-wiki-linux-diagnostic.sh"

echo "Diagnostic + Open WebUI fix workflow complete"
