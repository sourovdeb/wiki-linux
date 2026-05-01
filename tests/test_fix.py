from __future__ import annotations

import json
from pathlib import Path

from src import fix


def _cfg(tmp_path: Path) -> dict:
    docs = tmp_path / "docs"
    docs.mkdir()
    return {
        "fix": {
            "doc_roots": [str(docs)],
            "max_snippets": 2,
            "snippet_bytes": 50,
        }
    }


def test_collect_snippets_reads_rg_json(monkeypatch, tmp_path):
    monkeypatch.setattr(fix, "cfg", _cfg(tmp_path))

    class Result:
        stdout = "\n".join(
            [
                json.dumps(
                    {
                        "type": "match",
                        "data": {
                            "path": {"text": "/tmp/a.md"},
                            "line_number": 3,
                            "lines": {"text": "first match line"},
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "match",
                        "data": {
                            "path": {"text": "/tmp/b.md"},
                            "line_number": 7,
                            "lines": {"text": "second match line"},
                        },
                    }
                ),
            ]
        )

    monkeypatch.setattr(fix.subprocess, "run", lambda *args, **kwargs: Result())

    snippets = fix._collect_snippets("pacman")

    assert len(snippets) == 2
    assert snippets[0]["file"] == "/tmp/a.md"
    assert snippets[1]["line"] == 7


def test_suggest_fix_handles_no_snippets(monkeypatch, tmp_path):
    monkeypatch.setattr(fix, "cfg", _cfg(tmp_path))
    monkeypatch.setattr(fix, "_collect_snippets", lambda _query: [])

    output = fix.suggest_fix("broken mirrors")

    assert "No relevant local snippets found" in output


def test_suggest_fix_calls_llm(monkeypatch, tmp_path):
    monkeypatch.setattr(fix, "cfg", _cfg(tmp_path))
    monkeypatch.setattr(
        fix,
        "_collect_snippets",
        lambda _query: [{"file": "a.md", "line": 1, "text": "fact"}],
    )

    captured = {}

    def fake_answer(question, snippets):
        captured["question"] = question
        captured["snippets"] = snippets
        return "do this"

    monkeypatch.setattr(fix.llm, "answer_question", fake_answer)

    output = fix.suggest_fix("wifi broken")

    assert output == "do this"
    assert "Problem: wifi broken" in captured["question"]
    assert captured["snippets"][0]["file"] == "a.md"
