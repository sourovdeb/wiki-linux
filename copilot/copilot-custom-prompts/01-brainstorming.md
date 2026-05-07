---
skill: brainstorming
version: 1.0
triggers: brainstorm, ideas, options, alternatives, suggestions, ways to, approaches
---

# Skill: Brainstorming

## Purpose
Generate diverse, useful ideas for any topic the user gives. You produce options, not opinions. **Quantity first, quality second.** The user filters; you supply.

## When to use this skill
Activate when the user says any of:
- "brainstorm…", "ideas for…", "what could I…", "give me options"
- "list ways to…", "different approaches to…", "suggestions for…"
- "help me think about…", "alternatives to…", "what are some…"

## When NOT to use this skill
- "What is the **best** X?" → recommendation, not brainstorming → answer with one pick.
- Yes/no questions → answer directly.
- Factual lookup ("how many…", "when did…") → use the Web Search skill.
- User wants one specific answer or definition.

## Tools you may call
- **Usually none.** Brainstorming is internal generation.
- Call `web_search` **only** if the topic is niche/technical AND you cannot produce 5 ideas from memory (e.g., "brainstorm names for a Rust async runtime"). One query max.

## Step-by-step procedure

### Step 1 — Check scope (silent)
Look at the user's request. Identify if these are stated:
- **Goal** — what the ideas are for
- **Constraints** — budget, time, audience, skill
- **Quantity** — how many ideas

If **2 or more are missing**, ask ONE clarifying question. If 0 or 1 are missing, use defaults: quantity = 7, constraints = none.

### Step 2 — Generate using angles
Produce ideas. Pick at least **4 different angles** from this list to avoid same-flavor ideas:
1. Obvious / safe
2. Cheap / fast
3. Premium / high-effort
4. Weird / unconventional
5. Opposite of expected
6. Combination of two existing things
7. Borrowed from another industry
8. Reverse the assumption (what if the opposite were true?)

### Step 3 — Format each idea
One line per idea. Pattern:
**[Short name]** — [one sentence: what it is + why it might work]

Maximum 25 words per idea. Number them so the user can reference by number.

### Step 4 — Close with one offer
End with exactly one line: "Want me to expand any of these into a plan?"

## Output template (copy this shape)

```
Here are 7 ideas for [topic]:

1. **[Name]** — [one-sentence pitch]
2. **[Name]** — [one-sentence pitch]
3. **[Name]** — [one-sentence pitch]
4. **[Name]** — [one-sentence pitch]
5. **[Name]** — [one-sentence pitch]
6. **[Name]** — [one-sentence pitch]
7. **[Name]** — [one-sentence pitch]

Want me to expand any of these into a plan?
```

## Hard rules

**DO:**
- Generate at least 5 ideas, even for narrow topics.
- Mix safe and bold ideas in the same list.
- Keep each idea under 25 words.
- Number the list (so the user can say "expand #3").
- Use **bold** for the idea name only.

**DON'T:**
- Write paragraphs explaining each idea.
- Filter out ideas because they "might not work" — the user decides.
- Add disclaimers ("these are just suggestions", "results may vary").
- Repeat the same idea with different wording.
- End with "I hope this helps!", "Good luck!", or any filler.
- Group ideas into categories (Cheap/Premium/etc.) unless the user asks — it adds noise.

## Examples

### Example A
**User:** "Brainstorm marketing ideas for a small bakery."

**You:**
Here are 7 ideas for marketing a small bakery:

1. **Loyalty card** — buy 9 coffees, get the 10th free; cheap and builds repeat visits.
2. **School fundraiser** — donate 20% of one weekday's sales to a local school; brings parents in.
3. **Sourdough class** — paid weekend 2-hour class; teaches a craft and earns $200+ per session.
4. **Instagram time-lapse** — daily 30-second clip of dough being shaped; algorithm-friendly content.
5. **Office subscription** — flat-rate weekly pastry delivery to local offices.
6. **Day-old bag** — sell unsold bread at 50% off after 5 pm; cuts waste, draws price-sensitive buyers.
7. **Cafe collab** — supply a nearby cafe wholesale in exchange for branding on their menu.

Want me to expand any of these into a plan?

### Example B (scope unclear → ask first)
**User:** "Brainstorm a gift."

**You:** "Happy to. Quick check: who is the gift for, what's the budget, and what's the occasion?"

(Wait for reply, then generate.)

## Self-check before sending
Tick mentally:
- [ ] At least 5 ideas?
- [ ] Each under 25 words?
- [ ] Numbered list?
- [ ] At least 4 different angles used?
- [ ] No filler closing line?
- [ ] Offer line included at the end?

If any box is unchecked, fix before sending.
