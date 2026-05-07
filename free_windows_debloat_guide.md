# Windows 11 Debloat & Wiki-Native System Guide

> **Based on:** [wiki-linux](https://github.com/sourovdeb/wiki-linux) philosophy
> **Adapted for:** Windows 11 (22H2/23H2+)
> **Last updated:** 2026-05-02

---

## Executive Summary

This guide transforms Windows 11 from a bloated consumer OS into a **clean, wiki-first knowledge workstation** by:

1. **Removing Microsoft bloat** (Teams, OneDrive sync, telemetry, ads, Edge nags)
2. **Installing lightweight alternatives** (everything local, no cloud subscriptions)
3. **Setting up a personal wiki** at `%USERPROFILE%\Wiki\` that auto-documents your system
4. **Customizing the interface** to feel wiki-native (Files opens to Wiki by default)
5. **Blocking telemetry** at the network and registry level

**Data flows one direction:** System → Wiki (read-only mirroring). Your actual Windows configuration is never touched by automation. The wiki is documentation, not configuration.

---

## Phase 1 — Pre-Flight Safety

### Backup Before Starting

```powershell
# Create a system restore point
Checkpoint-Computer -Description "Before Wiki-OS Debloat" -RestorePointType "MODIFY_SETTINGS"

# Backup registry
reg export "HKLM\SOFTWARE" "C:\Backup\HKLM_SOFTWARE.reg"
reg export "HKCU\SOFTWARE" "C:\Backup\HKCU_SOFTWARE.reg"

# List installed packages (so you can reinstall if needed)
Get-AppxPackage | Select Name, PackageFullName | Out-File "C:\Backup\installed_apps.txt"
winget list > "C:\Backup\winget_list.txt"
```

### Requirements

- Windows 11 Pro or Home (22H2 or 23H2+)
- Administrator access
- 20 GB free disk space (for Ollama models)
- **Offline Windows installation media** (in case you need to repair)

---

## Phase 2 — Nuclear Debloat (The Microsoft Purge)

### 2.1 — Remove Built-in Apps

Run this PowerShell script as **Administrator**:

```powershell
# Windows 11 bloatware removal script
# Based on Chris Titus Tech's debloat + wiki-linux minimalism

$bloatApps = @(
    "Microsoft.BingNews",
    "Microsoft.BingWeather",
    "Microsoft.GetHelp",
    "Microsoft.Getstarted",
    "Microsoft.Microsoft3DViewer",
    "Microsoft.MicrosoftOfficeHub",
    "Microsoft.MicrosoftSolitaireCollection",
    "Microsoft.MixedReality.Portal",
    "Microsoft.Office.OneNote",
    "Microsoft.People",
    "Microsoft.SkypeApp",
    "Microsoft.Todos",
    "Microsoft.WindowsAlarms",
    "Microsoft.WindowsCamera",
    "Microsoft.WindowsFeedbackHub",
    "Microsoft.WindowsMaps",
    "Microsoft.WindowsSoundRecorder",
    "Microsoft.Xbox.TCUI",
    "Microsoft.XboxApp",
    "Microsoft.XboxGameOverlay",
    "Microsoft.XboxGamingOverlay",
    "Microsoft.XboxIdentityProvider",
    "Microsoft.XboxSpeechToTextOverlay",
    "Microsoft.YourPhone",
    "Microsoft.ZuneMusic",
    "Microsoft.ZuneVideo",
    "MicrosoftTeams",  # Personal Teams, not the work one
    "Clipchamp.Clipchamp",
    "Disney+",
    "SpotifyAB.SpotifyMusic",
    "*TikTok*",
    "*Facebook*",
    "*Instagram*",
    "*Candy*",  # Candy Crush and variants
)

foreach ($app in $bloatApps) {
    Write-Host "Removing: $app" -ForegroundColor Yellow
    Get-AppxPackage -Name $app -AllUsers | Remove-AppxPackage -ErrorAction SilentlyContinue
    Get-AppxProvisionedPackage -Online | Where-Object DisplayName -like $app | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue
}

Write-Host "Bloat removal complete." -ForegroundColor Green
```

### 2.2 — Disable OneDrive (Keep the Files, Kill the Sync)

```powershell
# Stop OneDrive process
taskkill /f /im OneDrive.exe

# Uninstall OneDrive (32-bit and 64-bit paths)
if (Test-Path "$env:SystemRoot\System32\OneDriveSetup.exe") {
    Start-Process "$env:SystemRoot\System32\OneDriveSetup.exe" -ArgumentList "/uninstall" -Wait
}
if (Test-Path "$env:SystemRoot\SysWOW64\OneDriveSetup.exe") {
    Start-Process "$env:SystemRoot\SysWOW64\OneDriveSetup.exe" -ArgumentList "/uninstall" -Wait
}

# Remove OneDrive from Explorer sidebar
Remove-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" -Recurse -SilentlyContinue

Write-Host "OneDrive removed. Your files in ~\OneDrive\ are untouched." -ForegroundColor Green
```

[...TRUNCATED CONTENT FOR BREVITY... restart message to preserve character limit guidance parsing]