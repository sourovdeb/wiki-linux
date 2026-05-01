# SUPPORT_POPUP.md — `wiki-notify`

> Read **WIKI_AGENT.md** first.
>
> `wiki-notify` is the support / notification system. The agent calls it
> when something needs the user's attention: a config change worth
> reviewing, a contradiction the lint pass found, an Ollama load failure,
> a daemon crash, a successful ingest. It produces a native OS toast
> with a one-line message. Optionally a button that opens a wiki page.
>
> The whole helper is one file per platform and under 50 lines. The
> agent installs it as `wiki-notify` on `$PATH`.

---

## CALLING CONVENTION (universal)

```
wiki-notify "<title>" "<message>" [--open <wiki-page>] [--level info|warn|error]
```

Examples:

```bash
wiki-notify "Ingested" "pacman.conf documented" --open system/config/pacman.conf
wiki-notify "Lint warning" "3 orphan pages found" --open _meta/lint-report --level warn
wiki-notify "Daemon failed" "Ollama not reachable on :11434" --level error
```

---

## LINUX (`~/.local/bin/wiki-notify`)

```bash
#!/usr/bin/env bash
# wiki-notify — Linux toast wrapper
set -euo pipefail

TITLE="${1:?title required}"
MESSAGE="${2:?message required}"
shift 2

OPEN_PAGE=""
LEVEL="normal"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --open)  OPEN_PAGE="$2"; shift 2 ;;
    --level) case "$2" in
               info)  LEVEL="low"      ;;
               warn)  LEVEL="normal"   ;;
               error) LEVEL="critical" ;;
             esac; shift 2 ;;
    *) shift ;;
  esac
done

WIKI_ROOT="${WIKI_ROOT:-$HOME/wiki}"
ICON="$WIKI_ROOT/.icon.png"
[[ -f "$ICON" ]] || ICON="text-x-generic"

# Send the notification.
notify-send \
  --urgency="$LEVEL" \
  --icon="$ICON" \
  --app-name="wiki" \
  "$TITLE" "$MESSAGE"

# If --open given and an action handler exists, log it. Linux notify-send
# action callbacks need a long-running daemon; for simplicity we just log
# the page so the user can open it manually from the message.
if [[ -n "$OPEN_PAGE" ]]; then
  echo "$(date -Iseconds) $TITLE: $WIKI_ROOT/$OPEN_PAGE.md" \
    >> "$WIKI_ROOT/_meta/notifications.log"
fi
```

Make it executable:

```bash
chmod +x "$HOME/.local/bin/wiki-notify"
```

For an "Open" button, install `dunst` or `mako` (modern notification
daemons) and use the actions API; the snippet above keeps the
dependency surface to just `libnotify` and is enough for 95 % of cases.

---

## WINDOWS (`%USERPROFILE%\wiki-notify.ps1` + a tiny launcher)

Requires the `BurntToast` module:

```powershell
Install-Module -Name BurntToast -Scope CurrentUser -Force
```

`wiki-notify.ps1`:

```powershell
param(
  [Parameter(Mandatory)] [string]$Title,
  [Parameter(Mandatory)] [string]$Message,
  [string]$Open = "",
  [ValidateSet("info","warn","error")] [string]$Level = "info"
)

Import-Module BurntToast -ErrorAction Stop
$WikiRoot = if ($env:WIKI_ROOT) { $env:WIKI_ROOT } else { "C:\Wiki" }

$buttons = @()
if ($Open) {
  $target = Join-Path $WikiRoot ($Open + ".md")
  $buttons += New-BTButton -Content "Open" -Arguments $target -ActivationType Protocol
}

# Map level to a header colour by prefixing the title.
$prefix = switch ($Level) {
  "warn"  { "[!] " }
  "error" { "[X] " }
  default { ""    }
}

if ($buttons.Count -gt 0) {
  New-BurntToastNotification -Text "$prefix$Title", $Message -Button $buttons
} else {
  New-BurntToastNotification -Text "$prefix$Title", $Message
}

# Always log.
$logDir = Join-Path $WikiRoot "_meta"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
"$(Get-Date -Format o) [$Level] $Title — $Message" |
  Add-Content -Path (Join-Path $logDir "notifications.log")
```

Wrapper batch file `wiki-notify.cmd` placed on `%PATH%` so the daemon
can call `wiki-notify "x" "y"`:

```cmd
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\wiki-notify.ps1" %*
```

---

## macOS (`~/.local/bin/wiki-notify`)

```bash
#!/usr/bin/env bash
set -euo pipefail
TITLE="${1:?}"; MESSAGE="${2:?}"; shift 2

# Use osascript — built into every Mac.
osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\""

# Optional: log similarly to the Linux version.
WIKI_ROOT="${WIKI_ROOT:-$HOME/wiki}"
echo "$(date -Iseconds) $TITLE: $MESSAGE" >> "$WIKI_ROOT/_meta/notifications.log"
```

For richer notifications with action buttons on macOS, install
`terminal-notifier` (`brew install terminal-notifier`) and replace the
`osascript` line with:

```bash
terminal-notifier -title "$TITLE" -message "$MESSAGE" \
  -open "obsidian://open?vault=wiki&file=$OPEN_PAGE"
```

---

## WHY THIS LIVES OUTSIDE THE WIKI

The notification helper is **on `$PATH`**, not inside the vault. This
means:

- It runs even if the vault is deleted.
- It runs even if Ollama is offline.
- It runs from systemd / Task Scheduler with no special configuration.
- The user can call it from any script: build pipelines, cron jobs,
  even other apps.

The helper writes a log (`_meta/notifications.log`) so the user has a
history of every popup, browsable like any other wiki page.
