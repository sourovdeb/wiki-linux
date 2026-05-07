/*
 * wiki-startup — Obsidian plugin
 * Shows a startup status popup and provides wiki-linux quick actions.
 * Auto-runs on Obsidian open.
 */

const { Plugin, Modal, Notice, MarkdownRenderer, Setting } = require('obsidian');
const { exec, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const WIKI_ROOT = '/home/sourov/Documents/wiki-linux/wiki-linux';
const BIN = WIKI_ROOT + '/bin';
const OLLAMA = 'http://127.0.0.1:11434';
const OPENWEBUI = 'http://127.0.0.1:8080';

function run(cmd) {
  try { return execSync(cmd, { timeout: 3000, encoding: 'utf8' }).trim(); }
  catch (e) { return null; }
}

function countPages(root) {
  try {
    const r = execSync(`find "${root}" -name "*.md" -not -path "*/.git/*" | wc -l`, { timeout: 3000, encoding: 'utf8' });
    return parseInt(r.trim()) || 0;
  } catch { return 0; }
}

async function fetchOllama() {
  try {
    const r = await fetch(OLLAMA + '/api/tags', { signal: AbortSignal.timeout(2000) });
    if (!r.ok) return null;
    const j = await r.json();
    return j.models ? j.models.map(m => m.name) : [];
  } catch { return null; }
}

async function fetchWebUI() {
  try {
    const r = await fetch(OPENWEBUI, { signal: AbortSignal.timeout(2000) });
    return r.ok;
  } catch { return false; }
}

// ── Startup modal
class WikiStartupModal extends Modal {
  constructor(app, plugin) {
    super(app);
    this.plugin = plugin;
    this.data = {};
  }

  async onOpen() {
    const { contentEl } = this;
    contentEl.addClass('wiki-startup-modal');
    contentEl.createEl('h2', { text: '⚡ Wiki-Linux Status' });

    const grid = contentEl.createDiv({ cls: 'wiki-grid' });

    // Gather data async
    const [ollamaModels, webuiOk] = await Promise.all([fetchOllama(), fetchWebUI()]);
    const pages = countPages(WIKI_ROOT);
    const gitLog = run(`git -C "${WIKI_ROOT}" log -1 --format='%ar · %s'`) || 'no commits';
    const diskFree = run(`df -h /home/sourov | awk 'NR==2{print $4" free / "$5" used"}'`) || '?';
    const wikiMonitor = run(`systemctl --user is-active wiki-monitor.service`) || 'inactive';
    const syncTimer = run(`systemctl --user is-active wiki-sync.timer`) || 'inactive';

    const rows = [
      ['📄 Pages',    `${pages} markdown files`],
      ['🔄 Last sync', gitLog],
      ['💾 Disk',      diskFree],
      ['🤖 Ollama',    ollamaModels ? `✓ ${ollamaModels.length} models` : '✗ offline'],
      ['🌐 Web UI',    webuiOk ? `✓ ${OPENWEBUI}` : '✗ offline'],
      ['👁 Monitor',   wikiMonitor === 'active' ? '✓ active' : '✗ ' + wikiMonitor],
      ['⏱ Sync timer', syncTimer === 'active' ? '✓ active' : '✗ ' + syncTimer],
    ];

    const table = grid.createEl('table', { cls: 'wiki-status-table' });
    rows.forEach(([label, value]) => {
      const tr = table.createEl('tr');
      tr.createEl('td', { text: label, cls: 'wiki-label' });
      const td = tr.createEl('td', { cls: 'wiki-value' });
      td.textContent = value;
      if (value.startsWith('✗')) td.addClass('wiki-err');
      else if (value.startsWith('✓')) td.addClass('wiki-ok');
    });

    // Ollama model list
    if (ollamaModels && ollamaModels.length > 0) {
      const modelDiv = contentEl.createDiv({ cls: 'wiki-models' });
      modelDiv.createEl('strong', { text: 'Available models: ' });
      modelDiv.appendText(ollamaModels.join('  ·  '));
    }

    // Quick action buttons
    const actions = contentEl.createDiv({ cls: 'wiki-actions' });
    actions.createEl('p', { text: 'Quick Actions', cls: 'wiki-section-title' });

    const btnRow = actions.createDiv({ cls: 'wiki-btn-row' });

    const btn = (label, onClick) => {
      const b = btnRow.createEl('button', { text: label, cls: 'wiki-btn' });
      b.addEventListener('click', onClick);
      return b;
    };

    btn('🔍 Search', () => {
      exec(`${BIN}/wiki-search-dialog`);
      this.close();
    });
    btn('📝 New Note', () => {
      exec(`${BIN}/wiki-new-note "Untitled"`);
      this.close();
    });
    btn('🌐 Open WebUI', () => {
      exec(`xdg-open ${OPENWEBUI}`);
    });
    btn('🔄 Sync Now', () => {
      exec(`git -C "${WIKI_ROOT}" add -A && git -C "${WIKI_ROOT}" commit -m "manual sync" && git -C "${WIKI_ROOT}" push`);
      new Notice('Syncing to GitHub...');
    });
    btn('✅ Health Check', () => {
      exec(`${BIN}/wiki-health-check`, (err, stdout) => {
        new Notice(stdout ? stdout.slice(0, 300) : 'Health check done');
      });
    });

    // Dismiss button
    const closeBtn = contentEl.createEl('button', { text: 'Dismiss', cls: 'wiki-dismiss' });
    closeBtn.addEventListener('click', () => this.close());

    // Inject CSS
    this._injectStyle();
  }

  onClose() {
    this.contentEl.empty();
  }

  _injectStyle() {
    if (document.getElementById('wiki-startup-style')) return;
    const style = document.createElement('style');
    style.id = 'wiki-startup-style';
    style.textContent = `
      .wiki-startup-modal { padding: 12px; min-width: 480px; }
      .wiki-status-table { width: 100%; border-collapse: collapse; margin: 8px 0; }
      .wiki-status-table td { padding: 4px 8px; font-size: 0.9em; }
      .wiki-label { color: var(--text-muted); width: 130px; white-space: nowrap; }
      .wiki-ok { color: #4caf50; }
      .wiki-err { color: #f44336; }
      .wiki-models { font-size: 0.82em; color: var(--text-muted); margin: 4px 0 12px; }
      .wiki-section-title { font-size: 0.85em; text-transform: uppercase; letter-spacing: .06em; color: var(--text-muted); margin: 12px 0 6px; }
      .wiki-btn-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
      .wiki-btn { padding: 5px 12px; border-radius: 4px; cursor: pointer; font-size: 0.88em; background: var(--interactive-normal); border: 1px solid var(--background-modifier-border); }
      .wiki-btn:hover { background: var(--interactive-hover); }
      .wiki-dismiss { width: 100%; padding: 6px; cursor: pointer; background: var(--interactive-accent); color: var(--text-on-accent); border: none; border-radius: 4px; margin-top: 4px; }
    `;
    document.head.appendChild(style);
  }
}

// ── Main plugin
module.exports = class WikiStartupPlugin extends Plugin {
  async onload() {
    // Show modal on startup after a short delay
    this.app.workspace.onLayoutReady(() => {
      setTimeout(() => new WikiStartupModal(this.app, this).open(), 800);
    });

    // Register command: show popup manually
    this.addCommand({
      id: 'wiki-startup-show',
      name: 'Show Wiki-Linux status popup',
      callback: () => new WikiStartupModal(this.app, this).open(),
    });

    // Ribbon icon
    this.addRibbonIcon('activity', 'Wiki-Linux Status', () => {
      new WikiStartupModal(this.app, this).open();
    });
  }

  onunload() {}
};
