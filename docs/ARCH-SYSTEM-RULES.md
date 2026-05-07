# Arch System Wiki Integration Rules
**Effective:** May 2, 2026 | **Status:** ENFORCED

## 🔐 Core Principles

From this date forward, all software and configurations on this Arch system follow wiki-linux rules:

1. **Everything is documented** — system changes must be reflected in `~/wiki/system/`
2. **Config is immutable** — `~/.config/wiki-linux/config.json` is read-only (444)
3. **/etc never changes** — snapshots verified daily by `wiki doctor`
4. **All writes are archived** — deleted pages stay in `_archive/`
5. **Git tracks everything** — auto-commit every 5 minutes via systemd timer
6. **User is always root** — daemon runs as login user, never sudo

## 🛠️ Software Requirements

### New Package Installation
When installing new software via `pacman`:
```bash
pacman -S <package>
# Document in: ~/wiki/system/packages.md
# Add config if needed to: ~/wiki/system/
```

### Configuration Changes
- Edit system files → documented in `~/wiki/system/<service>.md`
- Never modify configs outside wiki tracking
- Use `wiki sync` to commit changes

### LLM Awareness
All LLM interactions reference:
- Project schema: `~/wiki/AGENTS.md`, `~/wiki/CLAUDE.md`
- System config: `~/wiki/system/` 
- Ollama models: `mistral:latest`, `llama3.2:3b`, `qwen2.5-coder:3b`

## 🚀 UIs

### Primary: Open WebUI
- URL: http://127.0.0.1:8080
- RAG knowledge base: `~/wiki`
- Backend: Ollama at localhost:11434
- Features: Chat, embeddings, document search

### Secondary: Obsidian
- Vault: `~/wiki`
- Plugins: BMO Chatbot (→ Ollama), obsidian-git, smart-connections
- Use for: Graph view, daily notes, reference

## ✅ Verification

**Daily health check:**
```bash
wiki doctor    # 10-point safety audit
```

**Status:**
```bash
wiki status    # Daemon, disk, git, pages
```

**Disk recovery:**
```bash
wiki rescue --list    # Find orphaned docs
wiki rescue --auto    # Import stray files
```

## 📋 Permanent Integration

**Shell:** `~/.bashrc.d/wiki-integration` + `~/.zshrc`
```bash
export WIKI_ROOT=$HOME/wiki
export WIKI_CONFIG=$HOME/.config/wiki-linux/config.json
export OLLAMA_BASE_URL=http://localhost:11434
```

**Systemd:** Auto-start on reboot
```bash
systemctl --user enable wiki-monitor.service wiki-sync.timer
```

**Environment:** System-wide variables
```bash
~/.config/environment.d/wiki-linux.conf
```

## 🔒 Immutable Points

- ✓ Config file: 444 (read-only)
- ✓ /etc allowlist: hashed & verified
- ✓ Archive directory: never overwritten
- ✓ Git history: permanent, no force-push
- ✓ Daemon privilege: user-only, no sudo

## 🌐 External Integration

This Arch system's wiki is discoverable via:
1. **Obsidian:** `/home/sourov/wiki` (local vault)
2. **CLI:** `wiki` command dispatcher
3. **API:** Open WebUI (http://127.0.0.1:8080)
4. **LLM:** Ollama at localhost:11434
5. **Schema:** AGENTS.md, CLAUDE.md inside vault

---

**Initiated by:** Claude Code | **Branch:** wiki-arch | **Commits:** 6
