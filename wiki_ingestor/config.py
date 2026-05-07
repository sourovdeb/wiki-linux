"""
config.py — Configuration for wiki_ingestor.

Reads from (in order of priority):
  1. Environment variables (WIKI_INGESTOR_*)
  2. wiki_ingestor_config.json in the script directory
  3. The existing wiki-linux config.json (if found at OS-specific paths)
  4. Hard-coded defaults

This layering means the ingestor integrates with the existing wiki-linux
config without requiring any changes to it.
"""

import json
import os
import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


_DEFAULT_WIKI_DIR = Path.home() / "wiki"

# OS-specific config paths for wiki-linux
if platform.system() == "Windows":
    WIKI_LINUX_CONFIG_PATHS = [
        Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "wiki-linux" / "config.json",
        Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "wiki-linux" / "config.json",
        Path.home() / "wiki" / "config.json",
    ]
else:
    # Linux/Unix
    WIKI_LINUX_CONFIG_PATHS = [
        Path.home() / ".config" / "wiki-linux" / "config.json",
        Path.home() / "wiki" / "config.json",
        Path.home() / ".wiki-linux" / "config.json",
    ]


@dataclass
class IngestorConfig:
    # ---- Paths -------------------------------------------------------
    wiki_dir: Path = field(default_factory=lambda: _DEFAULT_WIKI_DIR)
    output_subdir: str = "converted"          # relative to wiki_dir
    ledger_path: Path = field(
        default_factory=lambda: _DEFAULT_WIKI_DIR / ".ingestor" / "ledger.db"
    )
    log_path: Path = field(
        default_factory=lambda: _DEFAULT_WIKI_DIR / ".ingestor" / "ingestor.log"
    )

    # ---- Watch dirs --------------------------------------------------
    watch_dirs: List[str] = field(default_factory=list)   # e.g. ["~/Documents", "~/Downloads"]
    recursive: bool = True
    debounce_seconds: float = 2.0

    # ---- Batch (on startup) -----------------------------------------
    batch_on_start: bool = True               # convert existing files when daemon starts
    batch_dirs: List[str] = field(default_factory=list)   # defaults to watch_dirs if empty

    # ---- LLM (optional, for image captions) -------------------------
    llm_enabled: bool = False
    llm_provider: str = "ollama"              # "ollama" | "openai"
    llm_model: str = "llava"                  # model name
    llm_base_url: str = "http://localhost:11434/v1"

    # ---- Logging -----------------------------------------------------
    log_level: str = "INFO"

    # ------------------------------------------------------------------
    @property
    def output_dir(self) -> Path:
        return self.wiki_dir / self.output_subdir

    # ------------------------------------------------------------------
    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> "IngestorConfig":
        cfg = cls()

        # 1. Try to absorb settings from existing wiki-linux config.json
        # Search in OS-specific locations
        wiki_config_found = False
        for config_path in WIKI_LINUX_CONFIG_PATHS:
            if config_path.exists():
                try:
                    data = json.loads(config_path.read_text())
                    wiki_config_found = True
                    
                    # Extract wiki root path
                    wiki_root = None
                    if "wiki" in data and isinstance(data["wiki"], dict):
                        if "root" in data["wiki"]:
                            wiki_root = Path(data["wiki"]["root"])
                        elif "base_dir" in data["wiki"]:
                            wiki_root = Path(data["wiki"]["base_dir"])
                    elif "wiki_path" in data:
                        wiki_root = Path(data["wiki_path"])
                    elif "base_dir" in data:
                        wiki_root = Path(data["base_dir"])
                    
                    if wiki_root:
                        cfg.wiki_dir = wiki_root.expanduser()
                    
                    # Extract watch_dirs from monitor config if available
                    if "monitor" in data and isinstance(data["monitor"], dict):
                        if "watch_dirs" in data["monitor"]:
                            cfg.watch_dirs = list(data["monitor"]["watch_dirs"])
                    
                    break  # Use the first found config
                except Exception:
                    pass  # silently ignore malformed upstream config

        # 2. Overlay with ingestor-specific config file
        candidates = [
            config_file,
            Path(__file__).parent / "wiki_ingestor_config.json",
            cfg.wiki_dir / "wiki_ingestor_config.json",
        ]
        for candidate in candidates:
            if candidate and Path(candidate).exists():
                _apply_json(cfg, json.loads(Path(candidate).read_text()))
                break

        # 3. Environment variable overrides  (WIKI_INGESTOR_WATCH_DIRS="~/Docs,~/Downloads")
        _apply_env(cfg)

        # 4. Expand user paths
        cfg.wiki_dir = Path(cfg.wiki_dir).expanduser().resolve()
        cfg.ledger_path = Path(cfg.ledger_path).expanduser()
        cfg.log_path = Path(cfg.log_path).expanduser()
        cfg.watch_dirs = [str(Path(d).expanduser().resolve()) for d in cfg.watch_dirs]
        if cfg.batch_dirs:
            cfg.batch_dirs = [str(Path(d).expanduser().resolve()) for d in cfg.batch_dirs]
        else:
            cfg.batch_dirs = list(cfg.watch_dirs)

        return cfg


def _apply_json(cfg: IngestorConfig, data: dict):
    field_map = {
        "wiki_dir": ("wiki_dir", Path),
        "output_subdir": ("output_subdir", str),
        "ledger_path": ("ledger_path", Path),
        "log_path": ("log_path", Path),
        "watch_dirs": ("watch_dirs", list),
        "recursive": ("recursive", bool),
        "debounce_seconds": ("debounce_seconds", float),
        "batch_on_start": ("batch_on_start", bool),
        "batch_dirs": ("batch_dirs", list),
        "llm_enabled": ("llm_enabled", bool),
        "llm_provider": ("llm_provider", str),
        "llm_model": ("llm_model", str),
        "llm_base_url": ("llm_base_url", str),
        "log_level": ("log_level", str),
    }
    for key, (attr, cast) in field_map.items():
        if key in data:
            setattr(cfg, attr, cast(data[key]) if not isinstance(data[key], cast) else data[key])


def _apply_env(cfg: IngestorConfig):
    prefix = "WIKI_INGESTOR_"
    mapping = {
        "WIKI_DIR": ("wiki_dir", Path),
        "OUTPUT_SUBDIR": ("output_subdir", str),
        "WATCH_DIRS": ("watch_dirs", lambda v: v.split(",")),
        "RECURSIVE": ("recursive", lambda v: v.lower() == "true"),
        "BATCH_ON_START": ("batch_on_start", lambda v: v.lower() == "true"),
        "LLM_ENABLED": ("llm_enabled", lambda v: v.lower() == "true"),
        "LLM_PROVIDER": ("llm_provider", str),
        "LLM_MODEL": ("llm_model", str),
        "LLM_BASE_URL": ("llm_base_url", str),
        "LOG_LEVEL": ("log_level", str),
    }
    for env_key, (attr, cast) in mapping.items():
        val = os.environ.get(f"{prefix}{env_key}")
        if val:
            setattr(cfg, attr, cast(val))


def write_default_config(dest: Path):
    """Write a template wiki_ingestor_config.json to *dest*."""
    template = {
        "_comment": "wiki_ingestor configuration — see config.py for all options",
        "watch_dirs": [
            str(Path.home() / "Documents"),
            str(Path.home() / "Downloads"),
        ],
        "output_subdir": "converted",
        "recursive": True,
        "debounce_seconds": 2.0,
        "batch_on_start": True,
        "llm_enabled": False,
        "llm_provider": "ollama",
        "llm_model": "llava",
        "llm_base_url": "http://localhost:11434/v1",
        "log_level": "INFO",
    }
    dest.write_text(json.dumps(template, indent=2))
    print(f"Default config written → {dest}")
