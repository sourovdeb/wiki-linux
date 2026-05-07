# Open WebUI Prompts — 6 Templates

Copy each block below into Open WebUI → **Workspace → Prompts → Create New**.
Each one references its matching **Skill** and the matching **Tool** by name.

Open WebUI replaces `{{variable}}` placeholders with values entered at run time.
You can leave any field blank — the LM will use the skill's defaults.

---

## 1. Brainstorm — `/brainstorm`

**Title:** Brainstorm
**Command:** `/brainstorm`
**Description:** Generate a list of ideas using the Brainstorming skill.

**Prompt:**
```
Use the **Brainstorming** skill.

Topic: {{topic}}
Goal: {{goal}}
Audience: {{audience}}
Constraints: {{constraints}}
Number of ideas: {{count}}

Step 1 — If the topic might already exist in my notes, call
`seed_from_wiki(topic="{{topic}}", count=3)` first to gather context.
Step 2 — Generate {{count}} numbered ideas (default 7 if blank).
Each: **bold name** — one-sentence pitch, max 25 words. Mix safe and bold.
Step 3 — End with: "Want me to expand any of these into a plan?"
Step 4 — If I say "save", call `save_idea_list(topic="{{topic}}", ideas=<the list>)`.
```

---

## 2. Fetch URL → Wiki → Summary — `/fetch`

**Title:** Fetch URL
**Command:** `/fetch`
**Description:** Fetch a webpage, save as clean Markdown to wiki, return a bullet summary.

**Prompt:**
```
Use the **Web Search** skill, branch C (URL fetch).

URL: {{url}}
Save as filename: {{filename}}
Folder under wiki: {{folder}}

Step 1 — Call `fetch_url_as_markdown(url="{{url}}", save_as="{{filename}}", folder="{{folder}}")`.
Step 2 — Confirm the saved path on one line.
Step 3 — Summarise the page in 3–5 bullet points. One main idea per bullet, max 20 words each.
Step 4 — End with: "Source: <domain>".

Do not paraphrase more than ~15 words verbatim from the page. Cite the domain only.
```

---

## 3. Code — `/code`

**Title:** Code
**Command:** `/code`
**Description:** Write, save, and (optionally) lint a snippet using the Code skill.

**Prompt:**
```
Use the **Code** skill, Task A (Generate).

Language: {{language}}
Task: {{task}}
Inputs: {{inputs}}
Expected output: {{output}}
Save as filename (optional): {{filename}}

Step 1 — Write the smallest version that solves the task.
Step 2 — Include imports + ONE example call with expected output as a comment.
Step 3 — If `{{filename}}` is given, call
`save_snippet(filename="{{filename}}", language="{{language}}", code=<your code>)`.
Step 4 — If language is python, call `lint_python(code=<your code>)` and report any issues.
Step 5 — One-line note about any assumption you made.

No try/except, no logging, no docstrings unless I asked.
```

---

## 4. Content — `/content`

**Title:** Content Draft
**Command:** `/content`
**Description:** Produce platform-ready content using the Content Creation skill.

**Prompt:**
```
Use the **Content Creation** skill.

Platform: {{platform}}
Format: {{format}}
Topic: {{topic}}
Audience: {{audience}}
Tone: {{tone}}
Goal: {{goal}}
Length (or "default"): {{length}}

Step 1 — Apply platform conventions from the skill table.
Step 2 — Structure: Hook → Value → CTA. One clear CTA only.
Step 3 — No banned phrases (delve, unlock, dive deep, in today's world, etc.).
Step 4 — Output the content with no preamble.
Step 5 — Call `save_draft(platform="{{platform}}", title="{{topic}}", content=<output>)`.
Step 6 — One-line note (max 15 words) on any assumption made.
```

---

## 5. Reflect — `/reflect`

**Title:** Reflect
**Command:** `/reflect`
**Description:** Talk something through using the Mental Health skill.

**Prompt:**
```
Use the **Mental Health** skill.

What's on my mind: {{topic}}
What I want from you: {{mode}}     (listen / think_through / suggest)
Mood (optional): {{mood}}

Step 1 — Acknowledge what I said in one sentence using my own words.
Step 2 — Match my mode:
  - listen → reflect, ask one open question, no advice.
  - think_through → ask one gentle open question.
  - suggest → offer at most 3 small ideas, one line each.
Step 3 — Keep the whole reply short. No platitudes. No banned phrases.
Step 4 — Only if I say "log this" or "save", call
`add_journal_entry(text=<my words>, mood="{{mood}}", tags="reflection")`.

Crisis check: if I mention wanting to die, self-harm, or harming others, drop the
normal flow and call `get_hotlines(country_code="{{country}}")`. Show the result,
ask "Are you safe right now?", and stay present.
```

---

## 6. Writing — `/write`

**Title:** Writing
**Command:** `/write`
**Description:** Edit, rewrite, draft, critique, summarise, or expand text using the Writing skill.

**Prompt:**
```
Use the **Writing** skill.

Task: {{task}}        (edit / rewrite / draft / critique / summarise / expand)
Direction: {{direction}}     (e.g., shorter, more formal, for beginners)
Audience: {{audience}}
Length: {{length}}

Text:
{{text}}

Step 1 — Run the task per the skill's branch (A–F).
Step 2 — Output the result with no preamble.
Step 3 — Call `check_banned_phrases(text=<output>)`. If any are flagged, fix and re-output.
Step 4 — If task is "edit" or "rewrite", also call `text_stats(text=<output>)` and
report: word count, avg sentence length, reading ease — on one line.
Step 5 — If I say "save", call
`save_versioned_draft(filename="{{filename}}", content=<output>)`.
```

---

## How to install in Open WebUI

1. **Workspace → Prompts → +** (or **Admin Panel → Prompts**).
2. For each block above:
   - Title = the title field
   - Command = the `/...` shortcut
   - Description = the description line
   - Content = paste everything inside the ```code``` block
3. Save.
4. In any chat, type the command (e.g., `/brainstorm`) — Open WebUI shows a form with the `{{variable}}` fields.

## How they wire together

```
User types  →  Prompt template (with {{vars}})
                ↓
              Small LM (Llama 3.2 3B / Qwen 2.5 3B)
                ↓
              Reads the matching SKILL.md from the knowledge base
                ↓
              Calls the matching Tool method (Python)
                ↓
              Returns answer + saved file path
```

The skill tells the LM **what to do**, the tool **does the parts the LM is bad at** (file I/O, paths, parsing), and the prompt **structures the user input** so the LM doesn't have to guess.
