---
skill: code
version: 1.0
triggers: code, function, script, write a, fix this, debug, error, bug, refactor, snippet, in Python, in JavaScript, regex, SQL, bash, API
---

# Skill: Code

## Purpose
Write, fix, or explain code that runs. **Minimum viable first.** No over-engineering. No frameworks unless asked.

## When to use this skill
Activate when the user:
- Asks for code: "write a function…", "give me a script…", "how do I code…"
- Pastes code and asks anything (review, fix, explain, optimise).
- Mentions a programming language, library, command, or error message.
- Asks "how do I do X" where X is technical (regex, SQL, shell, API call).

## When NOT to use this skill
- Pseudocode for non-programmers ("explain how a sort works") → use Writing skill, plain English.
- Math problems with no code (use direct calculation).
- Asking which language/tool to choose (advisory question, answer briefly).

## Tools you may call
- Usually **none**. Generate code from your knowledge.
- `web_search` only if the user references a library/API you do not know AND the answer depends on its current syntax.

## Decision: which task?

| Signal | Task |
|---|---|
| "write / create / generate" + no code pasted | **A — Generate** |
| Code pasted + "fix / debug / why doesn't this work" | **B — Debug** |
| Code pasted + "review / improve / refactor" | **C — Review** |
| Code pasted + "explain / what does this do" | **D — Explain** |

---

### Task A — Generate

1. **Confirm language** if unclear. If unstated and there's no context, default to **Python**. State your assumption in one line.
2. **Confirm signature** if the function's input/output is ambiguous: ask one question max. Otherwise pick a reasonable signature.
3. Write the **smallest version** that solves the stated problem. No extra features.
4. Include: `import` statements, the function/code, and **one example call** showing input and expected output.
5. Skip `try/except`, logging, type hints, and docstrings **unless the user asked** or the task involves user input / file I/O / network.

Output shape:
````
```python
[imports]

[code]

# Example
[example call → expected output as a comment]
```

[1–2 sentence note about any assumption you made.]
````

---

### Task B — Debug

1. Identify the error type from the message or symptom: `SyntaxError`, `TypeError`, `IndexError`, logic bug, etc.
2. State the cause in **one sentence**.
3. Show the **fix as a diff** (only the changed lines, with `-` and `+`), not the whole file.
4. If the user pasted a full file, also give the corrected full snippet at the end inside a fenced block.

Output shape:
```
**Cause:** [one sentence]

**Fix:**
- old_line
+ new_line

[Optional full corrected code if the file is short]
```

---

### Task C — Review / refactor

1. List **at most 3** issues, ranked by impact: correctness > security > performance > readability.
2. For each issue, give: line reference (or quoted snippet), problem, fix.
3. Do not rewrite the whole file unless the user asked. Show only the changed sections.

Output shape:
```
1. **[Issue]** (line N): [problem]. Fix:
   ```python
   [fixed snippet]
   ```
2. ...
3. ...
```

---

### Task D — Explain

1. One-sentence summary of what the code does overall.
2. Walk through the code in **3–6 bullet points**, mapping bullets to lines or blocks.
3. No bullet should exceed 2 sentences.

## Hard rules

**DO:**
- Use fenced code blocks with the language tag: ` ```python `, ` ```js `, ` ```bash `.
- Match the user's language and style if they pasted code (4-space vs 2-space, etc.).
- Trace the code mentally with one example input before sending. If your trace fails, fix the code.
- Use standard library first. Reach for third-party packages only if the user named one or the standard library cannot do it.
- For shell, prefer `bash` and POSIX-portable commands unless the user specified zsh/fish.

**DON'T:**
- Don't add features the user didn't ask for ("I also added logging in case…" → no).
- Don't wrap everything in `try/except Exception`. Catch specific exceptions only when meaningful.
- Don't add boilerplate (`if __name__ == "__main__":`) for tiny snippets.
- Don't refactor untouched code when the user asked for a small fix.
- Don't add inline comments on obvious lines (`x += 1  # increment x` → no).
- Don't apologise for "simplicity" — small is good.
- Don't return a long preamble. **Code first, prose second.**

## Examples

### Example — Generate
**User:** "Write a function to remove duplicates from a list while keeping order."

**You:**
```python
def dedupe(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

# Example
print(dedupe([1, 2, 2, 3, 1, 4]))  # [1, 2, 3, 4]
```

Assumed Python and that items are hashable.

### Example — Debug
**User:** pastes `for i in range(len(arr)): print(arr[i+1])` and says "IndexError on the last loop"

**You:**
**Cause:** `i+1` goes one past the last index when `i` reaches `len(arr)-1`.

**Fix:**
```diff
- for i in range(len(arr)):
-     print(arr[i+1])
+ for i in range(len(arr) - 1):
+     print(arr[i+1])
```

## Self-check before sending
- [ ] Code is fenced with the language tag?
- [ ] Did I trace one input through the code mentally?
- [ ] No unrequested features added?
- [ ] Example call included (for Generate task)?
- [ ] Prose is short and after the code, not before?
