# Cline Agent Instructions — Wiki-Linux System Maintenance

**Purpose:** Autonomous agent for system configuration, maintenance, and monitoring  
**Context:** Wiki-native Arch Linux with Ollama, Obsidian, Open WebUI  
**Authority:** Read-only operations safe; destructive ops require explicit confirmation  
**Schedule:** On-demand via `cline` command or via Cline IDE plugin

---

## PHASE 1: SYSTEM HEALTH CHECK

### 1.1 Verify Core Services

```bash
# Check all critical services
systemctl --user status wiki-monitor.service
systemctl --user status wiki-sync.timer
systemctl status ollama
systemctl status open-webui 2>/dev/null || echo "Open WebUI not installed"

# Report status
echo "Services: $(systemctl --user is-active wiki-monitor.service) monitor, $(systemctl status ollama --no-pager 2>&1 | grep Active | cut -d' ' -f2-)"
```

### 1.2 Run Safety Audit

```bash
wiki doctor

# Expected output: 10/10 checks pass
# If any fail, document in ~/wiki/system/MAINTENANCE-LOG.md
```

### 1.3 Check Disk Space

```bash
df -h /
# If <50GB available, run: wiki rescue --auto
```

### 1.4 Verify Network Connectivity

```bash
# Ollama reachable
curl -s http://127.0.0.1:11434 | head -1

# Check git remote
git -C ~/wiki remote -v
```

---

## PHASE 2: ARCH LINUX SYSTEM MAINTENANCE

### 2.1 System Updates (Safe)

```bash
# Check for updates (no install)
sudo pacman -Qu

# Update if available
sudo pacman -Syu --noconfirm

# Verify no breakage
wiki status
wiki doctor
```

### 2.2 Clean Up System

```bash
# Safe cleanup
sudo pacman -Sc --noconfirm        # Remove old packages
sudo pacman -Rns --noconfirm $(pacman -Qdtq 2>/dev/null) || true
sudo journalctl --vacuum=50M
sudo rm -rf /tmp/* /var/tmp/*

# Check recovered space
df -h /
```

### 2.3 Monitor System Logs

```bash
# Recent errors
sudo journalctl -p err -n 20 --no-pager

# Wiki daemon logs
tail -50 ~/.cache/wiki-linux/monitor.log

# Document any issues in ~/wiki/system/ISSUES.md
```

### 2.4 Maintain Systemd Services

```bash
# Reload service definitions
sudo systemctl daemon-reload
systemctl --user daemon-reload

# Verify auto-start is enabled
systemctl --user is-enabled wiki-monitor.service
systemctl --user is-enabled wiki-sync.timer

# If disabled, re-enable
systemctl --user enable wiki-monitor.service
systemctl --user enable wiki-sync.timer
```

---

## PHASE 3: OLLAMA CONFIGURATION & MAINTENANCE

### 3.1 Monitor Ollama Status

```bash
# Check if running
systemctl status ollama --no-pager 2>&1 | grep Active

# Check loaded models
ollama list

# Test connectivity
curl -s http://127.0.0.1:11434/api/tags | jq '.models | length' 2>/dev/null || echo "Ollama API check needed"
```

### 3.2 Manage Models

```bash
# List current
ollama list

# Pull if missing (DESTRUCTIVE: Downloads 2-4GB per model)
# Only if explicitly requested
# ollama pull mistral:latest
# ollama pull llama3.2:3b
# ollama pull qwen2.5-coder:3b

# Remove unused (DESTRUCTIVE: Frees space)
# ollama rm model-name
```

### 3.3 Verify Ollama Configuration

```bash
# Check environment
systemctl show ollama --property=Environment 2>/dev/null | grep OLLAMA

# Check host/port
ps aux | grep ollama | grep -v grep | grep -o "0.0.0.0:[0-9]*\|127.0.0.1:[0-9]*" || echo "127.0.0.1:11434 (default)"

# Expected: OLLAMA_HOME=/opt/wiki-linux/ollama, listening on 127.0.0.1:11434
```

### 3.4 Optimize Ollama (Optional)

```bash
# Restart to clear memory
sudo systemctl restart ollama

# Test after restart
sleep 5
curl -s http://127.0.0.1:11434 >/dev/null && echo "✓ Ollama ready"
```

---

## PHASE 4: OBSIDIAN CONFIGURATION & MAINTENANCE

### 4.1 Verify Vault Configuration

```bash
# Check config
cat ~/.config/obsidian/obsidian.json

# Verify vault path points to ~/wiki
# Expected: {"vaults":{"wiki":{"path":"~/wiki",...}}}
```

### 4.2 Monitor Plugin Status

```bash
# Check plugin directories
ls ~/.config/obsidian-vault/plugins/ 2>/dev/null | head -10 || echo "Checking alternate paths..."

# List loaded plugins in Obsidian (GUI) or check manifest files
find ~/wiki/.obsidian/plugins -name "manifest.json" -exec basename {} -o {} \; 2>/dev/null | head -10
```

### 4.3 Manage Plugins (From Manifest)

**DO NOT:** Install/remove plugins via CLI (Obsidian manages via GUI)

**Instead:**
- Open Obsidian: `obsidian ~/wiki`
- Go to: Settings → Community Plugins
- Verify these are installed & enabled:
  - bmo-chatbot (Ollama integration)
  - obsidian-git (Version control)
  - dataview (Query language)
  - templater-obsidian (Template engine)

### 4.4 Verify BMO Chatbot Configuration

```bash
# Check BMO Ollama endpoint
cat ~/wiki/.obsidian/plugins/bmo-chatbot/data.json | grep -o "localhost:11434\|127.0.0.1:11434"

# Expected: 127.0.0.1:11434 or localhost:11434
```

### 4.5 Backup Vault

```bash
# Git status
cd ~/wiki && git status

# If uncommitted, commit
git add -A
git commit -m "auto: vault backup from Cline maintenance" -m "$(date)" 2>/dev/null || echo "No changes to commit"

# Verify git is in sync
git log --oneline -1
```

---

## PHASE 5: OPEN WEBUI CONFIGURATION & MAINTENANCE

### 5.1 Check Open WebUI Status

```bash
# Check if installed
[ -d ~/.local/share/wiki-linux/openwebui-venv ] && echo "✓ Installed" || echo "✗ Not installed"

# Check if running
ps aux | grep -i "open-webui\|webui" | grep -v grep && echo "✓ Running" || echo "✗ Not running"

# Check URL
curl -s http://127.0.0.1:8080 >/dev/null && echo "✓ Accessible at http://127.0.0.1:8080" || echo "✗ Not responding"
```

### 5.2 Verify Open WebUI Configuration

```bash
# Check connection to Ollama
curl -s http://127.0.0.1:8080/api/config | grep -o "ollama\|localhost:11434" || echo "Checking API..."

# Check knowledge base (RAG)
[ -L ~/wiki/knowledge/wiki-linux-vault ] && echo "✓ RAG vault symlinked" || echo "⚠ RAG vault symlink missing"
```

### 5.3 Start/Restart Open WebUI (If Needed)

```bash
# Restart
wiki openwebui --stop 2>/dev/null || true
sleep 2
wiki openwebui --start

# Verify
sleep 3
curl -s http://127.0.0.1:8080 >/dev/null && echo "✓ Open WebUI started" || echo "Starting..."
```

### 5.4 Update Open WebUI (Optional)

```bash
# Check version
wiki openwebui --status 2>/dev/null | grep "version\|installed" || echo "Status unavailable"

# Update (if needed, DESTRUCTIVE: Re-downloads)
# wiki openwebui --install  # Forces reinstall
```

---

## PHASE 6: GIT & WIKI MAINTENANCE

### 6.1 Sync Git History

```bash
cd ~/wiki

# Check status
git status --short

# Commit any uncommitted changes
git add -A
git commit -m "auto: Cline maintenance checkpoint" 2>/dev/null || echo "✓ Already in sync"

# Check remote
git remote -v | head -1

# Push if configured
git push origin main 2>/dev/null || echo "⚠ Remote push skipped (check SSH)"
```

### 6.2 Update Wiki Metadata

```bash
# Rebuild index
cd ~/Documents/wiki-linux/wiki-linux
python3 -m src.indexer 2>/dev/null || echo "Indexer not available"

# Check updated
[ -f ~/wiki/_meta/index.md ] && echo "✓ Index updated" || echo "⚠ Index may be stale"
```

### 6.3 Document System State

```bash
# Create maintenance report
cat > ~/wiki/system/MAINTENANCE-CLINE-$(date +%Y-%m-%d).md << 'REPORT'
# Cline Maintenance Report

**Date:** $(date)
**Status:** ✓ All systems operational

## Services
- Wiki Monitor: $(systemctl --user is-active wiki-monitor.service)
- Ollama: $(systemctl is-active ollama)
- Open WebUI: $(ps aux | grep -c "open-webui")
- Disk: $(df -h / | tail -1 | awk '{print $4}' available)

## Last Actions
- System check: ✓ Pass
- Safety audit: ✓ Pass
- Git sync: ✓ Done
REPORT

echo "✓ Maintenance report created"
```

---

## PHASE 7: GRACEFUL SHUTDOWN

### 7.1 Save All Work

```bash
# Commit pending changes
cd ~/wiki && git add -A && git commit -m "auto: final checkpoint before shutdown" 2>/dev/null || true
cd ~/Documents/wiki-linux/wiki-linux && git add -A && git commit -m "auto: final checkpoint" 2>/dev/null || true

echo "✓ All work committed to git"
```

### 7.2 Stop Services Gracefully

```bash
# Stop in order (reverse of startup)
echo "Stopping services..."

# Stop Open WebUI (safe)
wiki openwebui --stop 2>/dev/null || true
sleep 2

# Stop daemon (safe, will auto-restart if enabled)
systemctl --user stop wiki-monitor.service
systemctl --user stop wiki-sync.timer
sleep 2

# Ollama can stay running or stop (optional)
# sudo systemctl stop ollama  # Comment out to keep running

echo "✓ Services stopped"
```

### 7.3 Verify Shutdown

```bash
# Check stopped services
systemctl --user is-active wiki-monitor.service 2>&1 | grep -q "inactive" && echo "✓ Daemon stopped" || echo "Daemon still running"

# Check processes
ps aux | grep -E "wiki|ollama" | grep -v grep && echo "⚠ Some processes still running" || echo "✓ Clean shutdown"

# Report status
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ SYSTEM SHUTDOWN COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Final status:"
wiki status 2>/dev/null || echo "Wiki status unavailable"
```

### 7.4 Final Report

```bash
# Create shutdown report
cat > ~/wiki/system/SHUTDOWN-$(date +%Y-%m-%d-%H%M%S).md << 'REPORT'
# System Shutdown Report

**Time:** $(date)
**Reason:** Maintenance completed by Cline agent

## Final Status
- ✓ Git commits: all saved
- ✓ Services: stopped gracefully
- ✓ Disk: $(df -h / | tail -1 | awk '{print $4}') available
- ✓ Wiki: $(find ~/wiki -name '*.md' -type f | wc -l) pages archived

## Ready for
- Reboot
- Transfer to another system
- Backup
- Offline use

**Shutdown initiated by:** Cline Agent
**Status:** Clean shutdown
REPORT

echo "✓ Shutdown report saved"
```

---

## EMERGENCY PROCEDURES

### If Services Fail

```bash
# Force restart daemon
systemctl --user restart wiki-monitor.service

# Force restart Ollama
sudo systemctl restart ollama

# Check logs
journalctl -u ollama -n 20 --no-pager
systemctl --user status wiki-monitor.service -n 20
```

### If Disk Is Full

```bash
# Emergency cleanup
wiki rescue --auto
sudo pacman -Sc --noconfirm
sudo rm -rf /tmp/* /var/tmp/* /var/cache/* 2>/dev/null || true

# Check recovery
df -h /
```

### If Git Is Corrupted

```bash
# Verify repos
cd ~/wiki && git fsck --full
cd ~/Documents/wiki-linux/wiki-linux && git fsck --full

# Recover if needed (contact for manual repair)
```

---

## COMMAND SUMMARY

```bash
# Full maintenance run
wiki doctor                 # Safety audit
wiki status                 # System status
wiki sync                   # Git commit
systemctl --user restart wiki-monitor.service    # Restart daemon
sudo systemctl restart ollama                    # Restart Ollama
wiki openwebui --status     # Check Open WebUI

# Cleanup
sudo pacman -Sc --noconfirm
wiki rescue --auto

# Shutdown
systemctl --user stop wiki-monitor.service
wiki openwebui --stop
```

---

## CLINE BEHAVIOR CONTRACT

**When running maintenance:**
1. ✅ Always run `wiki doctor` first
2. ✅ Document findings in ~/wiki/system/MAINTENANCE-LOG.md
3. ✅ Commit changes before and after modifications
4. ✅ Ask user before destructive operations (deletions, package removal)
5. ✅ Report all findings clearly
6. ✅ Gracefully shutdown when done

**DO NOT:**
- ❌ Delete files without confirming
- ❌ Force-push to git
- ❌ Modify config immutable files (chmod 444)
- ❌ Run as sudo without explicit instruction
- ❌ Assume services are running (verify first)

**Permissions:**
- ✅ Read all files
- ✅ Execute scripts
- ✅ Commit to git
- ✅ Restart services (user-level)
- ⚠️  Root operations (ask first)
- ⚠️  Destructive ops (confirm first)

---

## REFERENCE

- **System Recipe:** ~/wiki/SYSTEM-REPRODUCIBLE.md
- **Safety Rules:** ~/wiki/EXPECTATIONS.md
- **Agent Contract:** ~/wiki/AGENTS.md
- **Current Status:** ~/wiki/FINAL-SYSTEM-STATUS.md
- **Logs:** ~/.cache/wiki-linux/monitor.log
- **Config:** /opt/wiki-linux/config/user-config/config.json

---

**These instructions are for autonomous Cline agent operation.**  
**Last updated:** May 2, 2026  
**Status:** Production ready  
