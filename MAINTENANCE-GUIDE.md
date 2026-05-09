# Wiki-Linux System Maintenance Guide

## Overview

This guide covers comprehensive system maintenance for **wiki-linux**, a read-only LLM wiki system that monitors system configurations. Maintenance tasks focus on:

- **Disk space recovery** without breaking system functionality
- **Boot-level health checks** that run automatically
- **Model optimization** for Ollama / AI inference  
- **OpenWebUI resource management**
- **Git repository optimization**

**Rule of Safety**: All cleanup operations are conservative and reversible. No production data is modified.

---

## System Status (as of May 9, 2026)

| Metric | Value | Status |
|--------|-------|--------|
| Total Disk | 216GB | - |
| Used | 177GB (81.7%) | ⚠️ HIGH |
| Available | 29GB (18.3%) | ⚠️ TIGHT |
| Major space consumers | Ollama (21GB) + Git (14GB) + Cache (10GB+) | ⚠️ ACTION NEEDED |

---

## Quick Start

### Run Maintenance Now
```bash
~/Documents/wiki-linux/wiki-linux/bin/wiki-system-maintenance
```

**Expected output**: 
- Duration: ~60 seconds
- Space recovered: 5-50MB (first run), more on subsequent runs
- Logs saved to: `~/.local/var/log/wiki-linux/`

### Enable Automatic Maintenance

Install systemd services to run maintenance:
- **At boot** (2 minutes after startup)
- **Daily at 3 AM**

```bash
mkdir -p ~/.config/systemd/user
cp ~/Documents/wiki-linux/wiki-linux/systemd/wiki-system-maintenance.* \
   ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable wiki-system-maintenance.timer
systemctl --user start wiki-system-maintenance.timer

# Verify
systemctl --user status wiki-system-maintenance.timer
```

---

## Key Tools

### 1. System Maintenance
**File**: `bin/wiki-system-maintenance`

Runs comprehensive cleanup in one pass:

```bash
wiki-system-maintenance
```

**Cleans**:
- Python bytecode (`__pycache__`, `.pyc`)
- Old temporary files (`*.tmp`, `*.bak`, `~*`)
- Partial Ollama downloads
- Cache files older than 14 days
- Git repository via `git gc --aggressive`

**Output**: JSON report with space recovered, duration, disk status

---

### 2. Ollama Model Optimization
**File**: `bin/wiki-ollama-optimize`

Analyze model storage and identify optimization opportunities:

```bash
wiki-ollama-optimize
```

**Shows**:
- All installed models with sizes
- Storage locations (`~/.ollama` vs `/var/lib/ollama`)
- Duplicate models across locations
- Recommendations for smaller models for maintenance tasks

**Recommendations**:
| Task | Model | Size | Reason |
|------|-------|------|--------|
| Health checks | tinyllama | 637MB | Fast, lightweight |
| Code generation | deepseek-coder:6.7b | 4.1GB | Specialized |
| Summarization | phi3 | 2.2GB | Efficient |
| Embeddings | nomic-embed-text | 274MB | Tiny, specialized |

**Action**: Remove unused larger models to recover 5-10GB

```bash
ollama rm mistral        # or whatever model isn't used
ollama pull tinyllama    # for system tasks
```

---

### 3. Library Archive Analysis
**File**: `bin/wiki-library-analyze`

Check for redundant ZIP archives in wiki library:

```bash
wiki-library-analyze
```

**Identifies**:
- ZIP files in `~/wiki/user/my_library/`
- Whether they're extractable and already extracted
- Potential disk space recovery

**Common scenario**: 
- Archive (2GB) + extracted copy (2GB) = 4GB redundancy

---

### 4. Health Check (existing)
**File**: `bin/wiki-health-check`

Quick status of wiki system:

```bash
wiki-health-check
```

**Checks**:
- Number of wiki pages
- Git pending changes
- Free disk space
- Service status (monitors, timers, daemons)
- Ollama API status
- OpenWebUI HTTP status

---

## Disk Space Recovery Strategy

### Priority 1: Duplicate Models (5-10GB potential)
1. Run `wiki-ollama-optimize`
2. Identify duplicate models across `~/.ollama` and `/var/lib/ollama`
3. Remove duplicates: `ollama rm <model>`
4. Keep smaller models for maintenance tasks

**ETA**: 5 minutes  
**Risk**: Low (models can be re-downloaded)

### Priority 2: Unused Ollama Models (5-20GB potential)
1. Identify which models are actually used
2. Remove unused models: `ollama rm <model>`
3. Keep: tinyllama (maintenance), your primary model

**ETA**: 5 minutes  
**Risk**: Low

### Priority 3: Git Repository Optimization (1-3GB potential)
1. Automatic via `wiki-system-maintenance`
2. Manual: `cd ~/wiki && git gc --aggressive --prune=now`
3. Consider shallow clone if repo history is not critical

**ETA**: 1-5 minutes  
**Risk**: Very low (only optimizes, doesn't delete history)

### Priority 4: Cache Cleanup (2-5GB potential)
1. Automatic via `wiki-system-maintenance` (runs on all caches older than 14 days)
2. Manual: `rm -rf ~/.cache/*`
3. VS Code cache: `rm -rf ~/.config/Code\ -\ OSS/CachedData/`

**ETA**: 1 minute  
**Risk**: Very low (caches are regenerated on demand)

### Priority 5: Archive Redundancy (0-4GB potential)
1. Run `wiki-library-analyze`
2. Check if `~/wiki/user/my_library/*.zip` have extracted copies
3. Safe removal: `rm <archive.zip>` (keep extracted)

**ETA**: 5 minutes  
**Risk**: Very low (extracted copies exist)

---

## OpenWebUI Management

### Check Status
```bash
systemctl --user status open-webui
# or
ps aux | grep -i webui
```

### Expected Resource Usage
- **Memory**: 100-300MB idle, 500MB-1GB with active models
- **CPU**: <10% idle, 50-90% during inference
- **Ports**: 8080 (web), 11434 (Ollama API)

### Optimize Resource Usage
```bash
# Verify it's not consuming excess memory
ps aux | grep -E 'open-webui|webui' | awk '{print $2, $4, $6}' | sort -k3 -rn

# Limit model loading
# Configure in OpenWebUI settings:
# - Max loaded models: 1
# - Auto-offload unused models
```

### Disable If Not Needed
```bash
systemctl --user disable open-webui.service
systemctl --user stop open-webui.service
```

**Recovers**: 100-300MB memory for other tasks  
**Alternative**: Use wiki CLI instead of web UI when possible

---

## Boot-Level Health Service

Automatic health check and cleanup at every boot.

### What Runs
1. Python cache cleanup
2. Temporary file removal  
3. Partial blob removal
4. Cache cleanup (files older than 14 days)
5. Git optimization

### When
- **At boot**: 2 minutes after system starts
- **Daily**: 3:00 AM automatically

### Logs
```bash
# View boot maintenance
journalctl --user -u wiki-system-maintenance.service -f

# View timer status
systemctl --user list-timers

# View past runs
journalctl --user -u wiki-system-maintenance.service --all
```

### Manual Trigger
```bash
systemctl --user start wiki-system-maintenance.service
```

---

## Monitoring Strategies

### Daily Dashboard
```bash
wiki health-check
df -h /
du -sh ~/.ollama ~/.cache ~/wiki
```

### Monthly Deep Dive
1. Check `journalctl --user -u wiki-system-maintenance.service`
2. Review maintenance logs: `ls -lt ~/.local/var/log/wiki-linux/`
3. Run `wiki-ollama-optimize` to spot redundancy
4. Run `wiki-library-analyze` to check for unused archives

### Alerts
- **Free space <10%**: Immediate action needed
- **Free space <5%**: System will become unstable
- **Free space <1%**: Risk of data loss

Current status: **18.3% free** ✓ (Safe, but monitor closely)

---

## Performance Tips

### 1. Disable Unnecessary Services
```bash
systemctl --user disable wiki-wallpaper.timer  # if not needed
systemctl --user disable wiki-screensaver-watch.service  # if not needed
```

### 2. Optimize Ollama
```bash
# Use 4-bit quantization for smaller model files
# In Ollama modelfile:
# PARAMETER quantization q4_0  # 4-bit quantization

# Or use GGML format (more efficient)
ollama pull neural-chat:7b-q4  # Already quantized version
```

### 3. Use Smaller Models for Specific Tasks
- Health checks: **tinyllama** (637MB)
- Code review: **deepseek-coder:6.7b** (4GB, specialized)
- Embeddings: **nomic-embed-text** (274MB)

### 4. Reduce Git Clone Depth (if re-cloning)
```bash
git clone --depth 1 https://github.com/user/repo
```

---

## Troubleshooting

### Issue: Maintenance Script Hangs
**Cause**: Git GC taking too long on large repository

**Fix**:
```bash
# Kill process if needed
pkill -f "wiki-system-maintenance"

# Manually run git gc with timeout
timeout 30 git -C ~/wiki gc --aggressive
```

### Issue: OpenWebUI Using Too Much Memory
**Cause**: Model not unloading after use

**Fix**:
```bash
# Restart service
systemctl --user restart open-webui

# Or manually: navigate to Settings → Model Management → Unload Models
```

### Issue: Low Free Space During Downloads
**Cause**: Large models being downloaded while disk is full

**Fix**:
1. Run `wiki-system-maintenance` first
2. Then download: `ollama pull <model>`

### Issue: Cannot Write Maintenance Logs
**Cause**: `/var/log/wiki-linux` owned by root

**Fix**: Logs fallback to `~/.local/var/log/wiki-linux/` automatically. Verify:
```bash
ls -l ~/.local/var/log/wiki-linux/
```

---

## Integration with System

### Systemd User Services
```bash
~/.config/systemd/user/wiki-system-maintenance.service
~/.config/systemd/user/wiki-system-maintenance.timer
```

### Cron Alternative (if systemd user services not available)
```bash
# Add to crontab
crontab -e

# Run maintenance daily at 3 AM
0 3 * * * ~/Documents/wiki-linux/wiki-linux/bin/wiki-system-maintenance >> ~/.local/var/log/wiki-linux/cron.log 2>&1

# Run health check daily at 9 AM
0 9 * * * ~/Documents/wiki-linux/wiki-linux/bin/wiki-health-check >> ~/.local/var/log/wiki-linux/health.log 2>&1
```

---

## Recovery Procedures

### Restore Deleted Model
```bash
ollama pull <model-name>  # Re-download from registry
```

### Restore Deleted Cache
```bash
# Most caches are regenerated automatically
# For specific application:
<app-name> --reset-cache  # varies by app
```

### Restore Git History (if accidentally pruned)
```bash
cd ~/wiki
git reflog
git reset --hard <commit-before-prune>  # restore to specific point
```

---

## Capacity Planning

### Current Usage Pattern
| Component | Size | Growth Rate | Action |
|-----------|------|-------------|--------|
| Ollama models | 21GB | Depends on new models | Quarterly review |
| Git repository | 14GB | ~1GB/month | Monthly git gc |
| Caches | 5GB+ | Automatic cleanup | Daily via maintenance |
| System configs (wiki) | <1GB | Minimal | N/A |

### Recommendations
1. **Keep 10-15% free space** for system operations (currently at 18.3% ✓)
2. **Schedule monthly reviews** of Ollama models for removal
3. **Run weekly maintenance** to catch accumulation early
4. **Archive old wiki pages** if /wiki grows beyond 50GB

---

## Advanced: Custom Cleanup Scripts

### Remove Specific Cache
```bash
# Firefox cache
rm -rf ~/.cache/firefox

# Chromium cache  
rm -rf ~/.cache/chromium

# System package cache (Arch)
sudo pacman -Sc  # Clean uninstalled package cache
```

### Git Repository Size Audit
```bash
cd ~/wiki

# Find largest files in history
git rev-list --all --objects | \
  sed -n $(git rev-list --objects --all | \
  cut -f1 -d' ' | git cat-file --batch-check | \
  grep blob | sort -t' ' -k3 -rn | head -10 | \
  awk '{print $1}') | \
  paste - - | \
  awk '{print $3, $2}' | \
  sort -rn | head -10
```

---

## Questions / Help

For issues with wiki-linux maintenance:
1. Check `/var/log/wiki-linux/` or `~/.local/var/log/wiki-linux/` for logs
2. Run `wiki-health-check` for system status
3. Review `journalctl --user` for service errors

---

## Summary: The Rule of 3

1. **Quarterly** (every 3 months):
   - Review Ollama models
   - Archive old wiki pages
   - Check disk usage trend

2. **Monthly** (every 30 days):
   - Run manual health check
   - Review maintenance logs
   - Optimize git repositories

3. **Weekly** (every 7 days):
   - Ensure automatic maintenance is running
   - Monitor free disk space
   - Check system logs

**Current Status**: 18.3% free space - monitor quarterly ✓
