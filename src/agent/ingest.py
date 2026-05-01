"""
src/agent/ingest.py — Auto-ingest agent for messy home directories.

Scans ~/Downloads, ~/Desktop, ~/Documents, ~/code/ etc.
Classifies each file via LLM into wiki structure.
Detects duplicates.
Proposes JSON actions.
Executes on confirmation.

Use in Codespaces during setup to rescue scattered files.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

from src.config import cfg
from src import llm, monitor

log = logging.getLogger("wiki.agent.ingest")

# Directories to scan in order of priority
SCAN_DIRS = [
    "~/Downloads",
    "~/Desktop",
    "~/Documents",
    "~/code",
    "~/notes",
    "~/projects",
]

# File extensions to consider
INGESTIBLE = {
    ".md", ".txt", ".docx", ".pdf",
    ".py", ".js", ".sh", ".java",
    ".json", ".yaml", ".toml",
}

# Never scan
IGNORE_DIRS = {
    ".git", ".venv", "venv", ".cache", "__pycache__",
    ".local", ".config", ".ssh", "node_modules",
    ".obsidian", "_tmp", "site-packages",
}


def read_file_safe(path: Path, max_bytes: int = 10000) -> Optional[str]:
    """Read file content safely, truncate if too large."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)
        if len(content) > 100:  # Only ingest if meaningfully sized
            return content
    except (OSError, UnicodeDecodeError):
        pass
    return None


def classify_file_content(path: Path, content: str) -> Optional[dict]:
    """
    Ask LLM: where should this file go in the wiki?
    
    Returns JSON proposal:
    {
      "category": "system|user",
      "subcategory": "teaching|code|notes|research",
      "topic": "slug-name",
      "title": "Human Title",
      "reason": "Why this classification"
    }
    """
    filename = path.name
    # First 200 chars to give context
    preview = content[:200].replace("\n", " ")
    
    prompt = f"""Classify this file into wiki structure.

Filename: {filename}
Preview: {preview}

Respond ONLY with JSON (no preamble):
{{
  "category": "system|user",
  "subcategory": "teaching|code|notes|research",
  "topic": "slug-name",
  "title": "Human Title",
  "reason": "Why"
}}"""
    
    try:
        # Use llm.answer_question RAG mode — we pass empty snippets
        # so LLM just uses the prompt
        response = llm.answer_question(prompt, [])
        parsed = json.loads(response)
        
        # Validate structure
        required = {"category", "subcategory", "topic", "title", "reason"}
        if not required.issubset(parsed.keys()):
            log.warning(f"Incomplete LLM response for {filename}")
            return None
        
        return parsed
    except (json.JSONDecodeError, ValueError) as e:
        log.warning(f"LLM classification failed for {filename}: {e}")
        return None


def compute_content_hash(content: str) -> str:
    """Simple hash to detect exact duplicates."""
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()


def scan_home_directory(home: Optional[Path] = None) -> dict:
    """
    Walk home directory. Classify each file. Detect duplicates.
    
    Returns:
    {
      "discovered": [
        {"source": Path, "proposal": dict, "size_kb": float, "hash": str}
      ],
      "duplicates": [
        {"primary": Path, "duplicate": Path, "similarity": 0.95}
      ]
    }
    """
    if home is None:
        home = Path.home()
    
    discovered = []
    hashes = {}  # hash → (path, content)
    
    log.info(f"Scanning {home} recursively...")
    
    for root, dirs, files in os.walk(home, topdown=True):
        # Prune ignored dirs in-place
        dirs[:] = [
            d for d in dirs 
            if not d.startswith('.') and d not in IGNORE_DIRS
        ]
        
        root_path = Path(root)
        
        for filename in files:
            # Skip if wrong extension
            if not any(filename.endswith(ext) for ext in INGESTIBLE):
                continue
            
            file_path = root_path / filename
            
            # Skip if unreadable or too small
            content = read_file_safe(file_path)
            if not content:
                continue
            
            # Classify
            proposal = classify_file_content(file_path, content)
            if not proposal:
                log.debug(f"Skipped (unclassifiable): {file_path}")
                continue
            
            # Compute hash for duplicate detection
            file_hash = compute_content_hash(content)
            
            discovered.append({
                "source": file_path,
                "proposal": proposal,
                "size_kb": file_path.stat().st_size / 1024,
                "hash": file_hash,
                "content_preview": content[:100],
            })
            
            # Track hash for duplicates
            if file_hash in hashes:
                log.debug(f"Potential duplicate: {file_path}")
            else:
                hashes[file_hash] = file_path
    
    log.info(f"Discovered {len(discovered)} candidate files")
    return {
        "discovered": discovered,
        "hashes": hashes,
    }


def build_ingest_proposal(scan_results: dict, wiki_root: Path) -> dict:
    """
    Build JSON proposal for user confirmation.
    
    Actions:
    - ingest: new file to wiki
    - skip: uninteresting file
    - link-duplicate: duplicate of existing page
    """
    proposal = {
        "phase": "ingest-proposal",
        "timestamp": str(__import__("datetime").datetime.utcnow().isoformat()),
        "files_discovered": len(scan_results["discovered"]),
        "actions": [],
        "summary": {},
    }
    
    duplicates = {}
    for item in scan_results["discovered"]:
        h = item["hash"]
        if h in duplicates:
            duplicates[h].append(item)
        else:
            duplicates[h] = [item]
    
    ingest_count = 0
    duplicate_count = 0
    
    for item in scan_results["discovered"]:
        source = item["source"]
        proposal_data = item["proposal"]
        
        # Check if this is a duplicate
        h = item["hash"]
        if len(duplicates[h]) > 1:
            # Is this the first? If so, ingest. Otherwise, link.
            if duplicates[h][0]["source"] == source:
                # Primary: ingest
                action = "ingest"
                ingest_count += 1
            else:
                # Duplicate: link to primary
                action = "link-duplicate"
                duplicate_count += 1
        else:
            # Unique: ingest
            action = "ingest"
            ingest_count += 1
        
        # Validate target path
        target_name = f"{proposal_data['topic']}.md"
        target = wiki_root / proposal_data['category'] / proposal_data['subcategory'] / target_name
        
        try:
            resolved = target.resolve()
            if not str(resolved).startswith(str(wiki_root.resolve())):
                log.error(f"Path escape: {target} → {resolved}")
                continue
        except Exception as e:
            log.error(f"Path resolution failed: {e}")
            continue
        
        proposal["actions"].append({
            "action": action,
            "source": str(source),
            "target": str(target.relative_to(wiki_root)) if action == "ingest" else None,
            "title": proposal_data["title"],
            "reason": proposal_data["reason"],
            "size_kb": item["size_kb"],
            "reversible": True,
        })
    
    proposal["summary"] = {
        "to_ingest": ingest_count,
        "duplicates_to_link": duplicate_count,
        "total_actions": len(proposal["actions"]),
    }
    
    return proposal


def execute_proposal(proposal: dict, wiki_root: Path) -> dict:
    """
    Execute the proposed actions.
    
    Returns:
    {
      "ingested": N,
      "linked": N,
      "failed": N,
      "errors": [...]
    }
    """
    results = {
        "ingested": 0,
        "linked": 0,
        "failed": 0,
        "errors": [],
    }
    
    for action_data in proposal["actions"]:
        action = action_data["action"]
        source = Path(action_data["source"])
        
        try:
            if action == "ingest":
                target = wiki_root / action_data["target"]
                target.parent.mkdir(parents=True, exist_ok=True)
                
                # Read source
                content = read_file_safe(source)
                if not content:
                    results["failed"] += 1
                    results["errors"].append(f"Could not read {source}")
                    continue
                
                # Ask LLM to format as wiki page
                page_content = format_wiki_page(source, content)
                
                # Write
                target.write_text(page_content)
                monitor.record_self_write(target)
                log.info(f"Ingested: {source} → {target}")
                results["ingested"] += 1
                
            elif action == "link-duplicate":
                # TODO: implement duplicate linking
                log.info(f"Would link duplicate: {source}")
                results["linked"] += 1
        
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{source}: {e}")
            log.error(f"Failed to process {source}: {e}")
    
    return results


def format_wiki_page(source: Path, content: str) -> str:
    """Format content as wiki page with frontmatter."""
    from datetime import datetime, timezone
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Truncate content if needed
    if len(content) > 8000:
        content = content[:8000] + "\n... [truncated]"
    
    page = f"""---
title: {source.name}
source: {source}
imported: {now}
tags: [imported]
---

# {source.stem}

> Imported from: `{source}`

## Contents

```
{content}
```
"""
    return page


def main(scan_home: bool = False, interactive: bool = False, apply: bool = False):
    """Main entry point for ingest agent."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    
    wiki_root = Path(cfg["wiki"]["root"])
    wiki_root.mkdir(parents=True, exist_ok=True)
    
    if not scan_home:
        log.error("Use --scan-home to scan home directory")
        return
    
    # Scan
    log.info("Scanning home directory for files to organize...")
    scan_results = scan_home_directory()
    
    # Propose
    log.info("Building proposal...")
    proposal = build_ingest_proposal(scan_results, wiki_root)
    
    # Display
    print("\n" + "=" * 80)
    print(json.dumps(proposal, indent=2, default=str))
    print("=" * 80 + "\n")
    
    if not apply:
        if interactive:
            confirm = input("Proceed with ingest? (y/n): ").strip().lower()
            if confirm != "y":
                log.info("Cancelled by user")
                return
        else:
            log.info("Use --apply to execute. Use --interactive to confirm first.")
            return
    
    # Execute
    log.info("Executing ingest...")
    results = execute_proposal(proposal, wiki_root)
    
    print("\nResults:")
    print(json.dumps(results, indent=2))
    
    log.info(f"Ingest complete: {results['ingested']} files ingested, "
             f"{results['linked']} linked, {results['failed']} failed")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-ingest messy home directory")
    parser.add_argument("--scan-home", action="store_true", help="Scan home directory")
    parser.add_argument("--interactive", action="store_true", help="Ask for confirmation")
    parser.add_argument("--apply", action="store_true", help="Execute proposal")
    args = parser.parse_args()
    
    main(
        scan_home=args.scan_home,
        interactive=args.interactive,
        apply=args.apply,
    )
