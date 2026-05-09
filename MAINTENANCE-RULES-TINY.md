# Wiki-Linux Maintenance (Ultra-Simple for Tiny LMs)

## What This System Does
- Monitors Linux system configs
- Creates wiki pages about them
- Needs disk space to work

---

## Most Important Rule

**Keep disk space above 10% free at all times.**

Current: 29GB free (13%) ✓ OK

---

## How to Check Disk Space

```bash
df -h /
```

Look at "Use%" column:
- **Below 85%** = Good
- **85-90%** = Watch closely  
- **90-95%** = Run cleanup
- **Above 95%** = URGENT

---

## Automatic Cleanup (Already Enabled)

Runs by itself:
- At boot (2 min after start)
- Daily at 3 AM

Removes:
- Python cache
- Old temp files (>1 day)
- Partial downloads
- Old cache (>14 days)

**No action needed** - it runs automatically.

---

## Manual Cleanup (When Disk Gets Full)

```bash
~/Documents/wiki-linux/wiki-linux/bin/wiki-system-maintenance
```

Takes 60 seconds. Cleans same things as automatic.

---

## Quick Status Check

```bash
~/Documents/wiki-linux/wiki-linux/bin/wiki-quick-check
```

Shows:
- Disk space
- Services status
- Ollama models
- OpenWebUI status

Look for ✓ (good) or ✗ (problem).

---

## Ollama Models (Big Space Users)

**Current**: 21GB (largest space user)

To see models:
```bash
ollama list
```

To remove unused model:
```bash
ollama rm MODEL_NAME
```

**Before removing**, run:
```bash
~/Documents/wiki-linux/wiki-linux/bin/wiki-ollama-optimize
```

This shows which models you have and recommends smaller ones.

---

## Never Delete These Folders

- `/home/sourov/wiki/` (wiki content)
- `/etc/` (system files)
- `~/Documents/wiki-linux/wiki-linux/` (this program)

Automatic cleanup never touches these.

---

## Emergency: Disk >95% Full

Run these in order:

1. Manual cleanup:
   ```bash
   wiki-system-maintenance
   ```

2. Clear cache:
   ```bash
   rm -rf ~/.cache/*
   ```

3. Remove Ollama models:
   ```bash
   ollama list
   ollama rm MODEL_NAME
   ```

4. Check disk:
   ```bash
   df -h /
   ```

Repeat step 3 until disk usage <85%.

---

## Service Status Check

```bash
systemctl --user status wiki-system-maintenance.timer
```

Should say: `Active: active (waiting)`

If it says `inactive`:
```bash
systemctl --user start wiki-system-maintenance.timer
```

---

## Commands Reference

| Task | Command | Time |
|------|---------|------|
| Check disk | `df -h /` | 1s |
| Quick status | `wiki-quick-check` | 2s |
| Manual cleanup | `wiki-system-maintenance` | 60s |
| List models | `ollama list` | 2s |
| Analyze models | `wiki-ollama-optimize` | 5s |

---

## Decision Logic

```
if disk_usage > 90%:
    run wiki-system-maintenance
    check ollama models
    remove unused models
else if disk_usage > 85%:
    plan cleanup this week
else:
    system is healthy
    check again next week
```

---

## Safety Rules

1. Only delete files in `.cache` or `.tmp`
2. Never delete files in `/etc` or `~/wiki`
3. Check with `wiki-ollama-optimize` before removing models
4. Keep 20GB+ free space
5. Ask if unsure

---

## Current Status Summary

| Item | Value | Status |
|------|-------|--------|
| Disk free | 29GB (13%) | ✓ OK |
| Disk used | 177GB (87%) | ⚠ Watch |
| Wiki pages | 31 | ✓ OK |
| Ollama models | 5 (21GB) | ⚠ Can reduce |
| Auto cleanup | Enabled | ✓ OK |
| Services | Running | ✓ OK |

---

## Files Created for You

1. `bin/wiki-system-maintenance` - Cleanup script
2. `bin/wiki-quick-check` - Status checker
3. `bin/wiki-ollama-optimize` - Model analyzer
4. `systemd/wiki-system-maintenance.timer` - Auto-runs cleanup

All working ✓

---

## One Command to Remember

```bash
wiki-quick-check
```

Run this daily. It shows everything you need to know.

---

## When to Act

- Disk >90% → Run cleanup NOW
- Disk >85% → Plan cleanup this week
- Disk <85% → Monitor monthly
- Services ✗ → Restart service
- OpenWebUI high memory → Restart it

---

*End of simple guide. For details, see MAINTENANCE-GUIDE.md*
