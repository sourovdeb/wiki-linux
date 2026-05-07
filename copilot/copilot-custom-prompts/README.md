# Open WebUI Setup — Skills + Prompts + Tools

Three layers that work together for small LMs (Llama 3.2 3B, Qwen 2.5 3B):

```
prompts/  →  fills in {{vars}} from the user
skills/   →  rules the LM follows (loaded as Knowledge)
tools/    →  Python that does the file I/O the LM is bad at
```

## Install

### 1. Skills → Knowledge base
- **Workspace → Knowledge → Create**, name it e.g. `core-skills`.
- Upload all 6 files from `skills/`.
- In each Model you want to use them with: **Workspace → Models → edit → Knowledge → attach `core-skills`**.

### 2. Prompts → Prompts
- **Workspace → Prompts → +** for each block in `prompts/all-prompts.md`.
- Set the `/command`, title, and paste the prompt body.

### 3. Tools → Tools
- **Workspace → Tools → +**, paste each `.py` file from `tools/`.
- Save and **enable** each tool inside the Models you want them on.
- Dependencies: tool 02 wants `trafilatura` and/or `html2text` — install in the Open WebUI Python env (`pip install trafilatura html2text`). Falls back to stdlib if missing.
- Tool 01 (`wiki_brainstorm_seed`) needs `ripgrep` on the host (`apt install ripgrep`).

## Pairing

| Skill | Prompt | Tool |
|---|---|---|
| 01 brainstorming | `/brainstorm` | `wiki_brainstorm_seed` |
| 02 web-search | `/fetch` | `fetch_url_to_wiki` |
| 03 code | `/code` | `code_workspace` |
| 04 content-creation | `/content` | `content_drafts` |
| 05 mental-health | `/reflect` | `journal_and_hotlines` |
| 06 writing | `/write` | `writing_aids` |

## Paths used

- Wiki: `~/Documents/wiki-linux/wiki-linux/` (matches your existing setup)
  - `brainstorms/` — saved idea lists
  - `inbox/` — fetched URLs
  - `snippets/<lang>/` — saved code
  - `content/<platform>/` — drafts
  - `drafts/` — versioned writing drafts
- **Private journal**: `~/Documents/journal-private/` — outside the wiki, dir is `chmod 700`, files `chmod 600`. Keeps it out of any RAG indexing of the wiki.

## Notes for the small LM

- Knowledge retrieval is keyword-driven. Each skill file has a `triggers:` line in the frontmatter — these words help RAG match user intent to the right skill.
- Prompts pre-fill the structure; the skill enforces the rules; the tool removes the parts the LM would mess up (path handling, slugifying, file I/O).
- Mental-health crisis routing is duplicated in both skill 05 and the journal tool's `get_hotlines` — the LM should use the tool when in doubt rather than reciting from memory.
