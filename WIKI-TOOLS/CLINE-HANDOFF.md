# CLINE HANDOFF — Continue Wiki-Linux Setup

**Context:** Claude (Opus) ran out of tokens mid-task. Below is the exact state and remaining work. Each step has a script to run; verify after each one.

---

## What's Already Done ✅

1. **Toleria removed** (binary + launchers + autostart)
2. **Obsidian installed** (`/usr/bin/obsidian`)
3. **OBS Studio installed** (`/usr/bin/obs`)
4. **openai-whisper installed** (`~/.local/bin/whisper`)
5. **Obsidian configured** — opens `~/wiki` by default; BMO Chatbot plugin installed at `~/wiki/.obsidian/plugins/bmo-chatbot/` and configured to use `http://localhost:11434` with mistral as default model
6. **Obsidian autostart fullscreen** — `~/.config/autostart/obsidian-wiki.desktop`
7. **Indexer date-comparison bug fixed** in `src/indexer.py`
8. **wiki-monitor daemon** running, ollama active with 4 models

---

## What's Left — Run These Scripts In Order

All scripts live under `/home/sourov/Desktop/WIKI-TOOLS/handoff/`. Run them as the `sourov` user (not root) unless noted.

### Step A — XFCE Desktop = Wiki Folder (Windows-like)

```bash
bash ~/Desktop/WIKI-TOOLS/handoff/01-xfce-desktop-as-wiki.sh
```

What it does: points `xfdesktop` at `~/wiki/` so the desktop shows wiki folders/notes directly. Adds Thunar custom action to open any wiki file in Obsidian.

### Step B — Welcome Assistance Popup at Login

```bash
bash ~/Desktop/WIKI-TOOLS/handoff/02-welcome-popup.sh
```

What it does: replaces the old `wiki-welcome.desktop` autostart with a richer zenity dialog offering: "Open Obsidian", "Ask Ollama", "New Note", "Record audio (whisper)", "OBS screen-record", "System status".

### Step C — Audio Transcription Pipeline (Whisper → Wiki)

```bash
bash ~/Desktop/WIKI-TOOLS/handoff/03-whisper-pipeline.sh
```

What it does: installs `~/.local/bin/wiki-transcribe` (records via `arecord`, transcribes with `whisper`, writes the result as a new wiki page in `~/wiki/user/transcripts/`). Adds a desktop launcher.

Test: `wiki-transcribe` (Ctrl+C to stop recording, transcript appears in vault).

### Step D — Trim Background Services (Lightweight Mode)

```bash
bash ~/Desktop/WIKI-TOOLS/handoff/04-trim-services.sh
```

What it does: surveys enabled user + system services, disables a vetted list of non-essentials (bluetooth if no devices, cups if no printer, ModemManager, packagekit, geoclue, tracker3-miner). **Review the diff it prints before answering `y`.** It does NOT touch wiki-monitor, ollama, NetworkManager, dbus, pipewire.

### Step E — AI-Augmented Browsers (Comet-style)

```bash
bash ~/Desktop/WIKI-TOOLS/handoff/05-ai-browsers.sh
```

What it does:
- Firefox: enables built-in AI sidebar (`browser.ml.chat.enabled = true`), sets provider to localhost Ollama via the `localhost:11434` endpoint, installs Sidebery + a Perplexity-style search redirect.
- Chromium: writes a managed-policy file enabling the sidepanel + adds a desktop launcher that runs Chromium with `--enable-features=SidePanelPinning` and an Ollama-bridge bookmarklet.
- Drops a `~/.local/bin/ask-ollama` CLI used by both browsers as the URL-handler `ollama:?q=...`.

Note: the closest free equivalent to Comet (Perplexity's browser) is **Brave with Leo** (`yay -S brave-bin`) — the script offers an optional install of Brave that uses Ollama as Leo's local backend.

### Step F — Update Master Setup Doc

```bash
bash ~/Desktop/WIKI-TOOLS/handoff/06-update-summary.sh
```

What it does: rewrites `~/Desktop/WIKI-TOOLS/FINAL-SETUP-SUMMARY.md` to drop all Toleria/Open-WebUI references, add Obsidian/OBS/whisper/AI-browser sections, and refresh the architecture diagram.

### Step G — Final Verification

```bash
bash ~/Desktop/WIKI-TOOLS/handoff/07-verify.sh
```

Prints a green/red checklist. All green = done. Commit changes:

```bash
cd ~/Documents/wiki-linux/wiki-linux
git add -A
git commit -m "feat: replace Toleria with Obsidian; add OBS, whisper, AI-browser, lightweight services"
```

---

## Constraints to Respect

- **Never write to `/etc`** unless the user explicitly approves. Step D and E may need one sudo prompt — surface it before running.
- **Wiki vault is git-tracked**; any file you create in `~/wiki/` will be auto-committed by `wiki-sync.timer` within 5 min.
- **Don't disable**: `wiki-monitor`, `ollama`, `NetworkManager`, `dbus`, `pipewire`, `pipewire-pulse`, `wireplumber`, `xfce4-*`.
- The user wants the **desktop itself to be the wiki** — Step A is the load-bearing one. Verify visually after running it (log out + back in or `xfdesktop --reload`).

---

## Files You'll Be Editing/Creating

| Path | Purpose |
|---|---|
| `~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml` | desktop = ~/wiki |
| `~/.config/autostart/wiki-welcome.desktop` | rewritten popup |
| `~/.local/bin/wiki-transcribe` | new — whisper recorder |
| `~/.local/bin/wiki-welcome` | new — zenity popup |
| `~/.local/bin/ask-ollama` | new — browser ollama bridge |
| `~/.mozilla/firefox/*/user.js` | Firefox AI sidebar prefs |
| `~/Desktop/WIKI-TOOLS/FINAL-SETUP-SUMMARY.md` | rewritten |

---

## If You Get Stuck

- `journalctl --user -u wiki-monitor -n 50` — daemon logs
- `obsidian` in terminal — Obsidian errors print to stderr
- `whisper --help` — confirm whisper installed
- `xfconf-query -c xfce4-desktop -lv` — current desktop settings

Hand control back to the user once Step G is all green.
