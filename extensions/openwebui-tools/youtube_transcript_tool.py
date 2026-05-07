"""
title: YouTube Transcript
author: wiki-linux (adapted from Newnol Clolab)
version: 1.0.0
description: Fetch the full transcript of a YouTube video by URL or video ID. Save to wiki optionally.
"""

import json
import re
from pathlib import Path


class Tools:
    def __init__(self):
        self.wiki_root = Path.home() / "Documents/wiki-linux/wiki-linux"

    def _extract_video_id(self, url_or_id: str) -> str:
        """Extract YouTube video ID from URL or return as-is if already an ID."""
        patterns = [
            r"youtu\.be/([a-zA-Z0-9_-]{11})",
            r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
            r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        ]
        for pat in patterns:
            m = re.search(pat, url_or_id)
            if m:
                return m.group(1)
        # Assume it's already a raw video ID
        if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
            return url_or_id
        return url_or_id

    def get_youtube_transcript(self, url_or_id: str, languages: str = "en", save_to_wiki: bool = False) -> str:
        """
        Fetch the full transcript of a YouTube video.

        :param url_or_id: YouTube URL or video ID.
        :param languages: Comma-separated language preferences e.g. 'en,vi'.
        :param save_to_wiki: If True, save the transcript as a wiki note.
        :return: Full transcript text.
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            return "Error: youtube-transcript-api not installed. Run: pip install youtube-transcript-api"

        video_id = self._extract_video_id(url_or_id)
        lang_list = [l.strip() for l in languages.split(",")]

        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=lang_list)
            segments = [s.text for s in transcript]
            full_text = " ".join(segments)
        except Exception as e:
            return f"Error fetching transcript for `{video_id}`: {e}"

        output = f"### YouTube Transcript: `{video_id}`\n\n{full_text}"

        if save_to_wiki:
            notes_dir = self.wiki_root / "user/notes"
            notes_dir.mkdir(parents=True, exist_ok=True)
            out_path = notes_dir / f"youtube_{video_id}.md"
            frontmatter = f"---\ntitle: YouTube {video_id}\nsource: https://youtu.be/{video_id}\ntags: [youtube, transcript]\n---\n\n"
            out_path.write_text(frontmatter + full_text, encoding="utf-8")
            output += f"\n\n_Saved to `user/notes/youtube_{video_id}.md`_"

        return output
