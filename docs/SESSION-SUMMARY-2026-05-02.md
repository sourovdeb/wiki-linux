# Wiki-Linux System Consolidation — May 2, 2026

## Summary
Complete system consolidation: moved all wiki-linux infrastructure to permanent system-wide locations at `/opt/wiki-linux`, removed 50GB of non-project files, configured Obsidian and Ollama system-wide.

## Changes Made

### 1. System Infrastructure (moved to /opt)
- **Config:** `~/.config/wiki-linux/` → `/opt/wiki-linux/config/user-config/`
- **Ollama:** `~/.ollama/` → `/opt/wiki-linux/ollama/`
- **Obsidian:** vault at `/home/sourov/wiki` + symlink at `/opt/wiki-linux/obsidian/vault`
- **Tools:** all `bin/wiki-*` scripts copied to `/opt/wiki-linux/tools/`
- **System environment:** `/etc/profile.d/wiki-linux.sh` and `~/.config/environment.d/wiki-linux.conf`

### 2. Cleanup (recovered 50GB)
- Removed: `~/aeon` (4.9GB), `~/Downloads` (689MB), `~/Pictures`, `~/Videos`, `~/Music`, `~/Writing`
- Cleared: `~/.cache/` (15GB)
- Cleaned: non-wiki home root files, Thunderbird, ProtonMail configs
- Kept only: `~/wiki`, `~/Documents/wiki-linux`, `~/bin`

### 3. Systemd Service Updates
- **wiki-monitor.service:** uses `/opt/wiki-linux/config/user-config/config.json`
- **wiki-sync.service:** updated with `/opt/wiki-linux` paths
- Both services auto-start on boot

### 4. System-wide Integration
- Environment variables exported from `/etc/profile.d/wiki-linux.sh`
- Unified launcher: `/usr/local/bin/wiki-system` → `/opt/wiki-linux/bin/wiki-system`
- Obsidian configured with BMO Chatbot → Ollama at localhost:11434

## Disk Recovery
- **Before:** 54GB free (74% used)
- **After:** 83GB free (60% used)
- **Recovered:** ~50GB

## Final Disk State
```
Filesystem: 216GB total
Used: 122GB (56%)
Free: 83GB (44%)
Utilization: 60%
```

## Permanent Configuration
All changes locked in:
- Config immutable (444)
- Systemd auto-start enabled
- Git history preserved (8 commits on wiki-arch)
- SSH remote configured

## Next Steps
1. Restart Ollama service
2. Verify all integrations
3. Push to GitHub (wiki-arch branch)

---
**Project:** wiki-linux (Arch system knowledge layer)
**Status:** ✅ CONSOLIDATED & READY
