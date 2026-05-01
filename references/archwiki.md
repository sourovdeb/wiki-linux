# ArchWiki — Reference & Offline Install Guide

> **Why no copy in this repo:** the ArchWiki is several hundred MB, licensed
> GFDL 1.3, and changes daily. Bundling it would bloat the repo, get stale,
> and risk a license-attribution mismatch. The right answer is to install it
> locally on your Arch system using the official packages.

---

## Quick Install on Arch (offline ArchWiki in ~30 seconds)

```bash
# Lean version: terminal viewer, ~10MB, plain text
sudo pacman -S --needed arch-wiki-lite

# Full HTML version: browse with any browser, ~600MB-1.5GB
sudo pacman -S --needed arch-wiki-docs
```

After installation:

| Package | Where it lives | How to read |
|---|---|---|
| `arch-wiki-lite` | `/usr/share/doc/arch-wiki-lite` | `wiki-search <term>` (terminal) |
| `arch-wiki-docs` | `/usr/share/doc/arch-wiki/html/` | Open `index.html` in any browser |

Example — open the offline wiki in Firefox:

```bash
firefox /usr/share/doc/arch-wiki/html/en/index.html
```

Example — search the lite version for "systemd":

```bash
wiki-search systemd
```

---

## How wiki-linux Uses the ArchWiki

The wiki-linux daemon does **not** ingest the ArchWiki into your wiki.
The ArchWiki is a reference manual — your wiki is *your own knowledge*. Mixing
them defeats both. Specifically:

- The ArchWiki tells you **how Arch works in general**.
- Your wiki tells you **how YOUR machine is configured** and **what YOU have
  decided to do with it**.

What we do instead is **link to the ArchWiki from your wiki pages**. When
the LLM generates a wiki page about, say, `/etc/pacman.conf`, the page
includes:

```markdown
## See Also

- [ArchWiki: pacman.conf](https://wiki.archlinux.org/title/pacman/Package_signing)
- [ArchWiki: mirrors](https://wiki.archlinux.org/title/Mirrors)
```

If you have `arch-wiki-docs` installed, you can switch the system prompt in
`src/llm.py` to prefer local file paths instead:

```markdown
- [pacman.conf (local)](file:///usr/share/doc/arch-wiki/html/en/Pacman.html)
```

This works fully offline.

---

## Citing the ArchWiki in Your Wiki

If the LLM uses ArchWiki content as a source for a wiki page (rather than just
linking out), the page **must** include attribution per GFDL 1.3:

```yaml
---
title: My pacman setup
sources:
  - /etc/pacman.conf
  - https://wiki.archlinux.org/title/pacman (CC BY-SA 4.0 / GFDL 1.3)
license_note: |
  Portions derived from the ArchWiki, licensed GFDL 1.3.
  Original at https://wiki.archlinux.org/
---
```

The wiki-linux ingest agent's prompt should remind the LLM of this. See
`src/llm.py` SYSTEM_PROMPT.

---

## Useful ArchWiki Pages for Setting Up wiki-linux

These are the pages the wiki-linux agent will most often reference when
configuring an Arch system:

| Topic | ArchWiki link |
|---|---|
| General installation | https://wiki.archlinux.org/title/Installation_guide |
| pacman | https://wiki.archlinux.org/title/Pacman |
| systemd user services | https://wiki.archlinux.org/title/Systemd/User |
| inotify-tools | https://wiki.archlinux.org/title/Inotify |
| Ollama | https://wiki.archlinux.org/title/Ollama |
| Obsidian | https://wiki.archlinux.org/title/Obsidian (if exists) |
| Git | https://wiki.archlinux.org/title/Git |
| ripgrep | https://wiki.archlinux.org/title/Ripgrep (if exists) |
| XDG user dirs | https://wiki.archlinux.org/title/XDG_user_directories |

---

## Verifying ArchWiki Content (for the AI Agent)

When the AI agent quotes the ArchWiki to the user, it should:

1. Note which version it is referencing (live online vs. installed `arch-wiki-docs`)
2. Include the URL or local path
3. Note if local copy may be stale (`pacman -S arch-wiki-docs` to refresh)

Example agent line:

> "Per the ArchWiki page on systemd/User
> (https://wiki.archlinux.org/title/Systemd/User, accessed
> via your local arch-wiki-docs install), user services are stored in
> `~/.config/systemd/user/`."

This is the pattern the rest of wiki-linux's documentation follows.

---

## License of This File

This file (`references/archwiki.md`) is wiki-linux's own documentation about
the ArchWiki. It is MIT-licensed like the rest of this repo. The ArchWiki
itself is GFDL 1.3 / CC BY-SA 4.0 — see https://wiki.archlinux.org/ for the
full licence terms.
