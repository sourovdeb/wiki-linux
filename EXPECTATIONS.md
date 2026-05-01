# WHAT YOU'LL SEE — The Complete Visual & Structural Tour

> **This file answers:** After setup completes, what UI/folders/software will
> I interact with? What's protected from accidental deletion? Where are the
> locks?
>
> **Guarantee:** Root/config files are in read-only filesystem contexts.
> Wiki data is in Git (recoverable). Destructive operations require
> explicit confirmation or have `rm` aliased to move-to-archive.

---

## Part 1 — The Folder Structure You'll See

After setup, your home directory looks like this. Bold = new. Indentation = 
containment.

```
~/ (your home folder)
├── wiki/                          ← NEW — your wiki vault
│   ├── .git/                      ← Git history (PROTECTED — read-only at file level)
│   │   ├── objects/               ← Git object database
│   │   ├── refs/                  ← Branch pointers
│   │   └── HEAD                   ← Current branch
│   ├── system/                    ← System config mirrors (read by daemon)
│   │   ├── config/
│   │   │   ├── pacman.conf.md
│   │   │   ├── fstab.md
│   │   │   ├── sshd_config.md
│   │   │   └── ...
│   │   └── services/              ← systemd units explained
│   ├── user/                      ← Your notes (you own these)
│   │   ├── notes/
│   │   │   ├── my-networking.md
│   │   │   └── ...
│   │   ├── projects/
│   │   │   ├── home-lab.md
│   │   │   └── ...
│   │   ├── code-examples/
│   │   │   ├── python-server.md
│   │   │   └── ...
│   │   └── research/
│   ├── _meta/                     ← Auto-generated indices (LLM owns this)
│   │   ├── index.md               ← Table of contents
│   │   ├── recent.md              ← Newest changes
│   │   ├── log.md                 ← Append-only operation log
│   │   └── ...
│   ├── _tmp/                      ← Scratch space (ephemeral)
│   └── _archive/                  ← Deleted files go here (NOT destroyed)
│
├── .config/                       ← Your system config folder (Arch convention)
│   └── wiki-os/                   ← NEW — wiki daemon config
│       └── config.json            ← settings (LOCKED — see below)
│
├── .local/bin/                    ← Custom executables
│   └── wiki  →  ~/wiki-linux/bin/wiki   ← Symlink to CLI dispatcher
│
├── Downloads/                     ← (unchanged)
├── Documents/                     ← (unchanged)
├── Desktop/                       ← (unchanged)
└── ... (all your other folders unchanged)
```

### Key Observation

- **`~/wiki/`** is the **only** new folder the daemon touches
- **`~/.config/wiki-os/config.json`** is the **only** config it reads
- *Everything else in your home* stays untouched
- **`/etc`, `/usr/`, `/var/`, `/root/`** are never written to (read-only)

---

## Part 2 — The Software You'll Interact With (4 Tools)

After setup, you interact with exactly **4 things**:

### Tool 1: The `wiki` Command (CLI)

**Where you type it:** Any terminal

**What it does:** Dispatches to Python daemon or external tools

**Looks like:**
```bash
$ wiki new "My networking notes"
Created: ~/wiki/user/notes/my-networking.md

$ wiki ask "What is the OSI model?"
Searching wiki...
Found in system/teaching/osi-model.md:
[Answer synthesised from your wiki]

$ wiki search "systemd"
system/config/systemd.md — "How to enable user services..."
system/services/user-timers.md — "Timers that run as your user..."

$ wiki status
Daemon status: running (PID 12345)
Wiki size: 47 pages, 150 KB
Last sync: 2026-05-01 15:23:45 UTC
Git remote: origin (https://github.com/sourovdeb/wiki-linux.git)

$ wiki open
(Opens ~/wiki/ in your default editor or Obsidian)

$ wiki lint
Running health checks...
✓ No broken links
✓ All sources cited
⚠ Page "old-notes.md" not updated in 6 months
2 issues found. See ~/wiki/_meta/lint-report-2026-05-01.md
```

### Tool 2: Obsidian (GUI Optional)

**Where you get it:** `sudo pacman -S obsidian`

**What it does:** Visual markdown editor with graph view and link navigation

**Looks like:**
```
┌─ Obsidian ───────────────────────────────────────┐
│                                                   │
│  Left panel: File tree           │ Right panel:  │
│  - system/                       │ Outline       │
│    - config/                     │ - ## Summary  │
│      - pacman.conf.md ← click    │ - ## Key pts  │
│    - teaching/                   │ - ## See also │
│  - user/                         │               │
│  - _meta/                        │ Center:       │
│                                  │ Markdown      │
│  Search: "systemd" ← type        │ with          │
│  3 results found                 │ [[wikilinks]] │
│                                  │ highlighted   │
│ Graph view (toggle):             │ as clickable  │
│ 47 nodes, 120 connections        │ blue text     │
│ (visual network of your wiki)    │               │
└───────────────────────────────────────────────────┘
```

**Key**: Obsidian is **read-only for the daemon**. You edit here; the daemon
reads here. They don't fight.

### Tool 3: The Terminal (Text Interface)

**Where you see it:** Any terminal (`kitty`, `alacritty`, `gnome-terminal`, etc.)

**What shows up:** Daemon logs (in background), error messages, search results

```bash
$ systemctl --user status wiki-monitor
● wiki-monitor.service - Wiki-OS file monitor daemon
     Loaded: loaded (/etc/systemd/user/wiki-monitor.service; enabled; vendor preset: disabled)
     Active: active (running) since Wed 2026-05-01 10:15:00 UTC; 5h ago
   Main PID: 12345 (python3)
     Tasks: 1 (limit: 2350)
    Memory: 45.2M
    CGroup: /user.slice/user-1000.slice/user@1000.service/app.slice/wiki-monitor.service
            └─12345 /home/user/wiki-linux/.venv/bin/python3 -m src.monitor

May 01 10:15:00 arch-box systemd[815]: Started Wiki-OS file monitor daemon.
May 01 15:23:45 arch-box wiki-monitor[12345]: INGEST /etc/pacman.conf → wiki/system/config/pacman.conf.md
May 01 15:24:02 arch-box wiki-monitor[12345]: ✓ Ingest complete: 487 words written

$ tail -f ~/.local/share/wiki-os/monitor.log
[INFO] 2026-05-01T15:23:45 inotify event: CLOSE_WRITE wiki/system/config/pacman.conf.md
[INFO] 2026-05-01T15:23:45 Debounce suppression: self-write (5 sec window active)
```

### Tool 4: Git (Version Control)

**Where you use it:** `git commit`, `git push`, `git log`

**What you see:**
```bash
$ cd ~/wiki && git log --oneline | head -5
a1b2c3d auto: ingest /etc/pacman.conf
f4e5d6c user: add networking notes
7a8b9c0 auto: lint and cross-link
... (full history)

$ git push
Pushing to https://github.com/yourusername/wiki-linux.git
Everything up-to-date
```

---

## Part 3 — What You'll See on Your Filesystem Right Now (Before Setup)

```
~/.config/
├── (other apps...)

/etc/
├── pacman.conf
├── fstab
├── ssh/sshd_config
└── (all your current system config)

/usr/
└── (untouched)

/root/
└── (untouched — you don't edit as root)
```

## Part 4 — What You'll See After Setup (Changes Only)

```
~NEW~ ~/.config/wiki-os/
  └── config.json  (LOCKED — explained below)

~NEW~ ~/wiki/
  └── (directory structure from Part 1)

~NEW~ ~/.local/bin/wiki
  └── (symlink to dispatcher)

~CHANGED~ systemd user services (run as your login user):
  ├── wiki-monitor.service  (daemon watching files)
  ├── wiki-sync.service     (auto-commit to git)
  └── wiki-sync.timer       (runs sync every 5 min)

~UNCHANGED~
  /etc/                    (still exactly the same)
  /usr/                    (still exactly the same)
  /root/                   (still exactly the same)
  Your home (except above) (still exactly the same)
```

---

## Part 5 — Safety Guarantees (The Locks)

### Guarantee 1: Config Files Are Read-Only (Filesystem Lock)

**File:** `~/.config/wiki-os/config.json`

**Protection:**
```bash
# After install, this is the permission:
ls -l ~/.config/wiki-os/config.json
-r--r--r-- 1 user user  2048 May 01 10:00 config.json
         ↑
    read-only for owner

# Daemon reads it. Daemon does NOT write it.
# Even if daemon crashes with write request, OS rejects it.

# To edit it, you must explicitly:
chmod u+w ~/.config/wiki-os/config.json
$EDITOR ~/.config/wiki-os/config.json
chmod u-r ~/.config/wiki-os/config.json  # re-lock

# OR use: install-time script (kept for rollback)
bash ~/wiki-linux/install.sh --reconfigure
```

**Why this works:** OS kernel enforces read-only. No application can bypass
this (except if you are `root`, in which case you chose to).

### Guarantee 2: Git Tracks Everything (Commit Log Lock)

**Where:** `~/wiki/.git/`

**Protection:**
```bash
# Every change is committed with timestamp + message:
git -C ~/wiki log --oneline
a1b2c3d auto: ingest /etc/pacman.conf
f4e5d6c user: added notes
7a8b9c0 lint check passed

# You deleted a file by accident?
git -C ~/wiki checkout HEAD~1 -- wiki/user/notes/important.md
# File recovered. Gone files are in .git/objects/ forever.

# Even if your ~/wiki/ folder caught fire:
git -C ~/wiki remote -v
origin  https://github.com/yourusername/wiki-linux.git (fetch)
origin  https://github.com/yourusername/wiki-linux.git (push)

# Push to origin:
git -C ~/wiki push origin main
# Now it's on GitHub. Recoverable from there.
```

**Why this works:** Git is forensic. Every state is recoverable. Even if you
`rm -rf ~/wiki/`, the `.git/` folder (if backed up to GitHub) has everything.

### Guarantee 3: Destructive Operations Move to Archive (No Hard Delete)

**How it works:**

In the daemon code (`src/monitor.py`), deletion doesn't call `rm`:

```python
# WRONG (does NOT happen in this daemon):
os.remove(target_path)

# RIGHT (what actually happens):
target_path.rename(WIKI_ROOT / "_archive" / f"{target_path.name}.deleted.{timestamp}")
log.info(f"Archived {target_path} → _archive/")
```

**What you see:**
```bash
# You accidentally run:
rm ~/wiki/user/notes/important.md

# It's NOT gone. It's in:
ls -la ~/wiki/_archive/
important.md.deleted.2026-05-01T15-23-45Z

# You can recover it:
mv ~/wiki/_archive/important.md.deleted.* ~/wiki/user/notes/important.md
git add -A
git commit -m "restore: recovered important.md from archive"
```

**Why this works:** The filesystem doesn't actually delete anything. Files
move to a graveyard folder (`_archive/`). They're still in Git history too.

### Guarantee 4: `/etc` Is Never Touched (Read-Only by Design)

**How:**

The daemon's allowlist in `config.json` has this:

```json
{
  "monitor": {
    "etc_allowlist": [
      "/etc/pacman.conf",
      "/etc/fstab",
      "/etc/ssh/sshd_config"
    ]
  }
}
```

**What this means:**

```python
# Pseudo-code from src/monitor.py:
if event.path in etc_allowlist:
    content = read_file(event.path)  # READ only
    wiki_page = llm.generate(content)
    write_wiki_page(wiki_page)  # Write goes to ~/wiki/, NOT /etc/

# The LLM sees /etc/pacman.conf and generates wiki/system/config/pacman.conf.md
# /etc/ stays untouched. Always.
```

**Verification:**

```bash
# Check /etc hasn't changed:
stat /etc/pacman.conf
# (same mtime, same size, same content as before setup)

# Check the wiki has the mirror:
ls -l ~/wiki/system/config/pacman.conf.md
# (created by daemon, contains LLM-formatted explanation)
```

**Why this works:** One-way read. Source → derived. Never reverse.

### Guarantee 5: Systemd Service Runs As You, Not Root

**How:**

The systemd units live in `~/.config/systemd/user/`:

```bash
# NOT /etc/systemd/system/ (that's system-wide, requires root)

ls ~/.config/systemd/user/
wiki-monitor.service
wiki-sync.service
wiki-sync.timer

# Content:
cat ~/.config/systemd/user/wiki-monitor.service
[Service]
ExecStart=%h/wiki-linux/.venv/bin/python3 -m src.monitor
User=%u  ← Your login user, NOT root
WorkingDirectory=%h/wiki-linux
```

**Implications:**

- Daemon runs as your user, not as root
- Can't accidentally write to `/root/` or `/etc/`
- Can only touch files your user can touch
- If daemon crashes, it crashes unprivileged
- No `sudo` needed for normal operation

**Verification:**

```bash
ps aux | grep wiki-monitor
yourusername 12345  0.0  1.2  ...  python3 -m src.monitor
           ↑
    Not root. You.
```

### Guarantee 6: Config + Root Locked From Modification

**The Lock Chain:**

```
~/.config/wiki-os/config.json  (read-only: u-w)
    ↓ daemon reads (cannot modify)
~/.local/share/wiki-os/monitor.log  (append-only, owned by daemon)
    ↓ daemon writes here, nowhere else
~/wiki/  (git-tracked, recoverable)
    ↓ git history
GitHub remote (backed up off-machine)

/etc/  (never written)
/usr/  (never written)
/root/  (never touched)
```

**How to Verify It's Locked:**

```bash
# Try to write to config (should fail):
echo '{}' > ~/.config/wiki-os/config.json
bash: ~/.config/wiki-os/config.json: Permission denied

# Try to write to /etc (should fail):
echo 'hack' > /etc/pacman.conf
bash: /etc/pacman.conf: Permission denied

# Only writing that should work:
echo "my note" > ~/wiki/user/notes/test.md
# (succeeds — you own ~/wiki/)

git -C ~/wiki add -A
git -C ~/wiki commit -m "test note"
# (succeeds — you own .git/)
```

---

## Part 6 — The Rollback Guarantee

If something breaks, you can undo it:

### Option 1: Git Rollback

```bash
# Oops, the daemon wrote garbage to a page
# Undo the last commit:
git -C ~/wiki reset --hard HEAD~1

# Oops, multiple commits went wrong
# Go back to 1 hour ago:
git -C ~/wiki log --oneline --all
a1b2c3d HEAD (1 min ago — broken)
f4e5d6c (5 min ago)
7a8b9c0 (1 hour ago — good state)

git -C ~/wiki checkout 7a8b9c0
git -C ~/wiki reset --hard 7a8b9c0
```

### Option 2: Archive Restore

```bash
# File was accidentally deleted
ls -la ~/wiki/_archive/ | grep important
important.md.deleted.2026-05-01T15-23-45Z

mv ~/wiki/_archive/important.md.deleted.* ~/wiki/user/notes/important.md
```

### Option 3: Full Uninstall

```bash
# If the whole daemon is broken:
bash ~/wiki-linux/install.sh --uninstall

# What it does:
# - Disables systemd units
# - Removes ~/.config/wiki-os/
# - Leaves ~/wiki/ untouched (it's just markdown files + git)
# - Leaves /etc/ untouched (it was never modified)

# Your wiki is still there:
ls ~/wiki/
# Full history is still in .git/:
git -C ~/wiki log --oneline
```

---

## Part 7 — What's NOT Locked (and Why)

### Intentionally Editable

| Path | Why | Protection |
|---|---|---|
| `~/wiki/user/` | You write notes here | Git history |
| `~/wiki/system/config/*.md` | LLM writes mirrors | Git history |
| `~/.bashrc` | You may add `source ~/.config/wiki-os/init.sh` | You own it |

### Intentionally Read-Only (Immutable)

| Path | Why | Protection |
|---|---|---|
| `/etc/` | System config | OS permission bits |
| `/usr/` | System packages | OS permission bits |
| `/root/` | Root home | OS permission bits (and daemon never sudo's) |
| `.git/objects/` | Commit history | Git integrity + filesystem readonly after commit |

---

## Part 8 — The Quick Reference Card

Print this. Post it on your wall.

```
GUARANTEE CHECKLIST

☐ Config locked read-only
  → chmod u-w ~/.config/wiki-os/config.json

☐ /etc/ never written
  → Read-only by design (one-way inotify)

☐ /usr/ never touched
  → Daemon doesn't run as root

☐ /root/ never accessed
  → Daemon is your user, not root

☐ Everything in Git
  → git -C ~/wiki log shows full history

☐ Deleted files recoverable
  → _archive/ has timestamps
  → .git/ has all states

☐ Rollback on demand
  → git reset --hard <commit>

☐ Uninstall keeps wiki
  → install.sh --uninstall leaves ~/wiki/ + .git/

YOUR DATA IS SAFE.
Even if daemon crashes, you have:
  1. Git history (local + GitHub)
  2. _archive/ folder
  3. Original /etc files (untouched)
  4. All edits tracked + timestamped
```

---

## Part 9 — What If I Get Paranoid?

### "I don't trust this — can I air-gap the wiki?"

```bash
# Mirror to external drive:
cp -r ~/wiki /mnt/external-drive/wiki-backup-2026-05-01

# Or clone to another machine:
git clone https://github.com/yourusername/wiki-linux ~/wiki-backup

# Or print the index:
cat ~/wiki/_meta/index.md | lp  # print to printer
```

### "Can I verify nothing was written to /etc?"

```bash
# Before setup, record /etc hashes:
find /etc -type f -exec sha256sum {} \; > /tmp/etc-hashes-before.txt

# After setup (several weeks later):
find /etc -type f -exec sha256sum {} \; > /tmp/etc-hashes-after.txt

# Compare:
diff /tmp/etc-hashes-before.txt /tmp/etc-hashes-after.txt
# (should be empty — /etc unchanged by daemon)
```

### "Can I audit the daemon's every action?"

```bash
# All operations logged:
tail -100 ~/.local/share/wiki-os/monitor.log

# All wiki changes in git:
git -C ~/wiki log -p -- wiki/system/config/ | less
# (shows every line added/removed with timestamp)
```

---

## Summary Table

| Category | What You See | What's Protected | How |
|---|---|---|---|
| **Folders** | `~/wiki/` + `~/.config/wiki-os/` | `/etc/`, `/usr/`, `/root/` | Read-only by daemon design |
| **Files** | Markdown notes + config.json | config.json (read-only) | `chmod u-w` + OS enforces |
| **Tools** | `wiki` CLI, Obsidian, Git, terminal | None (tools are safe) | Used by you, not daemon |
| **Data** | Notes in `~/wiki/` | Full history in `.git/` | Git tracks all changes |
| **Deletion** | Files move to `_archive/` | Nothing is hard-deleted | Recoverable from archive + git |
| **Recovery** | `git reset`, `_archive/` folder | Everything recoverable | Git + timestamped archive |

---

## The One-Sentence Guarantee

> **Everything you write is in Git (recoverable), nothing in `/etc` is touched
> (read-only by design), and there's an `_archive/` folder so accidental
> deletions aren't actually deletions.**

That's it.
