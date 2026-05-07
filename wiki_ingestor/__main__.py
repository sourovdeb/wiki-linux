"""
__main__.py — CLI entry point for wiki_ingestor.

Usage:
    python -m wiki_ingestor [command] [options]

Commands:
    watch       Start the real-time file watcher daemon (default)
    batch       One-shot conversion of all files in configured dirs
    init        Write a default config file to the wiki directory (interactive)
    status      Show current configuration and ledger stats
"""

import argparse
import logging
import sys
from pathlib import Path

from .config import IngestorConfig, write_default_config, WIKI_LINUX_CONFIG_PATHS
from .converter import ConversionLedger, WikiConverter
from .watcher import IngestorWatcher


def _build_converter(cfg: IngestorConfig):
    """Construct the LLM client (if enabled) and return a ready WikiConverter."""
    llm_client = None
    if cfg.llm_enabled:
        try:
            if cfg.llm_provider == "ollama":
                from openai import OpenAI  # openai-compat client for Ollama
                llm_client = OpenAI(base_url=cfg.llm_base_url, api_key="ollama")
            elif cfg.llm_provider == "openai":
                from openai import OpenAI
                llm_client = OpenAI()
        except ImportError:
            logging.warning(
                "LLM requested but 'openai' package not found — image captions disabled."
            )

    ledger = ConversionLedger(cfg.ledger_path)
    converter = WikiConverter(
        output_dir=cfg.output_dir,
        ledger=ledger,
        watch_root=None,  # set per-directory during batch
        llm_client=llm_client,
        llm_model=cfg.llm_model if cfg.llm_enabled else None,
    )
    return converter, ledger


def _get_wiki_linux_watch_dirs():
    """Extract watch_dirs from existing wiki-linux config if available."""
    for config_path in WIKI_LINUX_CONFIG_PATHS:
        if config_path.exists():
            try:
                import json
                data = json.loads(config_path.read_text())
                if "monitor" in data and isinstance(data["monitor"], dict):
                    if "watch_dirs" in data["monitor"]:
                        return data["monitor"]["watch_dirs"]
            except Exception:
                pass
    return []


def _prompt_for_folders(existing_dirs: list = None):
    """
    Interactive prompt for user to select folders to watch.
    Returns a list of resolved, expanded paths.
    """
    import platform
    
    print("\n" + "=" * 60)
    print("Wiki Ingestor - Folder Setup")
    print("=" * 60)
    
    # Show existing wiki-linux watch dirs if available
    wiki_linux_dirs = _get_wiki_linux_watch_dirs()
    if wiki_linux_dirs:
        print("\nExisting wiki-linux watch directories:")
        for d in wiki_linux_dirs:
            print(f"  - {d}")
        print("\nThese will be used as defaults.")
    
    # Show standard locations
    home = Path.home()
    if platform.system() == "Windows":
        standard_dirs = [
            home / "Documents",
            home / "Downloads",
            home / "Desktop",
        ]
    else:
        standard_dirs = [
            home / "Documents",
            home / "Downloads",
            home / "Desktop",
        ]
    
    print("\nStandard locations:")
    for i, d in enumerate(standard_dirs, 1):
        print(f"  {i}. {d}")
    
    # Get user input
    print("\n" + "-" * 60)
    print("Enter folders to watch (comma-separated):")
    print("  - Leave empty to use wiki-linux defaults (if available)")
    print("  - Or enter standard location numbers (e.g., 1,2,3)")
    print("  - Or enter custom paths (e.g., ~/Documents,~/Projects)")
    print("  - Existing folders will be validated, non-existent will be created")
    print("-" * 60)
    
    user_input = input("Folders to watch: ").strip()
    
    selected_dirs = []
    
    if not user_input:
        # Use wiki-linux dirs if available, otherwise standard
        if wiki_linux_dirs:
            selected_dirs = wiki_linux_dirs
        else:
            selected_dirs = [str(d) for d in standard_dirs]
    elif user_input.replace(",", "").replace(" ", "").isdigit():
        # User selected by number
        indices = [int(x.strip()) - 1 for x in user_input.split(",")]
        for idx in indices:
            if 0 <= idx < len(standard_dirs):
                selected_dirs.append(str(standard_dirs[idx]))
    else:
        # User entered custom paths
        selected_dirs = [x.strip() for x in user_input.split(",")]
    
    # Validate and expand paths
    resolved_dirs = []
    for d in selected_dirs:
        path = Path(d).expanduser().resolve()
        if not path.exists():
            print(f"\nFolder does not exist: {path}")
            create = input(f"Create directory '{path}'? [y/N]: ").strip().lower()
            if create == 'y':
                path.mkdir(parents=True, exist_ok=True)
                print(f"Created: {path}")
            else:
                print(f"Skipping: {path}")
                continue
        resolved_dirs.append(str(path))
    
    return resolved_dirs


def cmd_init(cfg: IngestorConfig, args):
    dest = cfg.wiki_dir / "wiki_ingestor_config.json"
    
    # Check if wiki-linux config exists
    wiki_linux_dirs = _get_wiki_linux_watch_dirs()
    
    if dest.exists() and not args.force:
        print(f"Config already exists at {dest} (use --force to overwrite)")
        return
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    # Interactive setup if no watch_dirs are configured and not forced
    if not wiki_linux_dirs and not args.force:
        print("\nNo existing wiki-linux configuration found.")
        folders = _prompt_for_folders()
        
        # Create custom config with selected folders
        import json
        config_data = {
            "_comment": "wiki_ingestor configuration — see config.py for all options",
            "watch_dirs": folders,
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
        dest.write_text(json.dumps(config_data, indent=2))
        print(f"\nConfig written to {dest}")
        print(f"Selected folders: {folders}")
    else:
        # Use default config
        write_default_config(dest)
        if wiki_linux_dirs:
            print(f"\nNote: wiki-linux watch directories found: {wiki_linux_dirs}")
            print("These will be used by wiki_ingestor automatically.")


def cmd_batch(cfg: IngestorConfig, args):
    converter, ledger = _build_converter(cfg)
    dirs = cfg.batch_dirs or cfg.watch_dirs
    if not dirs:
        print("No batch_dirs configured. Add paths to wiki_ingestor_config.json.")
        ledger.close()
        return

    converted = 0
    skipped = 0
    for directory in dirs:
        p = Path(directory)
        if not p.exists():
            logging.warning("Directory not found, skipping: %s", directory)
            continue
        converter.watch_root = p
        pattern = "**/*" if cfg.recursive else "*"
        for file in p.glob(pattern):
            if file.is_file():
                result = converter.convert(file)
                if result:
                    converted += 1
                else:
                    skipped += 1

    print(f"Batch complete — converted: {converted}, skipped/unsupported: {skipped}")
    ledger.close()


def cmd_watch(cfg: IngestorConfig, args):
    if not cfg.watch_dirs:
        print("No watch_dirs configured. Add paths to wiki_ingestor_config.json.")
        sys.exit(1)

    converter, ledger = _build_converter(cfg)

    # Optionally run batch on startup
    if cfg.batch_on_start:
        logging.info("Running initial batch conversion before starting watcher...")
        cmd_batch(cfg, args)

    print(f"Watching {len(cfg.watch_dirs)} director(y/ies). Ctrl+C to stop.")
    watcher = IngestorWatcher(
        converter=converter,
        watch_dirs=[Path(d) for d in cfg.watch_dirs],
        recursive=cfg.recursive,
        debounce_seconds=cfg.debounce_seconds,
    )
    try:
        watcher.run_forever()
    finally:
        ledger.close()


def cmd_status(cfg: IngestorConfig, args):
    import sqlite3

    print("\n── wiki_ingestor status ──────────────────────")
    print(f"  wiki_dir      : {cfg.wiki_dir}")
    print(f"  output_dir    : {cfg.output_dir}")
    print(f"  watch_dirs    : {cfg.watch_dirs or '(none)'}")
    print(f"  recursive     : {cfg.recursive}")
    print(f"  batch_on_start: {cfg.batch_on_start}")
    print(f"  llm_enabled   : {cfg.llm_enabled}")
    if cfg.llm_enabled:
        print(f"  llm_provider  : {cfg.llm_provider}  model={cfg.llm_model}")
    if cfg.ledger_path.exists():
        conn = sqlite3.connect(str(cfg.ledger_path))
        row = conn.execute("SELECT COUNT(*) FROM conversions").fetchone()
        conn.close()
        print(f"  ledger entries: {row[0]}")
    else:
        print("  ledger        : not yet created")
    print("─────────────────────────────────────────────\n")


def _setup_logging(cfg: IngestorConfig):
    cfg.log_path.parent.mkdir(parents=True, exist_ok=True)
    handlers = [logging.StreamHandler()]
    try:
        handlers.append(logging.FileHandler(cfg.log_path, encoding="utf-8"))
    except Exception:
        pass
    logging.basicConfig(
        level=getattr(logging, cfg.log_level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
        handlers=handlers,
    )


def main():
    parser = argparse.ArgumentParser(
        prog="wiki_ingestor",
        description="MarkItDown-powered file → Markdown daemon for wiki-linux",
    )
    parser.add_argument(
        "--config", metavar="FILE", help="Path to wiki_ingestor_config.json"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("watch", help="Start real-time watcher daemon (default)")
    sub.add_parser("batch", help="One-shot conversion of all configured directories")

    init_p = sub.add_parser("init", help="Write default config to wiki directory (interactive)")
    init_p.add_argument("--force", action="store_true")

    sub.add_parser("status", help="Show configuration and ledger statistics")

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None
    cfg = IngestorConfig.load(config_path)
    _setup_logging(cfg)

    command = args.command or "watch"
    dispatch = {
        "watch": cmd_watch,
        "batch": cmd_batch,
        "init": cmd_init,
        "status": cmd_status,
    }
    dispatch[command](cfg, args)


if __name__ == "__main__":
    main()
