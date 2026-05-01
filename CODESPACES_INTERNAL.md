# CODESPACES_INTERNAL.md — Internal Instructions for Codespaces Environment

> **Read by:** the agent running inside a GitHub Codespace, OR the agent
> setting up a Codespace for a user.
>
> **Why a separate file:** Codespaces are containers. They can't run
> `systemd`, can't watch the host's `/etc`, and have ephemeral filesystem
> outside `/workspaces/`. The other agent files assume a real OS. This file
> states the differences explicitly so smaller models don't crash trying to
> run `systemctl --user` and wondering why nothing works.
>
> **This file does NOT replace** `CODESPACES_AGENT.md`. That file is the
> high-level agent guide. This one is the operating-environment fact sheet.

---

## Section 1 — Environmental Facts (Read These First)

Inside a Codespace, the following statements are true. Treat them as axioms:

| Fact | Implication |
|---|---|
| The container is **Debian** (`ubuntu` user), not Arch | `pacman` doesn't exist. Use `apt-get` |
| There is **no real `/etc/`** to mirror | Don't enable the `etc_allowlist` here |
| `systemd` is **not running as PID 1** | `systemctl --user enable …` will fail |
| The container disk is **ephemeral outside `/workspaces/`** | Save everything inside the workspace |
| Network egress works to **GitHub, PyPI, npm, Ubuntu mirrors** | `pip install` works; `ollama pull` works if Ollama is installed |
| Default RAM: **2 GB** (free tier), **4–16 GB** (paid) | Mistral 7B needs ~5 GB. Use TinyLlama or remote Ollama on free tier |
| The user's home is `/home/codespace`, not `/home/<their-name>` | Use `$HOME`, never hardcode the username |
| GitHub credentials are **already configured** | `git push` works without prompting |

If any of these turn out to be false, **stop and tell the user** rather than
working around it silently. The environment may have been customised.

---

## Section 2 — What to Do (and Skip) in Setup

Reference: `.devcontainer/setup.sh` already runs the basics. After that
script finishes, here's what's done and what's left.

### Already Done by setup.sh

- ✓ Python 3.11 venv at `/workspaces/wiki-linux/.venv`
- ✓ `pip install -r requirements.txt`
- ✓ Wiki vault at `~/wiki/` with `system/`, `user/`, `_meta/`, `_tmp/`
- ✓ Git repo initialised in `~/wiki/`
- ✓ Initial commit
- ✓ Optional first-time scan of home (offered, may or may not have been run)

### Not Done — You May Need to Do These

| Step | When | How |
|---|---|---|
| Install Ollama | If user wants local LLM | `curl -fsSL https://ollama.com/install.sh \| sh` |
| Pull a model | After Ollama install | `ollama pull tinyllama` (free tier) or `ollama pull mistral` (paid) |
| Connect to remote Ollama | If running on free tier | Set `OLLAMA_HOST=https://<their-server>:11434` in `~/.bashrc` |
| Run the monitor | When user wants live updates | `cd /workspaces/wiki-linux && python3 -m src.monitor &` |
| Set up `wiki` CLI | First use | `ln -s /workspaces/wiki-linux/bin/wiki ~/.local/bin/wiki` (already added by setup.sh in most cases — verify with `which wiki`) |

### Never Do These in Codespaces

- ✗ Try to enable systemd units
- ✗ Mirror `/etc/` from the container (it's not the user's real `/etc`)
- ✗ Run `sudo apt-get install` for things already in `requirements.txt` (use pip instead)
- ✗ Modify files outside `/workspaces/` (they evaporate on rebuild)
- ✗ Run `rm -rf` on anything

---

## Section 3 — What the Agent Can Do RIGHT NOW for an Off-Computer User

Scenario: user is on their phone, will get to their Arch laptop in a few hours.
Agent is in Codespaces. What productive work can happen now?

### High-value work that does NOT need the user's laptop

1. **Customise `config.json`** — set the model name, set `etc_allowlist` to
   match what the user said they have (`/etc/pacman.conf`, `/etc/fstab`, etc.
   — those will be valid on their Arch box later).
2. **Write the AGENTS.md / CLAUDE.md schema** for their specific use case.
   Ask the user via chat: *"What are the topics this wiki will cover? What
   tone / depth? Any specific tags you'll use?"*
3. **Create starter wiki pages.** If the user described their interests,
   create a few empty topic pages with frontmatter so they have a skeleton.
4. **Write a `_meta/welcome.md`** explaining the structure to anyone (user
   or future agent) who opens the wiki.
5. **Update README.md, AGENT_PLAYBOOK.md, etc.** with project-specific
   tweaks the user requests.
6. **Run the test suite** to confirm nothing regressed: `pytest tests/`
7. **Commit and push** so when the user clones on Arch later, they get the
   customised version, not the generic template.

### Work to DEFER to the laptop

- Anything that touches a real `/etc/` file
- Anything that requires `systemd` (the daemon as a service)
- Pulling a 7B+ model (slow / RAM-bound on free Codespaces)
- Hardware-specific config (GPU, audio, printer)
- Setting up Obsidian (it's a desktop app)

---

## Section 4 — Explicit Walk-Through for the Agent

This is the script the agent should follow when invoked in a fresh Codespace
with no prior context. Run each step in order.

### Step 4.1 — Verify the environment

```bash
# Confirm we are where we think we are
pwd                    # expect /workspaces/wiki-linux
ls -la                 # expect README.md, src/, tests/, etc.
which python3          # expect /workspaces/wiki-linux/.venv/bin/python3
                       # OR /usr/bin/python3 if venv not active
cat /etc/os-release    # expect Ubuntu / Debian, NOT Arch
```

If any of these are wrong, stop and report.

### Step 4.2 — Verify setup.sh ran

```bash
ls -la ~/wiki                    # expect system/, user/, _meta/, _tmp/, .git/
git -C ~/wiki log --oneline -1   # expect "init: wiki vault initialised"
```

If `~/wiki` doesn't exist, run:

```bash
bash /workspaces/wiki-linux/.devcontainer/setup.sh
```

### Step 4.3 — Run the test suite

```bash
cd /workspaces/wiki-linux
PYTHONPATH=. .venv/bin/pytest tests/ -q
```

Expect: `16 passed`. If anything fails, **stop and report the failure
verbatim** to the user. Do not try to fix tests without permission.

### Step 4.4 — Ask the user what to customise

Send this exact message:

```
I'm in your Codespace and the setup is healthy. While you're on your phone,
I can prepare these things so they're ready when you reach your Arch box:

  1. Customise config.json to match your setup (which /etc files to watch,
     which Ollama model)
  2. Write a CLAUDE.md / AGENTS.md schema specific to your wiki's topic
  3. Create starter wiki pages from topics you care about
  4. Commit and push so cloning on Arch gets the customised version

Which of these do you want me to start on? (Type a number, or "all" for
all four in order.)
```

### Step 4.5 — Execute the chosen items

For each item the user picked, follow the standard flow from
`AGENT_PLAYBOOK.md` Section 2: classify → restate → plan → execute one step
→ report → wait.

### Step 4.6 — Commit and push at the end

```bash
cd /workspaces/wiki-linux
git add -A
git status              # show user what changed
git commit -m "agent: customise wiki for <user-name>'s setup"
git push origin main    # works because Codespaces has credentials
```

Confirm success:

```bash
git log origin/main --oneline -3
```

Tell the user: *"Pushed. When you `git clone https://github.com/sourovdeb/
wiki-linux ~/wiki-linux` on your Arch box, you'll get this customised
version."*

---

## Section 5 — When the User Gets Home (Hand-Off Note)

Generate this file before the agent's session ends, save as
`~/wiki/_meta/handoff.md`:

```markdown
---
title: Hand-Off — Codespaces to Arch
created: <ISO timestamp>
agent: <which agent ran this — Claude Code, Copilot, etc.>
---

# Hand-Off Note

The Codespace prepared the following for you:

- [ ] config.json customised at: <path>
- [ ] CLAUDE.md schema written (topic: <topic>)
- [ ] Starter wiki pages created at: <list of paths>
- [ ] All committed and pushed to origin/main (commit: <hash>)

## Your First Three Commands on Arch

```bash
# 1. Clone (this gets the customised version)
git clone https://github.com/sourovdeb/wiki-linux ~/wiki-linux

# 2. Run the installer (this is where we left off)
cd ~/wiki-linux && bash install.sh

# 3. After install finishes, enable services
systemctl --user enable --now wiki-monitor
systemctl --user enable --now wiki-sync.timer
```

## What's Different on Arch vs Codespaces

- The daemon will run as a systemd user service (not just a background process)
- /etc files in your config.json's etc_allowlist will actually be watched
- Ollama will run locally; you'll pull the model with `ollama pull <model>`
- Obsidian can open the wiki at ~/wiki

## If Something Doesn't Work

Open `LINUX_AGENT_TASKS.md` and follow Section 7 (Rollback / Troubleshooting).
Or paste this whole hand-off note plus your error to your AI agent and ask
for help.

## What This Codespace Did NOT Do

- Did not pull an Ollama model (do this on Arch: `ollama pull <model>`)
- Did not start the live monitor (do this with `systemctl --user enable
  --now wiki-monitor` on Arch)
- Did not install Obsidian (do `sudo pacman -S obsidian` on Arch)
```

---

## Section 6 — Resource Budget (free tier)

If the Codespace is on the free tier (2 vCPU / 8 GB RAM / 32 GB disk):

| Resource | Budget | Implication |
|---|---|---|
| RAM | ~6 GB usable | Don't pull Mistral 7B (uses ~5 GB just to load). Use TinyLlama 1.1B or Phi-3 Mini, or remote Ollama. |
| Disk | ~30 GB usable | Wiki + repo + venv = ~500 MB. Plenty unless you ingest huge PDFs. |
| Hours/month | 60 hours core, 15 GB-hours storage | Stop the Codespace when not using it. |
| CPU | 2 cores | Avoid heavy `pytest -n auto`. Single-threaded is fine. |

If the user has paid Codespaces (4–16 cores, more RAM), the agent can ignore
these limits and behave like a normal dev box.

---

## Section 7 — Self-Test for the Agent

Before declaring "ready", verify:

```bash
# 1. Tests pass
cd /workspaces/wiki-linux && PYTHONPATH=. .venv/bin/pytest tests/ -q

# 2. Wiki vault exists and is a git repo
test -d ~/wiki/.git && echo "✓ wiki is a git repo"

# 3. wiki CLI works
~/.local/bin/wiki --help 2>&1 | head -3 || /workspaces/wiki-linux/bin/wiki --help | head -3

# 4. No untracked changes that should be committed
git -C /workspaces/wiki-linux status --porcelain
```

Report each check `✓` or `✗`. Only say "ready" when all four are `✓`.

---

## Section 8 — One-Sentence Summary

> **In a Codespace, the agent prepares config and content; on Arch later,
> the user's agent installs the daemon. Hand off via `_meta/handoff.md`.**
