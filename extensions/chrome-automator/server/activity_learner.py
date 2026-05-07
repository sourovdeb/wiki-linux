"""
activity_learner.py — Save and process activity recordings.
Recordings are saved as JSONL files, one per platform.
Over time the system learns better selectors from user behaviour.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger("activity_learner")
RECORDINGS_DIR = Path(__file__).parent.parent / "recordings"
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


def save_recording(recording: dict):
    """Append a recording to the platform-specific JSONL log."""
    platform = recording.get("platform", "unknown")
    out_path = RECORDINGS_DIR / f"{platform}.jsonl"
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(recording) + "\n")
    log.debug("Recording saved: %s (%d actions)", platform, len(recording.get("actions", [])))


def load_recordings(platform: str, limit: int = 50) -> list[dict]:
    """Load recent recordings for a platform."""
    path = RECORDINGS_DIR / f"{platform}.jsonl"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    recs = []
    for line in lines[-limit:]:
        try:
            recs.append(json.loads(line))
        except Exception:
            continue
    return recs


def get_recording_stats() -> dict:
    """Return summary stats of all recordings."""
    stats = {}
    for jsonl in RECORDINGS_DIR.glob("*.jsonl"):
        lines = jsonl.read_text(encoding="utf-8").strip().splitlines()
        stats[jsonl.stem] = len(lines)
    return stats


def extract_learned_selectors(platform: str) -> dict[str, list[str]]:
    """
    Extract the most frequently successful selectors from recordings.
    Returns a dict of action_type → sorted list of selectors by frequency.
    """
    recordings = load_recordings(platform)
    selector_freq: dict[str, dict[str, int]] = {}
    for rec in recordings:
        for action in rec.get("actions", []):
            atype = action.get("type", "unknown")
            sel = action.get("selector", "")
            if not sel:
                continue
            selector_freq.setdefault(atype, {})
            selector_freq[atype][sel] = selector_freq[atype].get(sel, 0) + 1

    # Sort by frequency desc
    return {
        atype: sorted(sels, key=lambda s: sels[s], reverse=True)
        for atype, sels in selector_freq.items()
    }


async def analyse_recordings(recordings: list[dict]) -> str:
    """Delegate to llm_helper (import here to avoid circular)."""
    from llm_helper import analyse_recordings as _analyse
    return await _analyse(recordings)
