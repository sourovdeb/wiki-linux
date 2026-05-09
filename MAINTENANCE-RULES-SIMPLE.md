# System Maintenance Rules (Simple Guide for Small AI Models)

**Purpose**: Keep wiki-linux system healthy and disk space available.

---

## Rule 1: Check Disk Space Daily

**What to do**:
```bash
df -h /
```

**What to look for**:
- If "Use%" is **above 90%** → Run cleanup NOW
- If "Use%" is **above 95%** → URGENT, delete files NOW
- If "Use%" is **below 90%** → System is OK

**Current Status**: 87% used (OK, but watch it)

---

## Rule 2: Run Automatic Cleanup

**The system cleans itself automatically**:
- At boot (2 minutes after startup)
- Every day at 3:00 AM

**To check if it's working**:
```bash
systemctl --user status wiki-system-maintenance.timer
```

**Look for**: `Active: active (waiting)` ← This means it's ON

**If it says "inactive"**:
```bash
systemctl --user start wiki-system-maintenance.timer
```

---

## Rule 3: What Gets Cleaned Automatically

Every cleanup removes these SAFE files:
1. Python cache files (`__pycache__`, `.pyc`)
2. Temporary files older than 1 day (`*.tmp`, `*.bak`)
3. Partial Ollama downloads (`*-partial`)
4. Cache files older than 14 days
5. Git garbage (old versions nobody uses)

**These are SAFE to delete** - they regenerate if needed.

---

## Rule 4: Manual Cleanup Command

**When to use**: Disk space is getting low (above 85% used)

**Command**:
```bash
~/Documents/wiki-linux/wiki-linux/bin/wiki-system-maintenance
```

**How long**: 60 seconds

**What it does**: Same as automatic cleanup, but you control when

---

## Rule 5: Check System Status Fast

**Command**:
```bash
~/Documents/wiki-linux/wiki-linux/bin/wiki-quick-check
```

**What you'll see**:
- Disk space (how much free)
- Wiki pages (how many)
- Services (which are running)
- Ollama (AI models loaded)
- OpenWebUI (web interface status)

**All checks have ✓ or ✗**:
- ✓ = Working correctly
- ✗ = Problem, needs attention

---

## Rule 6: Ollama Models Take Lots of Space

**Current situation**: 21GB used by AI models

**To see which models you have**:
```bash
ollama list
```

**To remove a model you don't use**:
```bash
ollama rm MODEL_NAME
```

**BEFORE removing, check**:
```bash
~/Documents/wiki-linux/wiki-linux/bin/wiki-ollama-optimize
```

This shows:
- All models and their sizes
- Which models are duplicated
- Recommendations for smaller models

**Safe models to remove**: Any model you don't recognize or use

---

## Rule 7: Never Delete These

**DO NOT DELETE**:
- `/home/sourov/wiki/` (your wiki content)
- `/etc/` (system configuration)
- `/home/sourov/Documents/wiki-linux/wiki-linux/` (this program)
- Any file in `/bin` or `/usr/bin`

**Automatic cleanup NEVER touches these** - they are protected.

---

## Rule 8: OpenWebUI Memory Usage

**Normal memory usage**: 100-300MB idle, 500MB-1GB when using AI

**To check**:
```bash
ps aux | grep open-webui | grep -v grep
```

**Look at column 6** (memory in KB):
- Below 1,000,000 = Good (under 1GB)
- Above 2,000,000 = High (over 2GB), restart it

**To restart if using too much memory**:
```bash
systemctl --user restart open-webui
```

---

## Rule 9: Git Repository Cleanup

**The wiki uses Git** to track changes. Git stores history.

**Automatic cleanup happens** but if disk is very full:

```bash
cd ~/wiki
git gc --aggressive --prune=now
```

**This takes 1-5 minutes**. It makes Git smaller without losing data.

---

## Rule 10: Emergency Disk Recovery

**If disk space is CRITICAL (>95% used)**:

**Step 1** - Run maintenance:
```bash
~/Documents/wiki-linux/wiki-linux/bin/wiki-system-maintenance
```

**Step 2** - Clear all cache:
```bash
rm -rf ~/.cache/*
```

**Step 3** - Remove unused Ollama models:
```bash
ollama list
ollama rm MODEL_NAME  # Pick largest unused one
```

**Step 4** - Check space again:
```bash
df -h /
```

**Repeat Step 3** until disk usage is below 85%.

---

## Simple Decision Tree

```
Is disk usage > 90%?
├─ YES → Run wiki-system-maintenance NOW
│        Then check Ollama models
│        Remove models you don't use
│
└─ NO  → Is disk usage > 85%?
         ├─ YES → Schedule cleanup this week
         │        Check which models you need
         │
         └─ NO  → System is healthy
                  Keep monitoring monthly
```

---

## Commands You Need to Remember

**Daily check** (5 seconds):
```bash
wiki-quick-check
```

**Manual cleanup** (60 seconds):
```bash
wiki-system-maintenance
```

**See models** (to remove if needed):
```bash
ollama list
wiki-ollama-optimize
```

**Emergency cache clear**:
```bash
rm -rf ~/.cache/*
```

---

## How to Know If Automatic Cleanup Works

**Check the timer**:
```bash
systemctl --user list-timers
```

**Look for**: `wiki-system-maintenance.timer`

**You should see**:
- NEXT: When it will run next
- LEFT: How much time until it runs

**If you see "n/a"**, the timer is broken. Fix it:
```bash
systemctl --user enable wiki-system-maintenance.timer
systemctl --user start wiki-system-maintenance.timer
```

---

## Logs: Where to Look for Problems

**Automatic cleanup logs**:
```bash
journalctl --user -u wiki-system-maintenance.service -n 50
```

**Manual run logs**:
```bash
ls -lt ~/.local/var/log/wiki-linux/
cat ~/.local/var/log/wiki-linux/maintenance-*.json
```

---

## Safety Checklist

Before deleting ANYTHING manually, ask:

1. ✓ Is this file in `.cache`? → SAFE to delete
2. ✓ Is this file ending in `.tmp` or `.bak`? → SAFE to delete
3. ✓ Is this an Ollama model I don't use? → SAFE to delete
4. ✗ Is this in `/etc` or `/usr`? → DO NOT DELETE
5. ✗ Is this in `~/wiki` content? → DO NOT DELETE
6. ✗ Am I not sure what it is? → DO NOT DELETE

**When in doubt, ask before deleting.**

---

## Monthly Maintenance Routine

**1st of every month**:

```bash
# Check disk
df -h /

# Check services
wiki-quick-check

# Check models
wiki-ollama-optimize

# Check logs
journalctl --user -u wiki-system-maintenance.service --since "30 days ago" | tail -20
```

**Write down disk usage** each month to spot trends.

---

## What Each File Size Means

- **KB** (kilobytes) = Very small, ignore
- **MB** (megabytes) = Small, many needed to matter
- **GB** (gigabytes) = Large, pay attention
  - 1-2GB = Worth checking
  - 5-10GB = Definitely review
  - 20GB+ = Major space consumer

**Current major consumers**:
- Ollama models: 21GB
- Git history: 14GB
- Cache: 5-10GB

---

## Success Indicators

**System is healthy when**:
- ✓ Disk usage below 85%
- ✓ Timer shows "active (waiting)"
- ✓ wiki-monitor service is active
- ✓ wiki-quick-check shows mostly ✓ symbols
- ✓ Free space is above 20GB

**Current status**: 29GB free ✓ GOOD

---

## Troubleshooting Simple Problems

**Problem**: Timer says "inactive"
**Solution**: `systemctl --user start wiki-system-maintenance.timer`

**Problem**: Disk suddenly full
**Solution**: Run `wiki-system-maintenance`, then check Ollama models

**Problem**: OpenWebUI uses too much memory
**Solution**: `systemctl --user restart open-webui`

**Problem**: Can't write to logs
**Solution**: Logs automatically go to `~/.local/var/log/wiki-linux/` instead

**Problem**: Maintenance takes too long
**Solution**: Normal. Git cleanup can take 60-120 seconds.

---

## Key Numbers to Remember

- **90%** disk usage = Time to clean up
- **95%** disk usage = URGENT cleanup
- **60 seconds** = How long maintenance takes
- **21GB** = Space used by Ollama models (can reduce)
- **29GB** = Current free space (adequate)
- **3:00 AM** = When automatic cleanup runs

---

## Final Simple Rules

1. **Check disk space once per day** (5 seconds)
2. **Let automatic cleanup run** (don't disable it)
3. **If disk >90%, run manual cleanup** (60 seconds)
4. **Review Ollama models monthly** (remove unused)
5. **Never delete files in /etc or ~/wiki** (protected)
6. **Keep 20GB+ free always** (system needs space)
7. **Ask if unsure** (better safe than sorry)

---

## One-Line Summary

**Run `wiki-quick-check` daily, let automatic cleanup handle the rest, remove unused Ollama models when disk reaches 90%.**

---

*This guide is written for small AI models and humans to understand easily.*
