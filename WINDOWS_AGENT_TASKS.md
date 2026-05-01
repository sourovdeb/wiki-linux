# WINDOWS_AGENT_TASKS.md

> Read **WIKI_AGENT.md** first.
>
> **Important honesty up front.** The user may have asked for "jailbreaking
> Windows" — renaming `C:\Windows`, `C:\Users`, `C:\Program Files`, or
> writing the wiki at the root level. These operations brick Windows. Not
> in theory — in practice, on the next boot. The boot loader, the
> registry, every installed application, Windows Update, TrustedInstaller,
> and the side-by-side assembly cache all hard-code those paths.
> Disabling Windows Resource Protection does not change this; it just
> removes the only thing stopping you. The agent must refuse to perform
> these operations and explain why.
>
> What the agent **can** do is make Windows *feel* wiki-native:
>
> - Rename the **display names** users see in Explorer (registry
>   `LocalizedString`), without moving the underlying folders.
> - Create a top-level `C:\Wiki` folder (this is allowed; it's not a
>   system folder).
> - Move the user's personal `Documents`, `Downloads`, `Desktop`
>   library locations to subfolders of the wiki, using the supported
>   "Move folder" dialog.
> - Pin the wiki to Quick Access, the Start menu, and the taskbar.
> - Set Explorer's default open location to the wiki.
> - Replace the heavy Microsoft-bundled tooling with the minimal set.
>
> Together these produce the visual outcome the user wants. Nothing
> below this line will damage Windows.

---

## TARGET SYSTEMS

Windows 10 22H2, Windows 11. PowerShell 5+ (built in) or PowerShell 7.

Run all of these from an **elevated PowerShell** (Run as Administrator)
unless noted.

---

## TASK 1 — Vault and Git

```powershell
$WikiRoot = "C:\Wiki"          # top-level allowed; not a system folder
New-Item -ItemType Directory -Force -Path `
  "$WikiRoot\system\config", `
  "$WikiRoot\system\docs", `
  "$WikiRoot\user\notes", `
  "$WikiRoot\user\projects", `
  "$WikiRoot\user\research", `
  "$WikiRoot\_meta", `
  "$WikiRoot\raw" | Out-Null

@"
_tmp/
*.log
Thumbs.db
desktop.ini
"@ | Set-Content "$WikiRoot\.gitignore"

Push-Location $WikiRoot
git init -b main | Out-Null
git add .gitignore
git commit -m "init: empty wiki" | Out-Null
Pop-Location

Write-Host "Vault created at $WikiRoot"
```

If the user prefers `%USERPROFILE%\Wiki`, swap the `$WikiRoot`
assignment.

## TASK 2 — Install the wiki tools (winget)

```powershell
winget install --id Git.Git -e --accept-source-agreements
winget install --id BurntSushi.ripgrep.MSVC -e
winget install --id charmbracelet.glow -e
winget install --id Obsidian.Obsidian -e
winget install --id Ollama.Ollama -e
```

Pull the model (run as the normal user, not elevated, after Ollama
finishes installing and starting):

```powershell
ollama pull mistral        # or llama3.2 / phi3 / tinyllama
```

## TASK 3 — Tool minimisation

Audit and propose. **Do not execute without confirmation.**

```powershell
$proposed = @(
  "Microsoft.BingNews",
  "Microsoft.BingWeather",
  "Microsoft.GetHelp",
  "Microsoft.Getstarted",
  "Microsoft.MicrosoftSolitaireCollection",
  "Microsoft.MicrosoftStickyNotes",
  "Microsoft.People",
  "Microsoft.WindowsFeedbackHub",
  "Microsoft.Xbox.TCUI",
  "Microsoft.XboxApp",
  "Microsoft.XboxGameOverlay",
  "Microsoft.XboxGamingOverlay",
  "Microsoft.XboxIdentityProvider",
  "Microsoft.XboxSpeechToTextOverlay",
  "Microsoft.YourPhone",
  "Microsoft.ZuneMusic",
  "Microsoft.ZuneVideo",
  "MicrosoftTeams"
)

Write-Host "These appear installed and are commonly removed:"
$proposed | ForEach-Object {
  if (Get-AppxPackage -Name $_ -ErrorAction SilentlyContinue) {
    Write-Host "  $_"
  }
}
Write-Host ""
Write-Host "Type 'YES REMOVE' (exact) to remove all listed; anything else to skip:"
$confirm = Read-Host
```

After confirmation:

```powershell
if ($confirm -ceq "YES REMOVE") {
  $proposed | ForEach-Object {
    Get-AppxPackage -Name $_ -AllUsers -ErrorAction SilentlyContinue |
      Remove-AppxPackage -ErrorAction SilentlyContinue
  }
}
```

`Microsoft.WindowsStore`, `Microsoft.WindowsCalculator`,
`Microsoft.Windows.Photos`, `Microsoft.WindowsTerminal` —
**leave alone.** They look bloaty but are deeply integrated.

## TASK 4 — Visible folder renames (registry, safe)

Windows lets you change the *display name* of a known folder
(Documents, Downloads, Desktop, etc.) without moving the directory.
This is what makes Explorer say "Notes" while the underlying path is
still `C:\Users\<you>\Documents`.

```powershell
# Per-user known folder display names live in:
$key = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"

# We do NOT change the path values here — only Display Names through
# desktop.ini, which is the supported mechanism.

function Rename-FolderDisplay {
  param([string]$Path, [string]$NewName)
  if (-not (Test-Path $Path)) { return }
  $ini = Join-Path $Path "desktop.ini"
  attrib -h -s $ini 2>$null
  @"
[.ShellClassInfo]
LocalizedResourceName=$NewName
"@ | Set-Content -Path $ini -Encoding Unicode
  attrib +h +s $ini
  attrib +r $Path
}

# Examples — run with user confirmation only:
Rename-FolderDisplay "$env:USERPROFILE\Documents" "Notes"
Rename-FolderDisplay "$env:USERPROFILE\Downloads" "Inbox"
Rename-FolderDisplay "$env:USERPROFILE\Desktop"   "Desk"
```

This changes what Explorer shows. Applications that read the literal
path keep working — because nothing actually moved. To revert, delete
the `desktop.ini` file.

**Do not** attempt this on `C:\Users`, `C:\Program Files`, or
`C:\Windows`. The registry will let you set a `LocalizedString`, but
several Microsoft components hard-check the literal path string and
will fail.

## TASK 5 — Move personal libraries into the wiki (supported)

Windows fully supports moving the storage location of `Documents`,
`Downloads`, etc. The OS keeps the symlink semantics and applications
continue to work.

```powershell
# Right-click in Explorer → Properties → Location → Move...
# is the user-facing version. The PowerShell-equivalent is:

$moves = @{
  "Personal"   = "$WikiRoot\user\notes"      # Documents
  "Desktop"    = "$WikiRoot\user\desk"
  "{374DE290-123F-4565-9164-39C4925E467B}" = "$WikiRoot\raw"  # Downloads
}

# WARN the user: this physically moves files. Back up first.
# Implementation outline (one folder shown for clarity):
$key = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
Set-ItemProperty -Path $key -Name "Personal" -Value "$WikiRoot\user\notes"
# Then physically move existing contents and trigger a shell refresh.
```

**Always confirm with the user before this step.** It is reversible
(move the folders back, restore the registry values), but it touches
real data.

## TASK 6 — Quick Access, Start Menu, Taskbar

```powershell
# Pin the wiki to Explorer Quick Access:
$shell = New-Object -ComObject Shell.Application
$shell.Namespace($WikiRoot).Self.InvokeVerb("pintohome")

# Place a shortcut on the Desktop:
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Wiki.lnk")
$shortcut.TargetPath = $WikiRoot
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,4"
$shortcut.Save()
```

Set Explorer to open at the wiki by default:

```powershell
Set-ItemProperty `
  -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" `
  -Name "LaunchTo" -Value 1     # 1 = This PC, 2 = Quick Access, 3 = Downloads
# Pin Wiki at the top of Quick Access (TASK above) and the user lands there.
```

## TASK 7 — Obsidian vault registration

Obsidian on Windows stores its vault registry at:
`%APPDATA%\obsidian\obsidian.json`

```powershell
$obsidianCfg = "$env:APPDATA\obsidian\obsidian.json"
New-Item -ItemType Directory -Force -Path (Split-Path $obsidianCfg) | Out-Null

if (-not (Test-Path $obsidianCfg)) {
@"
{
  "vaults": {
    "wiki": {
      "path": "$($WikiRoot.Replace('\','/'))",
      "ts": $([int][double]::Parse((Get-Date -UFormat %s))),
      "open": true
    }
  }
}
"@ | Set-Content $obsidianCfg
}
```

## TASK 8 — PowerShell profile shortcuts

```powershell
$profileLine = @"

# wiki-os shortcuts
\$env:WIKI_ROOT = "$WikiRoot"
function wiki   { Set-Location \$env:WIKI_ROOT }
function cdwiki { param(\$sub) Set-Location (Join-Path \$env:WIKI_ROOT \$sub) }
"@

if (-not (Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force | Out-Null }
Add-Content -Path $PROFILE -Value $profileLine
```

## TASK 9 — Notification helper

See **SUPPORT_POPUP.md**. On Windows, `wiki-notify` is a small
PowerShell wrapper around the toast notification API (BurntToast
module or the built-in WinRT API).

```powershell
Install-Module -Name BurntToast -Scope CurrentUser -Force
```

## TASK 10 — Final commit

```powershell
Push-Location $WikiRoot
git add -A
git commit -m "init: vault structure, schema, AGENTS.md" 2>$null
Pop-Location

# Confirm with a toast:
Import-Module BurntToast
New-BurntToastNotification -Text "Wiki setup complete", "Open Obsidian to start using your vault."
```

---

## WHAT THIS NEVER TOUCHES

- `C:\Windows`, `C:\Program Files`, `C:\Program Files (x86)`,
  `C:\ProgramData`, `C:\Users` (the directory itself), the EFI
  partition.
- Registry keys outside `HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer`.
- TrustedInstaller, Windows Resource Protection, system file ACLs.
- The boot loader, recovery environment, BitLocker keys.
- Any service in `services.msc` not explicitly named in this file.

If the agent is asked to do something outside this list — **especially
"rename C:\Windows" or "move C:\Users" or "save changes at root level"
— the agent must refuse and reread WIKI_AGENT.md "Non-Negotiable
Invariants".**

---

## WHY YOU CAN'T "JAILBREAK" WINDOWS LIKE iOS

iOS jailbreaking exploits a kernel vulnerability to remove sandboxing,
then leaves the filesystem layout intact. The point of jailbreaking is
to *run unsigned code*, not to *rearrange the operating system*.

Windows already runs any code you give it (with your permission). What
"jailbreaking" would mean here — renaming or relocating the system
directories — is a thing iOS jailbreakers also do not do, because it
would brick iOS the same way it bricks Windows.

The visual outcome you want (a wiki-native PC) comes from the
display-name renames, the wiki at `C:\Wiki`, and Obsidian as the
front-of-house. Not from filesystem surgery.
