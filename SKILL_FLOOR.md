# SKILL_FLOOR.md — Plain-Language Setup for Non-Technical Users

> **Who this is for:** people who are not comfortable with the terminal,
> don't know what `~/wiki` means, and have never heard of "systemd".
>
> **Who this is NOT for:** developers — read `LINUX_AGENT_TASKS.md` instead.
>
> **The golden rule of this file:** every step is explicit. No assumed
> knowledge. If a button needs to be clicked, the file says which button. If a
> command needs to be typed, the file says where to type it.

---

## Before You Start — Computer Skills Self-Check

Tick the boxes you can already do. Things you can't tick are noted next to
each step below as "you'll need help with".

### 📁 Files & Folders

- [ ] I understand the difference between a **file** and a **folder**
- [ ] I can **create** a new file or folder
- [ ] I can **rename** files and folders
- [ ] I can **move** files between folders
- [ ] I can **delete** files and find them in Recycle Bin / Trash
- [ ] I recognise common file types (.docx, .pdf, .jpg, .md, .txt)
- [ ] I can **open**, **save**, and use **Save As**

### 🧭 Navigation & Organisation

- [ ] I can use File Explorer (Windows) or Finder (Mac) or Files (Linux)
- [ ] I know where to find **Desktop**, **Documents**, **Downloads**
- [ ] I can use the **search bar** to find files or apps
- [ ] I understand basic folder organisation

### 🖱️ Basic Actions

- [ ] I can **copy**, **cut**, and **paste** files or text
- [ ] I can use **right-click** for more options
- [ ] I know basic keyboard shortcuts (`Ctrl+C`, `Ctrl+V`, `Ctrl+S`)

### 🪟 Buttons & Interface

- [ ] I recognise **Close (X)**, **Minimise (_)**, **Maximise (□)**
- [ ] I can use **Back / Forward / Refresh**
- [ ] I recognise the **Settings** (gear) icon
- [ ] I can use menus (three dots / three lines)

### 🌐 Internet & Downloads

- [ ] I can download a file safely
- [ ] I know where downloaded files are saved
- [ ] I can open downloaded files

### ⚙️ Basic System Awareness

- [ ] I recognise Wi-Fi, battery, and volume icons
- [ ] I can install or uninstall simple applications

### 🆘 Things You'll Probably Need Help With

These are normal. Everyone needs help sometimes.

- [ ] Fixing errors or crashes
- [ ] Understanding where files are stored (file paths like `/home/me/wiki`)
- [ ] Managing storage space
- [ ] Installing complex software
- [ ] Dealing with viruses or suspicious files
- [ ] Setting up printers or Wi-Fi
- [ ] Backups (cloud vs local)
- [ ] Recovering lost files

---

## Setup Path — Pick One

There are **three ways** to use wiki-linux, listed easiest to hardest:

### 🌟 Easiest — GitHub Codespaces (works on phone, tablet, any computer)

You don't install anything. Everything runs in your web browser. **Choose
this if you ticked fewer than 5 boxes above.**

→ Jump to **Section A** below.

### Medium — Your Own Computer with an AI Helper

You install wiki-linux on your computer, but an AI agent (like Claude Code or
GitHub Copilot) does the typing for you. **Choose this if you have a
Mac/Linux/Windows machine and you've used an AI agent before.**

→ Jump to **Section B** below.

### Hardest — Manual Install on Arch Linux

You type every command yourself. **Choose this only if you've used the
terminal before and you're on Arch Linux.**

→ Read `LINUX_AGENT_TASKS.md` instead — that file is for you.

---

## Section A — GitHub Codespaces (Easiest)

### What You Need

- A GitHub account (free — sign up at https://github.com if you don't have one)
- A web browser (Chrome, Safari, Firefox, Edge — any modern one)
- An internet connection

That's it. **No installation on your computer.**

### Step-by-Step

#### A1. Open the wiki-linux repository

1. Open your web browser
2. Go to: **https://github.com/sourovdeb/wiki-linux**
3. If you're not signed in, click **Sign in** at the top right and sign in
   with your GitHub account

#### A2. Start a Codespace

1. On the wiki-linux page, find the green **`< > Code`** button (top right
   of the file list)
2. Click it. A small box appears.
3. In the box, click the **Codespaces** tab (next to "Local")
4. Click the green **Create codespace on main** button
5. **Wait 30–60 seconds.** A new browser tab opens showing what looks like
   a code editor. This is VS Code running in your browser.

#### A3. Wait for setup to finish

When the Codespace opens, the bottom panel shows messages like:

```
[1/5] Creating Python virtual environment...
[2/5] Installing dependencies...
[3/5] Setting up configuration...
[4/5] Initializing wiki git repository...
[5/5] Scanning home directory for knowledge to organize...
```

This takes another minute or two. Don't close the tab.

#### A4. Answer the setup question

When setup finishes, you'll see:

```
Would you like to scan ~/Downloads, ~/Desktop, ~/Documents? (y/n)
```

For your **first time**, type `n` and press **Enter**. (You haven't put any
files in yet, so there's nothing to scan.) Setup is done.

#### A5. Try your first command

In the bottom panel (the terminal), type:

```
wiki new "My first note"
```

Press **Enter**. A file opens. Type whatever you want. Save with `Ctrl+S`
(Windows / Linux) or `Cmd+S` (Mac).

#### A6. Close, come back later

You can close the tab any time. Your wiki is saved on GitHub. To come back:

1. Go to https://github.com/codespaces (in the browser)
2. Click the wiki-linux Codespace in the list
3. It re-opens exactly where you left off

#### A7. When you're done with this Codespace

GitHub gives you free Codespaces hours each month. To save your hours:

1. Go to https://github.com/codespaces
2. Find your wiki-linux Codespace
3. Click the **`...`** menu → **Stop codespace**

You can restart it any time. It's not deleted, just paused.

### What You Can Do in Codespaces

- ✅ Read and edit any file in the wiki
- ✅ Create new wiki pages with `wiki new "Title"`
- ✅ Search across all pages with `wiki search "term"`
- ✅ Auto-commit to Git (saves to GitHub automatically)
- ✅ Browse files in the left sidebar
- ❌ Run the live monitor daemon (Codespaces don't run systemd)
- ❌ Watch `/etc` system files (Codespaces is a container, not a real Arch box)

For the things that don't work in Codespaces, install on your real computer
later (Section B).

---

## Section B — Install on Your Computer with an AI Helper

This is for when you want wiki-linux running on your actual machine, watching
your real `/etc` files, with an offline LLM. The AI agent does the work; you
just answer questions and confirm.

### What You Need

- Your computer (any of: Arch Linux, Ubuntu/Debian Linux, macOS, Windows)
- An AI agent installed:
  - **Claude Code** — get from https://claude.com/claude-code
  - **GitHub Copilot in VS Code** — get from https://github.com/features/copilot
  - **OpenAI Codex** — see https://github.com/openai/codex
  - or any other agent that can read and write files
- Patience for ~15 minutes the first time

### Step-by-Step

#### B1. Make a folder for wiki-linux

Pick a place to put it. The simplest answer is your home folder. The
agent will tell you if it needs somewhere else.

#### B2. Open the AI agent

- **Claude Code** — open a terminal, type `claude`, press Enter
- **GitHub Copilot** — open VS Code, open the Chat panel (`Ctrl+Alt+I`)
- **Other agents** — start them however you normally do

#### B3. Tell the agent what to read

Copy and paste this **exact message** to the agent:

```
Please clone https://github.com/sourovdeb/wiki-linux into my home directory.
Then read these files in order:

1. WIKI_AGENT.md  (the master instruction file)
2. CLAUDE.md      (or AGENTS.md if you are Codex)
3. The platform file for my OS:
   - LINUX_AGENT_TASKS.md   if I'm on Linux
   - WINDOWS_AGENT_TASKS.md if I'm on Windows
   - MACOS_AGENT_TASKS.md   if I'm on macOS

After reading, do NOT make changes yet. Tell me what you understood and ask
me any questions you need answered before starting setup.

Important: do not skip the "non-negotiable invariants" section. Confirm you
will follow them.
```

#### B4. Answer the agent's questions

The agent will ask things like:

- *"What should the wiki be about?"* — Say what kinds of notes you'll keep.
- *"Which Ollama model do you want?"* — `mistral` is a safe default.
- *"Which `/etc` files should I watch?"* — Say "use the defaults from
  `config.json`" if unsure.
- *"Can I install these packages with `sudo`?"* — You'll need to answer yes
  the first time so it can install Ollama, ripgrep, etc.

The agent will **never** delete or rename system folders. If it ever asks to
do something that sounds dangerous, say no and ask why.

#### B5. Let it run setup

Once you've answered, say:

```
OK, please proceed with Phase 1 from WIKI_AGENT.md. Stop after each phase
and tell me what you did. Don't move to the next phase without my "go".
```

The agent will go phase by phase:

1. Initialise the wiki folder
2. Install Ollama and pull the model
3. Set up the daemon (the thing that watches files)
4. Install the `wiki` command
5. Optional: scan your messy folders and offer to organise them

#### B6. After setup — try it

In your terminal:

```bash
wiki new "My first note"
wiki ask "What is in my wiki so far?"
wiki status
```

You're done.

---

## Section C — When Something Breaks

### "I don't know where my Codespace went"

→ Go to https://github.com/codespaces — they're all listed there.

### "The AI agent can't find a file"

→ Tell the agent: *"Run `pwd` and `ls` and tell me what you see."* This shows
which folder the agent is in.

### "The setup script asks for `sudo` and I don't know what to do"

→ `sudo` means "do this as the administrator". On Linux/macOS, type your
login password when asked. The password won't be visible while you type — that
is normal.

### "I see lots of red error text"

→ Copy the **last 20 lines** of the error and paste them to your AI agent
with the message:

```
This error happened during wiki-linux setup. What does it mean and how do
I fix it?
```

### "I want to start over"

In Codespaces:

→ Stop and delete the Codespace at https://github.com/codespaces, then make a
new one.

On your computer:

→ Tell the agent: *"Please undo the wiki-linux setup. Use the rollback
section of `LINUX_AGENT_TASKS.md` (or the macOS / Windows equivalent)."*

### "I'm stuck and want a human"

→ Open an issue at https://github.com/sourovdeb/wiki-linux/issues

---

## Glossary — One Sentence Each

- **Repository (repo):** a folder of code stored on GitHub.
- **Clone:** copy a repo from GitHub onto your computer.
- **Git:** a tool that tracks every change to your files so you can go back
  if something breaks.
- **Terminal:** a window where you type commands instead of clicking.
- **Command:** an instruction you type into the terminal.
- **Path:** the address of a file or folder, like `/home/me/wiki`.
- **`~`** (tilde): shorthand for "my home folder".
- **`sudo`:** "do this as administrator" — needs your password.
- **Daemon:** a program that runs in the background watching for things.
- **Markdown:** plain text with simple formatting (`# heading`, `**bold**`).
- **LLM:** Large Language Model — an AI like Mistral, Llama, or Claude.
- **Ollama:** the tool that runs an LLM on your own computer (no cloud).
- **Wiki:** a collection of cross-linked notes, like Wikipedia.
- **Codespace:** a Linux computer that lives in your web browser.

---

## You Don't Have to Memorise Any of This

If you only remember **one** thing from this file, remember this:

> **Open https://github.com/sourovdeb/wiki-linux in your browser, click
> Code → Codespaces → Create codespace on main, and follow what the screen
> says.**

That's enough to start. Everything else, you can figure out as you go.
