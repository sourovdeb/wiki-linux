"""
title: Writing Aids
author: wiki-linux
version: 1.0.0
description: Text statistics (word count, readability), AI-cliché detection, and versioned draft saving for the wiki.
"""
import re
from datetime import datetime
from pathlib import Path


class Tools:
    def __init__(self):
        self.wiki_root = Path.home() / "Documents/wiki-linux/wiki-linux"
        self.drafts_dir = self.wiki_root / "drafts"
        # AI-tell phrases — case-insensitive substring match
        self.banned_phrases = [
            "in today's fast-paced world", "in today's world",
            "it's no secret that", "look no further",
            "dive deep", "dive into",
            "unlock the potential", "unlock your potential",
            "supercharge", "revolutionise", "revolutionize",
            "game-changer", "game changer",
            "navigate the complex landscape", "navigate the landscape",
            "harness the power", "elevate your",
            "whether you're a beginner or a pro",
            "whether you are a beginner or a pro",
            "in conclusion", "to summarise", "to summarize", "in summary",
            "delve into", "delve deep",
            "moreover, it is important to note",
            "it goes without saying",
            "as we've seen", "as we have seen",
            "it is important to note that",
            "embark on a journey",
            "at the end of the day",
            "the world of",
        ]

    def text_stats(self, text: str) -> str:
        """
        Compute simple readability stats for a piece of text:
        word count, sentence count, average sentence length, and the
        Flesch Reading Ease score (higher = easier; 60–70 = plain English).

        :param text: The text to analyse.
        :return: One-line markdown with the key stats.
        """
        if not text or not text.strip():
            return "Error: text is empty."

        words = re.findall(r"\b[\w'-]+\b", text)
        word_count = len(words)
        if word_count == 0:
            return "No words detected."

        # Sentences: split on . ! ? followed by space or EOL, ignoring decimals
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'])", text.strip())
        sentences = [s for s in sentences if s.strip()]
        sentence_count = max(1, len(sentences))

        avg_sentence_len = round(word_count / sentence_count, 1)

        # Syllable count (rough heuristic) for Flesch
        total_syllables = sum(self._syllable_count(w) for w in words)
        flesch = round(
            206.835
            - 1.015 * (word_count / sentence_count)
            - 84.6 * (total_syllables / word_count),
            1,
        )
        ease = self._flesch_label(flesch)

        return (
            f"**Words:** {word_count} · "
            f"**Sentences:** {sentence_count} · "
            f"**Avg sentence:** {avg_sentence_len} words · "
            f"**Flesch:** {flesch} ({ease})"
        )

    def check_banned_phrases(self, text: str) -> str:
        """
        Flag AI-cliché phrases found in the text. Returns a list of hits or
        an "OK" message if none found.

        :param text: The text to scan.
        :return: Markdown list of matched phrases (with counts), or 'OK — no clichés flagged.'
        """
        if not text or not text.strip():
            return "Error: text is empty."

        lower = text.lower()
        hits = []
        for phrase in self.banned_phrases:
            count = lower.count(phrase)
            if count:
                hits.append((phrase, count))

        if not hits:
            return "OK — no clichés flagged."

        lines = ["**Cliché phrases found:**"]
        for phrase, count in hits:
            lines.append(f"- `{phrase}` ×{count}")
        lines.append("\n_Rewrite these in concrete, specific language._")
        return "\n".join(lines)

    def save_versioned_draft(self, filename: str, content: str) -> str:
        """
        Save a draft to ~/Documents/wiki-linux/wiki-linux/drafts/<filename>.
        If a file with the same name exists, save as <filename>-v2, -v3, etc.
        (so previous versions are preserved).

        :param filename: Base filename without extension.
        :param content: The draft body.
        :return: Confirmation with saved path, or an error.
        """
        if not filename or not content:
            return "Error: filename and content are both required."

        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^a-zA-Z0-9._-]", "-", filename).strip("-") or "draft"
        if safe.endswith(".md"):
            safe = safe[:-3]

        path = self.drafts_dir / f"{safe}.md"
        version = 1
        while path.exists():
            version += 1
            path = self.drafts_dir / f"{safe}-v{version}.md"

        body = (
            f"---\n"
            f"saved: {datetime.now().isoformat(timespec='minutes')}\n"
            f"version: {version}\n"
            f"---\n\n"
            f"{content.strip()}\n"
        )
        try:
            path.write_text(body, encoding="utf-8")
        except OSError as e:
            return f"Error saving: {e}"
        rel = path.relative_to(self.wiki_root)
        return f"Saved `{rel}` (version {version}, {len(content)} chars)."

    # ---------- helpers ----------

    @staticmethod
    def _syllable_count(word: str) -> int:
        """Rough syllable count for Flesch — good enough for typical English prose."""
        word = word.lower()
        if len(word) <= 3:
            return 1
        word = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", word)
        word = re.sub(r"^y", "", word)
        groups = re.findall(r"[aeiouy]+", word)
        return max(1, len(groups))

    @staticmethod
    def _flesch_label(score: float) -> str:
        if score >= 90:
            return "very easy"
        if score >= 70:
            return "easy"
        if score >= 60:
            return "plain English"
        if score >= 50:
            return "fairly difficult"
        if score >= 30:
            return "difficult"
        return "very difficult"
