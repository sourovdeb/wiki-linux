function getWebviewHtml() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>WP Control Studio</title>
  <style>
    :root {
      --radius: 10px;
      --gap: 10px;
      --shell-bg: linear-gradient(160deg, rgba(31, 45, 54, 0.35), rgba(54, 45, 31, 0.25));
      --ok: #4aa977;
      --warn: #d59f34;
      --err: #d35d5d;
      --muted: var(--vscode-descriptionForeground);
      --fg: var(--vscode-editor-foreground);
      --bg: var(--vscode-editor-background);
      --card: var(--vscode-sideBar-background);
      --edge: var(--vscode-panel-border);
      --focus: var(--vscode-focusBorder);
      --btn: var(--vscode-button-background);
      --btn-fg: var(--vscode-button-foreground);
      --btn-hover: var(--vscode-button-hoverBackground);
    }

    * {
      box-sizing: border-box;
    }

    html,
    body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      font-size: 13px;
      color: var(--fg);
      background: var(--bg);
      font-family: 'Segoe UI', 'Noto Sans', sans-serif;
    }

    .shell {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: var(--shell-bg);
    }

    .top {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      border-bottom: 1px solid var(--edge);
      background: color-mix(in srgb, var(--card) 86%, transparent);
      backdrop-filter: blur(4px);
    }

    .title {
      font-weight: 700;
      letter-spacing: 0.2px;
      margin-right: auto;
    }

    .chip {
      font-size: 11px;
      padding: 2px 9px;
      border-radius: 999px;
      border: 1px solid var(--edge);
      color: var(--muted);
    }

    .tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      padding: 8px 10px;
      border-bottom: 1px solid var(--edge);
      background: color-mix(in srgb, var(--card) 82%, transparent);
    }

    .tab {
      border: 1px solid transparent;
      background: transparent;
      color: var(--muted);
      padding: 6px 10px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 12px;
    }

    .tab.active {
      border-color: var(--focus);
      color: var(--fg);
      background: color-mix(in srgb, var(--focus) 18%, transparent);
    }

    .views {
      min-height: 0;
      flex: 1;
      display: flex;
    }

    .view {
      display: none;
      flex: 1;
      min-height: 0;
      overflow: auto;
      padding: 12px;
      gap: var(--gap);
      flex-direction: column;
    }

    .view.active {
      display: flex;
    }

    .card {
      background: color-mix(in srgb, var(--card) 93%, transparent);
      border: 1px solid var(--edge);
      border-radius: var(--radius);
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .row {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }

    .row.grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      align-items: end;
    }

    label {
      display: flex;
      flex-direction: column;
      gap: 4px;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.45px;
      flex: 1;
      min-width: 170px;
    }

    input,
    select,
    textarea,
    button {
      font: inherit;
    }

    input,
    select,
    textarea {
      border: 1px solid var(--edge);
      background: var(--bg);
      color: var(--fg);
      border-radius: 8px;
      padding: 7px 9px;
      width: 100%;
    }

    textarea {
      min-height: 130px;
      resize: vertical;
    }

    button {
      border: 1px solid transparent;
      border-radius: 8px;
      background: var(--btn);
      color: var(--btn-fg);
      padding: 7px 10px;
      cursor: pointer;
      min-height: 30px;
    }

    button:hover {
      background: var(--btn-hover);
    }

    button.secondary {
      background: transparent;
      color: var(--fg);
      border-color: var(--edge);
    }

    button.danger {
      background: #5d2626;
      color: #fff;
      border-color: #8a3e3e;
    }

    .split {
      display: grid;
      grid-template-columns: 1.1fr 1fr;
      gap: 10px;
    }

    .meta {
      color: var(--muted);
      font-size: 12px;
    }

    .log-panel {
      min-height: 250px;
      overflow: auto;
      border: 1px solid var(--edge);
      border-radius: var(--radius);
      background: var(--bg);
      padding: 8px;
      font-family: 'Cascadia Mono', 'Consolas', monospace;
      font-size: 12px;
      line-height: 1.5;
    }

    .log-line {
      display: grid;
      grid-template-columns: 150px 1fr;
      gap: 10px;
      border-bottom: 1px dashed color-mix(in srgb, var(--edge) 65%, transparent);
      padding: 4px 0;
    }

    .log-line.ok {
      color: var(--ok);
    }

    .log-line.warn {
      color: var(--warn);
    }

    .log-line.error {
      color: var(--err);
    }

    .list {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .item {
      border: 1px solid var(--edge);
      border-radius: 8px;
      padding: 8px;
      background: color-mix(in srgb, var(--bg) 85%, transparent);
      display: flex;
      gap: 8px;
      align-items: center;
    }

    .item .title {
      flex: 1;
      font-size: 12px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .badge {
      border-radius: 999px;
      padding: 2px 8px;
      border: 1px solid var(--edge);
      font-size: 11px;
      color: var(--muted);
    }

    .review-title {
      font-size: 16px;
      font-weight: 700;
      margin: 0;
    }

    .hidden {
      display: none !important;
    }

    .guide-list {
      margin: 0;
      padding-left: 18px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .guide-list li {
      color: var(--fg);
    }

    @media (max-width: 980px) {
      .split {
        grid-template-columns: 1fr;
      }
      .log-line {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="top">
      <div class="title">WP Control Studio</div>
      <div class="chip" id="providerChip">provider: openwebui</div>
      <div class="chip" id="siteChip">site: not connected</div>
    </div>

    <div class="tabs">
      <button class="tab active" data-tab="generate">Generate</button>
      <button class="tab" data-tab="posts">Posts</button>
      <button class="tab" data-tab="queue">Queue</button>
      <button class="tab" data-tab="logs">Logs</button>
      <button class="tab" data-tab="settings">Settings</button>
    </div>

    <div class="views">
      <section class="view active" id="view-generate">
        <div class="card">
          <h4 style="margin:0;">Step-by-step Quick Start</h4>
          <ol class="guide-list">
            <li>Open Settings and set WordPress URL, credentials, and AI provider.</li>
            <li>In Queue, click Ping AutoPilot to verify your AutoPilot environment.</li>
            <li>Generate or import article drafts, then add them to queue.</li>
            <li>Run AutoPilot Dry Run and review output in Logs.</li>
            <li>Run AutoPilot Live Run when dry run output looks correct.</li>
          </ol>
          <div class="meta">This guide stays at the top so new users can follow the exact flow every time.</div>
        </div>

        <div class="card">
          <div class="row grid">
            <label>
              Topic
              <input id="topic" placeholder="Topic or article idea" />
            </label>
            <label>
              Tone
              <select id="tone">
                <option value="professional">Professional</option>
                <option value="friendly">Friendly</option>
                <option value="educational">Educational</option>
                <option value="persuasive">Persuasive</option>
              </select>
            </label>
            <label>
              Word count
              <select id="wordCount">
                <option value="450">450</option>
                <option value="700" selected>700</option>
                <option value="950">950</option>
                <option value="1200">1200</option>
              </select>
            </label>
          </div>

          <div class="row">
            <button id="generateBtn">Generate</button>
            <button class="secondary" id="queueBtn">Add Review To Queue</button>
          </div>
        </div>

        <div class="card hidden" id="reviewCard">
          <h3 class="review-title" id="reviewTitle"></h3>
          <div class="meta" id="reviewMeta"></div>
          <textarea id="reviewContent"></textarea>
          <div class="row">
            <button id="draftBtn">Create Draft</button>
            <button id="publishBtn" class="secondary">Publish Explicitly</button>
            <input id="scheduleDate" type="datetime-local" style="max-width: 220px;" />
            <button id="scheduleBtn" class="secondary">Schedule</button>
          </div>
        </div>
      </section>

      <section class="view" id="view-posts">
        <div class="card">
          <div class="row">
            <label>
              Status filter
              <select id="postStatus">
                <option value="">All</option>
                <option value="draft">Draft</option>
                <option value="future">Future</option>
                <option value="publish">Publish</option>
              </select>
            </label>
            <button id="refreshPosts">Refresh</button>
          </div>
          <div class="list" id="postList"></div>
        </div>
      </section>

      <section class="view" id="view-queue">
        <div class="card">
          <div class="row">
            <button id="runQueue">Run Queue</button>
            <button id="importArticles" class="secondary">Import Articles Folder</button>
            <div class="meta">Queue runs draft creation only for safety.</div>
          </div>
          <div class="list" id="queueList"></div>
        </div>

        <div class="card">
          <h4 style="margin:0;">WordPress AutoPilot</h4>
          <div class="row">
            <button id="autopilotPing" class="secondary">Ping AutoPilot</button>
            <button id="autopilotDryRun" class="secondary">Dry Run Queue</button>
            <button id="autopilotLiveRun">Live Run Queue</button>
          </div>
          <div class="meta">AutoPilot exports the current queue to CSV and executes the existing automation pipeline. Dry run first is recommended.</div>
        </div>
      </section>

      <section class="view" id="view-logs">
        <div class="card">
          <div class="row">
            <button id="testConnection">Test Connection</button>
            <button id="clearLogs" class="secondary">Clear</button>
          </div>
          <div class="log-panel" id="logPanel"></div>
        </div>
      </section>

      <section class="view" id="view-settings">
        <div class="split">
          <div class="card">
            <h4>WordPress</h4>
            <label>
              Site URL
              <input id="wordpressUrl" placeholder="https://example.com" />
            </label>
            <label>
              Username
              <input id="wpUser" placeholder="wp-user" />
            </label>
            <label>
              App Password
              <input id="wpAppPassword" type="password" placeholder="xxxx xxxx xxxx" />
            </label>
            <label>
              Plugin Key
              <input id="pluginKey" type="password" placeholder="optional" />
            </label>
          </div>

          <div class="card">
            <h4>AI Provider</h4>
            <label>
              Provider
              <select id="aiProvider">
                <option value="openwebui">OpenWebUI</option>
                <option value="ollama">Ollama</option>
                <option value="claude">Claude</option>
                <option value="deepseek">DeepSeek</option>
              </select>
            </label>
            <label>
              OpenWebUI URL
              <input id="openwebuiUrl" placeholder="http://127.0.0.1:8080" />
            </label>
            <label>
              OpenWebUI Model
              <input id="openwebuiModel" placeholder="llama3.2" list="modelHints" />
            </label>
            <label>
              OpenWebUI API Key
              <input id="openwebuiApiKey" type="password" placeholder="optional" />
            </label>
            <label>
              Ollama URL
              <input id="ollamaUrl" placeholder="http://127.0.0.1:11434" />
            </label>
            <label>
              Ollama Model
              <input id="ollamaModel" placeholder="llama3.2" list="modelHints" />
            </label>
            <datalist id="modelHints"></datalist>
            <label>
              Claude Key
              <input id="claudeKey" type="password" placeholder="sk-ant-..." />
            </label>
            <label>
              DeepSeek Key
              <input id="deepseekKey" type="password" placeholder="sk-..." />
            </label>
            <label style="text-transform:none;letter-spacing:0;font-size:12px;color:var(--fg);display:flex;flex-direction:row;align-items:center;gap:8px;">
              <input id="approvalMode" type="checkbox" checked style="width:auto;" />
              Approval mode required before posting
            </label>
            <label>
              Articles Folder
              <input id="articlesDir" placeholder="default: ../articles" />
            </label>
            <h4 style="margin:6px 0 0 0;">WP AutoPilot</h4>
            <label>
              AutoPilot Automation Directory
              <input id="autopilotAutomationDir" placeholder="default: workspace/user/development/tools/wordpress-control/automation" />
            </label>
            <label>
              AutoPilot Python Path
              <input id="autopilotPythonPath" placeholder="default: automation/.venv/bin/python" />
            </label>
            <label style="text-transform:none;letter-spacing:0;font-size:12px;color:var(--fg);display:flex;flex-direction:row;align-items:center;gap:8px;">
              <input id="autopilotUseDeepSeek" type="checkbox" style="width:auto;" />
              Use DeepSeek enrichment during AutoPilot runs
            </label>
            <div class="row">
              <button id="discoverModels" class="secondary">Discover Models</button>
              <button id="saveSettings">Save Settings</button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>

  <script>
    const vscode = acquireVsCodeApi();
    let currentPost = null;

    function send(cmd, data) {
      vscode.postMessage({ cmd: cmd, data: data || {} });
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab').forEach((el) => {
        el.classList.toggle('active', el.dataset.tab === tabId);
      });
      document.querySelectorAll('.view').forEach((el) => {
        el.classList.toggle('active', el.id === 'view-' + tabId);
      });
    }

    function appendLog(entry) {
      const panel = document.getElementById('logPanel');
      const row = document.createElement('div');
      row.className = 'log-line ' + (entry.level || 'info');
      const t = new Date(entry.time || Date.now()).toLocaleTimeString();
      row.innerHTML = '<div>' + t + ' [' + (entry.level || 'info') + ']</div><div>' + escapeHtml(entry.message || '') + '</div>';
      panel.appendChild(row);
      panel.scrollTop = panel.scrollHeight;
    }

    function renderPosts(posts) {
      const list = document.getElementById('postList');
      if (!posts || !posts.length) {
        list.innerHTML = '<div class="meta">No posts found.</div>';
        return;
      }

      list.innerHTML = '';
      posts.forEach((p) => {
        const item = document.createElement('div');
        item.className = 'item';
        const title = p.title?.rendered || p.title || 'Untitled';
        const status = p.status || 'unknown';
        item.innerHTML = '<span class="badge">' + escapeHtml(status) + '</span>' +
          '<span class="title" title="' + escapeHtml(title) + '">' + escapeHtml(title) + '</span>' +
          '<button class="secondary" data-action="publish">Publish</button>' +
          '<button class="danger" data-action="delete">Delete</button>';

        item.querySelector('[data-action="publish"]').addEventListener('click', () => {
          send('publish_post', { postId: p.id });
        });

        item.querySelector('[data-action="delete"]').addEventListener('click', () => {
          send('delete_post', { postId: p.id, force: false });
        });

        list.appendChild(item);
      });
    }

    function renderQueue(items) {
      const list = document.getElementById('queueList');
      if (!items || !items.length) {
        list.innerHTML = '<div class="meta">Queue is empty.</div>';
        return;
      }
      list.innerHTML = '';
      items.forEach((item, idx) => {
        const row = document.createElement('div');
        row.className = 'item';
        row.innerHTML = '<span class="badge">' + (idx + 1) + '</span><span class="title">' + escapeHtml(item.title || 'Untitled') + '</span>';
        list.appendChild(row);
      });
    }

    function showReview(post) {
      currentPost = post;
      document.getElementById('reviewCard').classList.remove('hidden');
      document.getElementById('reviewTitle').textContent = post.title || 'Untitled';
      document.getElementById('reviewMeta').textContent = 'SEO title: ' + (post.seo_title || '') + ' | Meta: ' + (post.meta_desc || '');
      document.getElementById('reviewContent').value = post.content || '';
    }

    function collectReviewPost() {
      if (!currentPost) {
        return null;
      }
      return Object.assign({}, currentPost, {
        content: document.getElementById('reviewContent').value
      });
    }

    function collectSettings() {
      return {
        wordpressUrl: document.getElementById('wordpressUrl').value.trim(),
        wpUser: document.getElementById('wpUser').value.trim(),
        wpAppPassword: document.getElementById('wpAppPassword').value.trim(),
        pluginKey: document.getElementById('pluginKey').value.trim(),
        aiProvider: document.getElementById('aiProvider').value,
        openwebuiUrl: document.getElementById('openwebuiUrl').value.trim(),
        openwebuiModel: document.getElementById('openwebuiModel').value.trim(),
        openwebuiApiKey: document.getElementById('openwebuiApiKey').value.trim(),
        ollamaUrl: document.getElementById('ollamaUrl').value.trim(),
        ollamaModel: document.getElementById('ollamaModel').value.trim(),
        claudeKey: document.getElementById('claudeKey').value.trim(),
        deepseekKey: document.getElementById('deepseekKey').value.trim(),
        approvalMode: document.getElementById('approvalMode').checked,
        articlesDir: document.getElementById('articlesDir').value.trim(),
        autopilotAutomationDir: document.getElementById('autopilotAutomationDir').value.trim(),
        autopilotPythonPath: document.getElementById('autopilotPythonPath').value.trim(),
        autopilotUseDeepSeek: document.getElementById('autopilotUseDeepSeek').checked
      };
    }

    function applySettings(data) {
      if (!data) {
        return;
      }
      document.getElementById('wordpressUrl').value = data.wordpressUrl || '';
      document.getElementById('wpUser').value = data.wpUser || '';
      document.getElementById('wpAppPassword').value = data.wpAppPassword || '';
      document.getElementById('pluginKey').value = data.pluginKey || '';
      document.getElementById('aiProvider').value = data.aiProvider || 'openwebui';
      document.getElementById('openwebuiUrl').value = data.openwebuiUrl || 'http://127.0.0.1:8080';
      document.getElementById('openwebuiModel').value = data.openwebuiModel || 'llama3.2';
      document.getElementById('openwebuiApiKey').value = data.openwebuiApiKey || '';
      document.getElementById('ollamaUrl').value = data.ollamaUrl || 'http://127.0.0.1:11434';
      document.getElementById('ollamaModel').value = data.ollamaModel || 'llama3.2';
      document.getElementById('claudeKey').value = data.claudeKey || '';
      document.getElementById('deepseekKey').value = data.deepseekKey || '';
      document.getElementById('approvalMode').checked = data.approvalMode !== false;
      document.getElementById('articlesDir').value = data.articlesDir || '';
      document.getElementById('autopilotAutomationDir').value = data.autopilotAutomationDir || '';
      document.getElementById('autopilotPythonPath').value = data.autopilotPythonPath || '';
      document.getElementById('autopilotUseDeepSeek').checked = data.autopilotUseDeepSeek === true;

      document.getElementById('providerChip').textContent = 'provider: ' + (data.aiProvider || 'openwebui');
      if (data.wordpressUrl) {
        try {
          const u = new URL(data.wordpressUrl);
          document.getElementById('siteChip').textContent = 'site: ' + u.hostname;
        } catch {
          document.getElementById('siteChip').textContent = 'site: configured';
        }
      }
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
    }

    document.querySelectorAll('.tab').forEach((btn) => {
      btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    document.getElementById('generateBtn').addEventListener('click', () => {
      send('generate', {
        topic: document.getElementById('topic').value,
        tone: document.getElementById('tone').value,
        wordCount: Number(document.getElementById('wordCount').value)
      });
    });

    document.getElementById('queueBtn').addEventListener('click', () => {
      const post = collectReviewPost();
      if (!post) {
        return;
      }
      send('queue_add', { post: post });
    });

    document.getElementById('draftBtn').addEventListener('click', () => {
      const post = collectReviewPost();
      if (!post) {
        return;
      }
      send('create_draft', { post: post });
    });

    document.getElementById('publishBtn').addEventListener('click', () => {
      const id = prompt('Enter post ID to publish explicitly');
      if (!id) {
        return;
      }
      send('publish_post', { postId: Number(id) });
    });

    document.getElementById('scheduleBtn').addEventListener('click', () => {
      const id = prompt('Enter post ID to schedule');
      if (!id) {
        return;
      }
      const raw = document.getElementById('scheduleDate').value;
      if (!raw) {
        alert('Select a schedule date and time first.');
        return;
      }
      send('schedule_post', { postId: Number(id), date: new Date(raw).toISOString() });
    });

    document.getElementById('refreshPosts').addEventListener('click', () => {
      send('list_posts', {
        status: document.getElementById('postStatus').value,
        page: 1,
        per_page: 20
      });
    });

    document.getElementById('postStatus').addEventListener('change', () => {
      send('list_posts', {
        status: document.getElementById('postStatus').value,
        page: 1,
        per_page: 20
      });
    });

    document.getElementById('runQueue').addEventListener('click', () => {
      send('queue_run');
    });

    document.getElementById('importArticles').addEventListener('click', () => {
      send('queue_import_articles');
    });

    document.getElementById('autopilotPing').addEventListener('click', () => {
      send('autopilot_ping');
    });

    document.getElementById('autopilotDryRun').addEventListener('click', () => {
      send('autopilot_dry_run');
    });

    document.getElementById('autopilotLiveRun').addEventListener('click', () => {
      const ok = confirm('Run AutoPilot live mode now? This can schedule posts in WordPress.');
      if (!ok) {
        return;
      }
      send('autopilot_live_run');
    });

    document.getElementById('testConnection').addEventListener('click', () => {
      send('test_connection');
    });

    document.getElementById('clearLogs').addEventListener('click', () => {
      document.getElementById('logPanel').innerHTML = '';
    });

    document.getElementById('saveSettings').addEventListener('click', () => {
      send('save_settings', collectSettings());
    });

    document.getElementById('discoverModels').addEventListener('click', () => {
      send('discover_models');
    });

    window.addEventListener('message', (event) => {
      const msg = event.data || {};
      if (msg.cmd === 'settings') {
        applySettings(msg.data);
      }
      if (msg.cmd === 'log') {
        appendLog(msg.data || {});
      }
      if (msg.cmd === 'logs_snapshot') {
        (msg.data || []).forEach((entry) => appendLog(entry));
      }
      if (msg.cmd === 'review_post') {
        showReview(msg.data || {});
      }
      if (msg.cmd === 'posts_list') {
        renderPosts(msg.data || []);
      }
      if (msg.cmd === 'queue') {
        renderQueue(msg.data || []);
      }
      if (msg.cmd === 'queue_failures') {
        alert('Some queue items failed. See Logs tab for details.');
      }
      if (msg.cmd === 'models') {
        const dl = document.getElementById('modelHints');
        dl.innerHTML = '';
        (msg.data || []).forEach((name) => {
          const opt = document.createElement('option');
          opt.value = name;
          dl.appendChild(opt);
        });
      }
      if (msg.cmd === 'status') {
        if (msg.data && msg.data.error) {
          alert('Connection failed: ' + msg.data.error);
        }
      }
      if (msg.cmd === 'ui_info') {
        alert(msg.data?.message || 'Action completed.');
      }
      if (msg.cmd === 'ui_error') {
        alert(msg.data?.message || 'Command failed.');
      }
    });

    send('load_settings');
  </script>
</body>
</html>`;
}

module.exports = {
  getWebviewHtml
};
