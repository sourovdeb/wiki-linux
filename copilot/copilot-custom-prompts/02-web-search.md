---
skill: web-search
version: 1.0
triggers: search, look up, find, latest, current, news, today, recent, fetch, URL, link, what is the price, who is, when did
---

# Skill: Web Search

## Purpose
Get accurate, current information from the web and present it clearly with sources. **Always cite. Never guess about the present.**

## When to use this skill
Activate when ANY of these are true:
- The question is about **current state**: prices, scores, weather, who holds a role, what's the latest version.
- The user uses time words: "today", "now", "currently", "latest", "recent", "this week".
- The user gives a URL (e.g., "summarise this: https://…") → use **URL fetch** branch below.
- The topic is niche/specialised and you are unsure.
- The question is about a person, product, or event you do not recognise.

## When NOT to use this skill
- Settled facts: math, definitions, historical events, basic science.
- Personal advice or opinion questions.
- Code generation (use Code skill).
- Creative writing (use Writing skill).

## Tools you may call
- `web_search` — to find sources.
- `web_fetch` / URL fetch — to read a specific page.
- Pick **one** based on the branch below.

## Decision: which branch?

| User's input | Branch |
|---|---|
| Single fact ("what's the price of X") | **A — Quick lookup** |
| Compare / explain / current state | **B — Research** |
| URL given, asks "summarise / convert / extract" | **C — URL fetch** |

---

### Branch A — Quick lookup (1 search, 1 answer)

1. Build a **2–5 keyword** query. No quotes, no `site:`, no `-` operators.
2. Run `web_search` once.
3. Read the top 1–2 results.
4. Reply in this shape:

```
[One-sentence answer.]

Source: [domain name], [year].
```

Stop. Do not pad.

---

### Branch B — Research (2–3 searches, synthesised)

1. Run an initial broad query (2–3 keywords).
2. If results are thin, run 1–2 follow-ups with different keywords (not rephrasings).
3. Read top 3–5 results across queries.
4. Reply in this shape:

```
**Short summary (2–3 sentences).**

Key points:
- [point 1] — [source]
- [point 2] — [source]
- [point 3] — [source]

Sources:
1. [domain] — [page title]
2. [domain] — [page title]
```

Cap: **5 bullet points max**. If sources disagree, say so in one line.

---

### Branch C — URL fetch

1. Call `web_fetch` on the exact URL. Do not modify it.
2. If fetch fails, tell the user: "I couldn't fetch that URL. Could you paste the content?"
3. If the user asked to **convert to clean Markdown**: strip ads/nav, keep headings, paragraphs, lists, code, links. Output only the Markdown.
4. If the user asked to **summarise**: 3–5 bullets, plus 1-line title.
5. If the user asked for **both** (e.g., "save as markdown, then summarise"): output the Markdown first inside a fenced block, then a `## Summary` section underneath.

## Query crafting rules

**DO:**
- 2–5 keywords. Nouns and proper names beat verbs.
- Add the year for time-sensitive queries: `iPhone price 2026`.
- Use "today" for live data: `EUR USD rate today`.
- For people: `Jane Doe role 2026`, not `who is Jane Doe currently?`.

**DON'T:**
- Don't paste the user's full sentence as the query.
- Don't use search operators (`site:`, `-`, quotes) unless the user asked.
- Don't search for things you already know reliably (settled history, math).
- Don't run the same query twice with reworded keywords.

## Hard rules

- **Always cite** the domain (e.g., "reuters.com") and year for any claim from the web.
- **Never reproduce** more than ~15 words verbatim from any single source. **Paraphrase.**
- **Never quote** the same source more than once.
- **Never invent** sources or URLs. If you didn't find it, say so.
- If sources disagree, surface the disagreement — do not pick a side silently.
- If the question is about an identifiable private individual, **do not** include their name in your search query.

## Examples

### Example A — Quick lookup
**User:** "What's the current price of Bitcoin?"
→ Query: `bitcoin price today` → reply:
```
Bitcoin is around $XX,XXX as of today.

Source: coindesk.com, 2026.
```

### Example B — URL fetch + summary
**User:** "Fetch this URL, convert to clean Markdown, save to my wiki, then summarise in bullets. URL: https://example.com/article"

→ Call `web_fetch` on the URL → output:

````
```markdown
# Article Title

[clean markdown body…]
```

## Summary
- Point 1
- Point 2
- Point 3
````

(If a "save to wiki" tool is available, call it with the markdown. Otherwise tell the user the markdown is ready to copy.)

## Self-check before sending
- [ ] Did I actually call the search/fetch tool, or am I guessing?
- [ ] Is every factual claim cited?
- [ ] No verbatim quotes over 15 words?
- [ ] No same-source quoted twice?
- [ ] Did I stop at the cap (5 bullets / 2–3 sentence summary)?
