#!/usr/bin/env bash
# .devcontainer/setup.sh — First-time setup for Codespaces

set -euo pipefail

echo "=========================================="
echo "  wiki-linux Codespaces Setup"
echo "=========================================="
echo ""

# 1. Create venv
if [ ! -d ".venv" ]; then
    echo "[1/5] Creating Python virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install --quiet --upgrade pip
    echo "✓ Virtual environment ready"
else
    echo "[1/5] Using existing virtual environment"
fi

# 2. Install dependencies
echo "[2/5] Installing dependencies..."
.venv/bin/pip install --quiet -r requirements.txt
echo "✓ Dependencies installed"

# 3. Create config
echo "[3/5] Setting up configuration..."
CONFIG_DIR="$HOME/.config/wiki-linux"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/config.json" ]; then
    cp config.json "$CONFIG_DIR/config.json"
    echo "✓ Config created at $CONFIG_DIR/config.json"
else
    echo "✓ Config already exists"
fi

# 4. Initialize git in wiki root
echo "[4/5] Initializing wiki git repository..."
WIKI_ROOT="$HOME/wiki"
mkdir -p "$WIKI_ROOT"/{system,user/{notes,projects,research},_meta,_tmp}

if [ ! -d "$WIKI_ROOT/.git" ]; then
    cd "$WIKI_ROOT"
    git init -b main
    cat > .gitignore <<'GITIGNORE'
_tmp/
*.log
.DS_Store
.obsidian/workspace.json
GITIGNORE
    git add .gitignore
    git commit -m "init: wiki vault initialised"
    cd - > /dev/null
    echo "✓ Git repo initialized"
else
    echo "✓ Git repo already exists"
fi

# 5. Offer to scan home directory for messy files
echo "[5/5] Scanning home directory for knowledge to organize..."
echo ""
echo "Found scattered files in your home directory?"
echo "The wiki agent can automatically organize them into the vault."
echo ""
read -p "Would you like to scan ~/Downloads, ~/Desktop, ~/Documents? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running ingest agent (interactive mode)..."
    echo ""
    PYTHONPATH=. .venv/bin/python3 -m src.agent.ingest \
        --scan-home \
        --interactive \
        --apply \
        || echo "Ingest skipped or failed (you can run it later with: python3 -m src.agent.ingest --scan-home)"
else
    echo "Skipped. You can run it later with: python3 -m src.agent.ingest --scan-home"
fi

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit config: $CONFIG_DIR/config.json"
echo "  2. Start using: wiki new 'First note'"
echo "  3. Query: wiki ask 'What have I learned?'"
echo ""
