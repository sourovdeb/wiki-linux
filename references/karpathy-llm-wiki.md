# LLM Wiki — Andrej Karpathy

> **Source:** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
> **Author:** Andrej Karpathy
> **Vendored here:** As reference material for the wiki-linux project.
> The original is the canonical version — check it for updates.
> This local copy lets agents read it offline and lets us reason about
> our implementation against the original spec without a network round-trip.

---

A pattern for building personal knowledge bases using LLMs.

This is an idea file. It is designed to be copy-pasted to your own LLM Agent
(e.g. OpenAI Codex, Claude Code, OpenCode / Pi, etc.). Its goal is to
communicate the high-level idea, but your agent will build out the specifics
in collaboration with you.

## The Problem with RAG

Most people's experience with LLMs and documents looks like RAG: you upload a
collection of files, the LLM retrieves relevant chunks at query time, and
generates an answer. This works, but the LLM is rediscovering knowledge from
scratch on every question. There's no accumulation. Ask a subtle question that
requires synthesizing five documents, and the LLM has to find and piece
together the relevant fragments every time. Nothing is built up.

NotebookLM, ChatGPT file uploads, and most RAG systems work this way.

## The Idea — A Persistent Compiled Wiki

The idea here is different. Instead of just retrieving from raw documents at
query time, the LLM **incrementally builds and maintains a persistent wiki** —
a structured, inter-linked Markdown directory.

When you add a new source, the LLM doesn't just index it for later retrieval.
It reads it, extracts the key information, and **integrates it into the
existing wiki** — updating entity pages, revising topic summaries, noting
where new data contradicts old claims, strengthening or challenging the
evolving synthesis. The knowledge is **compiled once and then kept current**,
not re-derived on every query.

This is the key difference: the wiki is a persistent, **compounding** artifact.
The cross-references are already there. The contradictions have already been
flagged. The synthesis already reflects everything you've read. The wiki keeps
getting richer with every source you add and every question you ask.

You never (or rarely) write the wiki yourself — the LLM writes and maintains
all of it. **You're in charge of sourcing, exploration, and asking the right
questions.** The LLM does all the grunt work — the summarising, cross-
referencing, filing, and bookkeeping that makes a knowledge base actually
useful over time.

In practice, you have the LLM agent open on one side and Obsidian (or any
Markdown viewer) on the other. The LLM makes edits based on your conversation,
and you browse the results in real time — following links, checking the graph
view, reading the updated pages.

> **Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.**

## The Three-Layer Architecture

```
LAYER 3 — THE SCHEMA  (CLAUDE.md / AGENTS.md)
  Rules • Conventions • Workflows • How to ingest/query
  ↕ tells the LLM HOW to behave

LAYER 2 — THE WIKI  (the LLM owns this entirely)
  Entity pages • Concept pages • Overview pages • index.md • log.md
  ↑ LLM creates, links, updates, maintains

LAYER 1 — RAW SOURCES  (IMMUTABLE)
  PDFs • Markdown • Articles • Meeting notes • Anything you read
  ← You drop sources here. Never edited.
```

### Layer 1 — Raw Sources (`raw/`)

Your input material. Drop articles, PDFs, transcripts, papers, notes here.
Organised in any way that makes sense to you (by topic, by date, by source).
**Immutable** — never edited by the LLM. Your source of truth.

### Layer 2 — The Wiki (`wiki/`)

A directory of Markdown pages the LLM owns entirely. Categories you'll see:

- **Entity pages** — one per person, place, paper, project, concept
- **Topic pages** — synthesis of a theme across many sources
- **Index pages** — `index.md` for the table of contents
- **Log** — `log.md` as an append-only record of operations

Cross-links use `[[wikilinks]]` so the wiki opens cleanly in Obsidian or any
Markdown viewer with link support.

### Layer 3 — The Schema (`CLAUDE.md` or `AGENTS.md`)

A document that tells the LLM how the wiki is structured, what the conventions
are, and what workflows to follow when ingesting sources, answering questions,
or maintaining the wiki. **This is the key configuration file** — it's what
makes the LLM a disciplined wiki maintainer rather than a generic chatbot.

## The Three Operations

### 1. **Ingest** — Process a new source
```
> I added a new article to raw/articles/. Please ingest it.
```
The LLM reads the source, extracts entities and concepts, finds existing
related pages in the wiki, updates them, and creates new pages where needed.
A single ingest can touch dozens of wiki pages.

### 2. **Query** — Ask a question
```
> What are the main critiques of approach X?
```
The LLM searches `index.md`, reads relevant pages, and synthesises an answer
using only what's in the wiki (which already reflects every source you've
ingested). If the answer is good, the LLM offers to file it back as a new
wiki page so the synthesis is preserved.

### 3. **Lint** — Health check
```
> Lint the wiki.
```
The LLM checks for broken links, orphan pages, contradictions, unsupported
claims (no source citation), and content gaps. It produces a report and
optionally fixes what it can.

## Use Cases

This pattern applies broadly:

- **Personal** — goals, health, psychology, self-improvement; filing journal
  entries, articles, podcast notes, building a structured picture of yourself
  over time.
- **Research** — going deep on a topic over weeks or months — papers,
  articles, reports, building a comprehensive wiki with an evolving thesis.
- **Reading a book** — filing each chapter, building pages for characters,
  themes, plot threads. By the end you have a rich companion wiki. Think
  Tolkien Gateway, but personal, automated.
- **Business / team** — internal wiki maintained by LLMs, fed by Slack
  threads, meeting transcripts, project documents, customer calls. Possibly
  with humans in the loop reviewing updates.
- Competitive analysis, due diligence, trip planning, course notes,
  hobby deep-dives — anything where you accumulate knowledge over time and
  want it organised rather than scattered.

## What Tools You Need

- **An LLM agent** with file-system access (Claude Code, OpenAI Codex,
  OpenCode, etc.)
- **A directory** for `raw/` and `wiki/`
- **A Markdown viewer** (Obsidian recommended for graph view; any editor
  works)
- **Git** (recommended) for history and backup

## How to Start

1. Create `raw/` and `wiki/` directories.
2. Copy this file to your LLM agent and say:
   > "Read this. Ask me what this wiki will be about and what sources I plan
   > to feed it. Once I answer, write me a `CLAUDE.md` (or `AGENTS.md`) schema
   > based on my answer."
3. Drop your first source into `raw/`.
4. Tell the agent to ingest it.
5. Iterate.

That's the whole pattern.

---

## Caveats (added by wiki-linux maintainers, not Karpathy)

This pattern is powerful but has real limits worth knowing:

- **Hallucinations are durable.** When the LLM gets something wrong and files
  it as a wiki page, that error is now part of the wiki's "knowledge". The
  immutable `raw/` layer is the safeguard — every claim should trace back to a
  source there. Run `lint` regularly to catch drift.
- **No human curation.** Unlike Wikipedia, no second human reviews edits. You
  are the editor; the LLM is the writer. Read what gets filed before trusting
  it.
- **Scale ceiling.** Karpathy's own wiki reportedly reached ~100 articles /
  ~400k words while remaining navigable. Past that, you may need automated
  consolidation, confidence scoring, or sub-wikis.
- **Provenance matters.** Every page should record which sources in `raw/`
  contributed to it (frontmatter `sources:` field). Without provenance, the
  wiki cannot be audited or corrected.

---

## How wiki-linux Implements This

The `wiki-linux` repository (this repo) implements the pattern with several
extensions:

1. **One-way mirror of `/etc`** — In addition to `raw/` (your documents), we
   also mirror selected system config files into `wiki/system/config/`. This
   gives you an LLM-maintained explanation of how your machine is set up.
2. **Local LLM** — We use Ollama so everything runs offline. No data leaves
   your machine.
3. **Auto-ingest agent** — `src/agent/ingest.py` scans `~/Downloads`,
   `~/Desktop`, `~/Documents`, and `~/code` for scattered files and proposes
   how to file them into the wiki. Useful for the messy-user starting state.
4. **Multi-platform** — Setup instructions for Linux, Windows, macOS, and
   GitHub Codespaces.
5. **Test-hardened** — Path-escape rejection and self-write debounce are
   covered by unit tests. The LLM cannot accidentally write outside `wiki/`.

See `WIKI_AGENT.md` for the detailed adaptation of Karpathy's pattern,
and `CLAUDE.md` / `AGENTS.md` for the schema this repo's agent uses.
