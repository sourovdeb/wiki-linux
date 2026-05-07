"""
title: Code Workspace
author: wiki-linux
version: 1.0.0
description: Save code snippets to the wiki, run a Python syntax-check, and (optionally) execute Python in a sandboxed subprocess with timeout.
"""
import ast
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


class Tools:
    def __init__(self):
        self.wiki_root = Path.home() / "Documents/wiki-linux/wiki-linux"
        self.snippets_dir = self.wiki_root / "snippets"
        # Map common languages to file extensions
        self.ext_map = {
            "python": "py", "py": "py",
            "javascript": "js", "js": "js", "node": "js",
            "typescript": "ts", "ts": "ts",
            "bash": "sh", "shell": "sh", "sh": "sh",
            "rust": "rs", "go": "go", "ruby": "rb",
            "html": "html", "css": "css", "json": "json",
            "yaml": "yaml", "yml": "yaml", "toml": "toml",
            "sql": "sql", "c": "c", "cpp": "cpp",
        }

    def save_snippet(self, filename: str, language: str, code: str) -> str:
        """
        Save a code snippet to ~/Documents/wiki-linux/wiki-linux/snippets/<language>/.

        :param filename: Filename without extension (it will be added).
        :param language: Language name (python, js, bash, rust, etc.).
        :param code: The full code as a string.
        :return: Confirmation with saved path, or an error.
        """
        if not filename or not language or not code:
            return "Error: filename, language, and code are all required."

        lang = language.lower().strip()
        ext = self.ext_map.get(lang, lang)
        target_dir = self.snippets_dir / lang
        target_dir.mkdir(parents=True, exist_ok=True)

        # Sanitise filename
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "-", filename).strip("-")
        if not safe_name:
            safe_name = "snippet"
        if not safe_name.endswith(f".{ext}"):
            safe_name = f"{safe_name}.{ext}"

        path = target_dir / safe_name
        try:
            path.write_text(code, encoding="utf-8")
        except OSError as e:
            return f"Error saving: {e}"
        rel = path.relative_to(self.wiki_root)
        return f"Saved `{rel}` ({len(code)} chars)."

    def lint_python(self, code: str) -> str:
        """
        Check Python code for syntax errors using the ast module. Fast, no
        external tools, no execution.

        :param code: Python source as a string.
        :return: 'OK — no syntax errors.' or a formatted error message.
        """
        if not code or not code.strip():
            return "Error: code is empty."
        try:
            ast.parse(code)
            return "OK — no syntax errors."
        except SyntaxError as e:
            return (
                f"SyntaxError: {e.msg}\n"
                f"Line {e.lineno}, column {e.offset}\n"
                f"  {e.text.rstrip() if e.text else ''}"
            )

    def run_python_safely(self, code: str, timeout: int = 5) -> str:
        """
        Run a short Python snippet in a subprocess with a hard timeout.
        Returns combined stdout + stderr. Network and file access are NOT
        sandboxed — use only with code you've reviewed.

        :param code: Python source to execute.
        :param timeout: Seconds before the subprocess is killed (default 5, max 30).
        :return: Captured output, or an error / timeout message.
        """
        if not code or not code.strip():
            return "Error: code is empty."
        timeout = max(1, min(int(timeout), 30))

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True, text=True,
                timeout=timeout,
            )
            out = result.stdout.strip()
            err = result.stderr.strip()
            parts = []
            if out:
                parts.append(f"**stdout:**\n```\n{out}\n```")
            if err:
                parts.append(f"**stderr:**\n```\n{err}\n```")
            parts.append(f"_exit code: {result.returncode}_")
            return "\n\n".join(parts) if parts else "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: timed out after {timeout}s."
        except Exception as e:
            return f"Error running code: {e}"
        finally:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass
