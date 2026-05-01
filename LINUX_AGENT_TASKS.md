# LINUX_AGENT_TASKS.md

> Read **WIKI_AGENT.md** first. This file is a checklist of concrete shell
> commands the agent runs during setup, plus the safe customisation moves
> that make the system feel wiki-native without breaking it.

---

## TARGET SYSTEMS

Arch (and derivatives), Debian/Ubuntu. Where commands differ, both forms
are given.

---

## TASK 1 — Vault and Git

```bash
WIKI_ROOT="${WIKI_ROOT:-$HOME/wiki}"

mkdir -p "$WIKI_ROOT"/{system/config,system/docs,user/notes,user/projects,user/research,_meta,raw}

cat > "$WIKI_ROOT/.gitignore" <<'EOF'
_tmp/
*.log
.DS_Store
EOF

cd "$WIKI_ROOT"
git init -b main >/dev/null
git add .gitignore
git commit -m "init: empty wiki" >/dev/null
echo "Vault created at $WIKI_ROOT"
```

## TASK 2 — Tool minimisation (audit first, remove second)

Audit first. Print the proposed list, wait for confirmation.

```bash
# Default removal proposals — agent must NOT execute without user OK.
cat <<'EOF'
Proposed removals (you will be asked to confirm each):

Arch:
  - cups, cups-pdf            (only if user does not print)
  - bluez, bluez-utils        (only if no Bluetooth devices)
  - gnome-software / discover (Obsidian + pacman cover the need)
  - manpages-XX                (large locale-specific man pages)

Debian/Ubuntu:
  - snapd                     (if flatpak or pacman-style preferred)
  - apport                    (crash reporter, often unwanted)
  - gnome-software            (CLI + Obsidian preferred)
  - thunderbird               (most users use webmail)

Cross-platform candidates the user usually does not need:
  - libreoffice-*             (if user only uses Markdown/web)
  - games-*, *-games

DO NOT auto-remove. Print list, ask: "Remove which?"
EOF
```

After confirmation:

```bash
# Arch
sudo pacman -Rns "$@"

# Debian/Ubuntu
sudo apt-get purge "$@" && sudo apt-get autoremove
```

## TASK 3 — Install the wiki tools

The minimum useful set. Anything else is the user's choice.

```bash
# Arch
sudo pacman -S --needed git ripgrep glow ollama obsidian

# Debian/Ubuntu (some via flatpak/snap)
sudo apt install -y git ripgrep
sudo snap install obsidian glow
# Ollama: curl -fsSL https://ollama.com/install.sh | sh
```

Pull the model:

```bash
systemctl enable --now ollama
ollama pull mistral        # or: llama3.2 / phi3 / tinyllama
```

## TASK 4 — XDG user directories (safe folder renames)

Linux supports renaming the visible names of `~/Documents`, `~/Downloads`,
etc. without moving the underlying paths the user expects. Edit
`~/.config/user-dirs.dirs` — this is the official mechanism.

```bash
mkdir -p "$HOME/Inbox" "$HOME/Notes" "$HOME/Archive"

cat > "$HOME/.config/user-dirs.dirs" <<EOF
XDG_DESKTOP_DIR="\$HOME/Desktop"
XDG_DOWNLOAD_DIR="\$HOME/Inbox"
XDG_DOCUMENTS_DIR="\$HOME/Notes"
XDG_MUSIC_DIR="\$HOME/Media/Music"
XDG_PICTURES_DIR="\$HOME/Media/Pictures"
XDG_VIDEOS_DIR="\$HOME/Media/Videos"
XDG_PUBLICSHARE_DIR="\$HOME/Archive"
XDG_TEMPLATES_DIR="\$HOME/.templates"
EOF

xdg-user-dirs-update
```

The actual `~/wiki` directory is *separate from* XDG dirs. Keep it that
way. Symlink it onto the desktop and into the file manager sidebar
instead of overloading XDG.

```bash
ln -sf "$HOME/wiki" "$HOME/Desktop/Wiki" 2>/dev/null || true
# GNOME Files / Nautilus sidebar bookmarks:
echo "file://$HOME/wiki Wiki" >> "$HOME/.config/gtk-3.0/bookmarks"
```

## TASK 5 — File manager default location

Open the file manager to `~/wiki` by default.

GNOME / Nautilus:

```bash
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/wiki-opener.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Open Wiki
Exec=xdg-open $HOME/wiki
NoDisplay=true
EOF
```

KDE Plasma — set Dolphin's default location through Settings → Startup,
or write `~/.config/dolphinrc`:

```bash
mkdir -p "$HOME/.config"
cat >> "$HOME/.config/dolphinrc" <<EOF

[General]
HomeUrl=$HOME/wiki
RememberOpenedTabs=false
EOF
```

## TASK 6 — Obsidian vault registration

Obsidian stores its vault registry in
`~/.config/obsidian/obsidian.json`. Add `~/wiki` as the default vault:

```bash
OBSIDIAN_CONFIG="$HOME/.config/obsidian/obsidian.json"
mkdir -p "$(dirname "$OBSIDIAN_CONFIG")"

# If file does not exist, create it minimally; otherwise let user edit.
if [ ! -f "$OBSIDIAN_CONFIG" ]; then
  cat > "$OBSIDIAN_CONFIG" <<EOF
{
  "vaults": {
    "wiki": {
      "path": "$HOME/wiki",
      "ts": $(date +%s%3N),
      "open": true
    }
  }
}
EOF
fi
```

## TASK 7 — Shell integration

Add a `wiki` alias and a `cdwiki` shortcut. These are the only OS-level
"wiki commands" the user needs to remember.

```bash
WIKI_RC_LINE='# wiki-os shortcuts
alias wiki="cd $HOME/wiki && ls"
cdwiki() { cd "$HOME/wiki/${1:-}"; }
export WIKI_ROOT="$HOME/wiki"'

case "$SHELL" in
  *bash) echo "$WIKI_RC_LINE" >> "$HOME/.bashrc" ;;
  *zsh)  echo "$WIKI_RC_LINE" >> "$HOME/.zshrc"  ;;
  *fish) printf '%s\n' \
           "set -gx WIKI_ROOT $HOME/wiki" \
           "alias wiki='cd $HOME/wiki && ls'" \
           >> "$HOME/.config/fish/config.fish" ;;
esac
```

## TASK 8 — Notification helper

See **SUPPORT_POPUP.md**. Install `wiki-notify` (a 30-line wrapper around
`notify-send` on Linux). Make sure `libnotify` is installed:

```bash
sudo pacman -S libnotify     # Arch
sudo apt install libnotify-bin   # Debian/Ubuntu
```

## TASK 9 — Confirmation, then commit

After all tasks finish, commit the vault:

```bash
cd "$WIKI_ROOT"
git add -A
git commit -m "init: vault structure, schema, AGENTS.md" || true
```

Run `wiki-notify` to tell the user setup is complete:

```bash
wiki-notify "Wiki setup complete" "Open Obsidian to start using your vault."
```

---

## WHAT THIS DOES NOT TOUCH

- `/etc` — never modified, only mirrored.
- `/usr`, `/var`, `/lib` — never modified.
- The kernel, init system, package manager — never modified.
- Existing dotfiles (`.bashrc`, `.zshrc`) — only **appended** to, never
  rewritten. If a backup is needed, the agent makes one first
  (`.bashrc.pre-wiki`).

If the agent finds itself wanting to do anything outside this list, it
stops and asks.
