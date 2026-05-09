const vscode = require('vscode');

const { getWebviewHtml } = require('./webview');
const { LogStore } = require('./services/log-store');
const { WPClient } = require('./services/wp-client');
const { AIClient } = require('./services/ai-client');
const { validateGeneratedPost, validateScheduleDate } = require('./services/validator');
const { importArticlesForQueue } = require('./services/article-importer');
const { pingAutoPilot, runAutoPilotQueue } = require('./services/autopilot-runner');

let panel = null;
const queue = [];
const logStore = new LogStore(400);

function appendLog(level, message, detail = '') {
  const entry = logStore.add(level, message, detail);
  if (panel) {
    panel.webview.postMessage({ cmd: 'log', data: entry });
  }
  return entry;
}

function getConfig() {
  return vscode.workspace.getConfiguration('wpControl');
}

const wpClient = new WPClient(getConfig, appendLog);
const aiClient = new AIClient(getConfig, appendLog);

function settingsPayload() {
  const c = getConfig();
  return {
    wordpressUrl: c.get('wordpressUrl'),
    wpUser: c.get('wpUser'),
    wpAppPassword: c.get('wpAppPassword'),
    pluginKey: c.get('pluginKey'),
    aiProvider: c.get('aiProvider'),
    openwebuiUrl: c.get('openwebuiUrl'),
    openwebuiModel: c.get('openwebuiModel'),
    openwebuiApiKey: c.get('openwebuiApiKey'),
    ollamaUrl: c.get('ollamaUrl'),
    ollamaModel: c.get('ollamaModel'),
    claudeKey: c.get('claudeKey'),
    deepseekKey: c.get('deepseekKey'),
    approvalMode: c.get('approvalMode') !== false,
    articlesDir: c.get('articlesDir'),
    autopilotAutomationDir: c.get('autopilotAutomationDir'),
    autopilotPythonPath: c.get('autopilotPythonPath'),
    autopilotUseDeepSeek: c.get('autopilotUseDeepSeek') === true
  };
}

function trimDetail(text, max = 1400) {
  const src = String(text || '').trim();
  if (!src) {
    return '';
  }
  if (src.length <= max) {
    return src;
  }
  return `${src.slice(0, max)}\n...[truncated]`;
}

async function saveSettings(data) {
  const c = getConfig();
  const entries = Object.entries(data || {});
  for (const [key, value] of entries) {
    await c.update(key, value, vscode.ConfigurationTarget.Global);
  }
  appendLog('ok', 'Settings saved.');
  if (panel) {
    panel.webview.postMessage({ cmd: 'settings', data: settingsPayload() });
  }
}

function sendQueueSnapshot() {
  if (!panel) {
    return;
  }
  panel.webview.postMessage({ cmd: 'queue', data: queue });
}

async function runHealthCheck(showToast = false) {
  try {
    const health = await wpClient.health();
    const info = await wpClient.info();
    const siteName = info.site_name || info.site || 'connected';
    appendLog('ok', `Connected to ${siteName}`);
    if (panel) {
      panel.webview.postMessage({ cmd: 'status', data: { health, info } });
    }
    if (showToast) {
      vscode.window.showInformationMessage(`WP Control connected: ${siteName}`);
    }
  } catch (err) {
    appendLog('error', `Health check failed: ${err.message}`);
    if (panel) {
      panel.webview.postMessage({ cmd: 'status', data: { error: err.message } });
    }
    if (showToast) {
      vscode.window.showErrorMessage(`WP Control health failed: ${err.message}`);
    }
  }
}

async function listPosts(params = {}) {
  try {
    const payload = Object.assign({
      per_page: 20,
      page: 1
    }, params);
    const data = await wpClient.listPosts(payload);
    const posts = data.value || data.posts || [];
    if (panel) {
      panel.webview.postMessage({ cmd: 'posts_list', data: posts });
    }
    appendLog('info', `Loaded ${posts.length} posts.`);
  } catch (err) {
    appendLog('error', `List posts failed: ${err.message}`);
  }
}

async function generatePost(data) {
  const topic = String(data.topic || '').trim();
  if (!topic) {
    throw new Error('Topic is required.');
  }

  const tone = String(data.tone || 'professional');
  const wordCount = Number(data.wordCount || 700);

  const raw = await aiClient.generatePost({ topic, tone, wordCount });
  const post = validateGeneratedPost(raw);

  appendLog('ok', `Generated post draft: ${post.title}`);

  const approvalMode = getConfig().get('approvalMode') !== false;
  if (approvalMode) {
    if (panel) {
      panel.webview.postMessage({ cmd: 'review_post', data: post });
    }
    return;
  }

  const created = await wpClient.createPost({ ...post, status: 'draft' });
  appendLog('ok', `Draft created automatically: ID ${created.id || 'unknown'}`);
  await listPosts();
}

async function createDraft(post) {
  const cleaned = validateGeneratedPost(post);
  const created = await wpClient.createPost({ ...cleaned, status: 'draft' });
  appendLog('ok', `Draft created: ID ${created.id || 'unknown'}`);
  await listPosts();
}

async function publishPost(postId) {
  if (!postId) {
    throw new Error('Post ID is required for publish.');
  }
  const res = await wpClient.publishPost(postId);
  appendLog('ok', `Post published: ID ${postId}`);
  await listPosts();
  return res;
}

async function schedulePost(postId, dateValue) {
  if (!postId) {
    throw new Error('Post ID is required for schedule.');
  }
  const iso = validateScheduleDate(dateValue);
  const res = await wpClient.schedulePost(postId, iso);
  appendLog('ok', `Post scheduled: ID ${postId}`);
  await listPosts();
  return res;
}

async function runQueue() {
  if (!queue.length) {
    appendLog('warn', 'Queue is empty.');
    return;
  }

  appendLog('info', `Running queue with ${queue.length} item(s).`);

  const failures = [];
  while (queue.length) {
    const item = queue.shift();
    try {
      await createDraft(item);
    } catch (err) {
      failures.push({ title: item.title || 'Untitled', error: err.message });
      appendLog('error', `Queue item failed: ${err.message}`);
    }
  }

  sendQueueSnapshot();

  if (failures.length) {
    appendLog('warn', `${failures.length} queue item(s) failed.`);
    if (panel) {
      panel.webview.postMessage({ cmd: 'queue_failures', data: failures });
    }
    return;
  }

  appendLog('ok', 'Queue completed successfully.');
}

function importArticlesIntoQueue() {
  const result = importArticlesForQueue(getConfig, appendLog);
  for (const post of result.posts) {
    queue.push(validateGeneratedPost(post));
  }
  sendQueueSnapshot();
  appendLog('ok', `Imported ${result.count} article(s) into queue from ${result.dir}`);
  return result;
}

async function pingAutoPilotService() {
  appendLog('info', 'Running AutoPilot ping check.');
  const result = await pingAutoPilot(getConfig);

  if (!result.success) {
    appendLog('error', `AutoPilot ping failed (exit ${result.exitCode}).`, trimDetail(result.output));
    throw new Error('AutoPilot ping failed. Check Logs for details.');
  }

  appendLog('ok', 'AutoPilot ping succeeded.', trimDetail(result.output));
  if (panel) {
    panel.webview.postMessage({
      cmd: 'ui_info',
      data: { message: 'AutoPilot ping succeeded. Environment is reachable.' }
    });
  }
}

async function runAutoPilotFromQueue(dryRun) {
  if (!queue.length) {
    throw new Error('Queue is empty. Add or import posts before running AutoPilot.');
  }

  const useDeepSeek = getConfig().get('autopilotUseDeepSeek') === true;
  const mode = dryRun ? 'dry run' : 'live run';
  appendLog('info', `Starting AutoPilot ${mode} for ${queue.length} queue item(s).`);

  const result = await runAutoPilotQueue({
    getConfig,
    posts: queue,
    dryRun,
    useDeepSeek
  });

  if (!result.success) {
    appendLog('error', `AutoPilot ${mode} failed (exit ${result.exitCode}).`, trimDetail(result.output));
    throw new Error(`AutoPilot ${mode} failed. Check Logs for details.`);
  }

  appendLog('ok', `AutoPilot ${mode} completed successfully.`, trimDetail(result.output));
  if (!dryRun) {
    queue.length = 0;
    sendQueueSnapshot();
  }

  if (panel) {
    panel.webview.postMessage({
      cmd: 'ui_info',
      data: {
        message: dryRun
          ? 'AutoPilot dry run completed. Review Logs, then run live when ready.'
          : 'AutoPilot live run completed and queue was cleared.'
      }
    });
  }
}

async function onMessage(msg) {
  const cmd = msg?.cmd;
  const data = msg?.data || {};

  try {
    switch (cmd) {
      case 'load_settings': {
        if (panel) {
          panel.webview.postMessage({ cmd: 'settings', data: settingsPayload() });
          panel.webview.postMessage({ cmd: 'logs_snapshot', data: logStore.all() });
        }
        sendQueueSnapshot();
        await listPosts();
        break;
      }

      case 'save_settings': {
        await saveSettings(data);
        break;
      }

      case 'test_connection': {
        await runHealthCheck(false);
        break;
      }

      case 'discover_models': {
        const models = await aiClient.discoverModels();
        if (panel) {
          panel.webview.postMessage({ cmd: 'models', data: models });
        }
        appendLog('ok', `Discovered ${models.length} model(s).`);
        break;
      }

      case 'queue_import_articles': {
        const result = importArticlesIntoQueue();
        if (panel) {
          panel.webview.postMessage({
            cmd: 'ui_info',
            data: { message: `Imported ${result.count} article(s) from ${result.dir}` }
          });
        }
        break;
      }

      case 'generate': {
        await generatePost(data);
        break;
      }

      case 'create_draft': {
        await createDraft(data.post || data);
        break;
      }

      case 'publish_post': {
        await publishPost(Number(data.postId));
        break;
      }

      case 'schedule_post': {
        await schedulePost(Number(data.postId), data.date);
        break;
      }

      case 'list_posts': {
        await listPosts(data);
        break;
      }

      case 'delete_post': {
        await wpClient.deletePost(Number(data.postId), Boolean(data.force));
        appendLog('ok', `Post moved to trash: ID ${data.postId}`);
        await listPosts();
        break;
      }

      case 'queue_add': {
        queue.push(validateGeneratedPost(data.post || data));
        appendLog('info', `Added to queue: ${data.post?.title || data.title || 'Untitled'}`);
        sendQueueSnapshot();
        break;
      }

      case 'queue_run': {
        await runQueue();
        break;
      }

      case 'autopilot_ping': {
        await pingAutoPilotService();
        break;
      }

      case 'autopilot_dry_run': {
        await runAutoPilotFromQueue(true);
        break;
      }

      case 'autopilot_live_run': {
        await runAutoPilotFromQueue(false);
        break;
      }

      default:
        appendLog('warn', `Unknown command: ${cmd || 'empty'}`);
    }
  } catch (err) {
    appendLog('error', err.message || 'Unhandled command error.');
    if (panel) {
      panel.webview.postMessage({ cmd: 'ui_error', data: { message: err.message || String(err) } });
    }
  }
}

function openStudio(context) {
  if (panel) {
    panel.reveal(vscode.ViewColumn.One);
    return;
  }

  panel = vscode.window.createWebviewPanel(
    'wpControlStudio',
    'WP Control Studio',
    vscode.ViewColumn.One,
    {
      enableScripts: true,
      retainContextWhenHidden: true
    }
  );

  panel.webview.html = getWebviewHtml();

  panel.webview.onDidReceiveMessage(onMessage, undefined, context.subscriptions);

  panel.onDidDispose(() => {
    panel = null;
  }, null, context.subscriptions);

  appendLog('info', 'Studio opened.');
}

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand('wpControl.openStudio', () => openStudio(context)),
    vscode.commands.registerCommand('wpControl.siteHealth', async () => {
      openStudio(context);
      await runHealthCheck(true);
    }),
    vscode.commands.registerCommand('wpControl.importArticlesToQueue', () => {
      openStudio(context);
      try {
        const result = importArticlesIntoQueue();
        vscode.window.showInformationMessage(`WP Control imported ${result.count} article(s) to queue.`);
      } catch (err) {
        appendLog('error', err.message || 'Article import failed.');
        vscode.window.showErrorMessage(`WP Control import failed: ${err.message}`);
      }
    }),
    vscode.commands.registerCommand('wpControl.autopilotPing', async () => {
      openStudio(context);
      try {
        await pingAutoPilotService();
      } catch (err) {
        appendLog('error', err.message || 'AutoPilot ping failed.');
        vscode.window.showErrorMessage(`WP AutoPilot ping failed: ${err.message}`);
      }
    }),
    vscode.commands.registerCommand('wpControl.autopilotDryRun', async () => {
      openStudio(context);
      try {
        await runAutoPilotFromQueue(true);
      } catch (err) {
        appendLog('error', err.message || 'AutoPilot dry run failed.');
        vscode.window.showErrorMessage(`WP AutoPilot dry run failed: ${err.message}`);
      }
    }),
    vscode.commands.registerCommand('wpControl.autopilotLiveRun', async () => {
      openStudio(context);
      try {
        await runAutoPilotFromQueue(false);
      } catch (err) {
        appendLog('error', err.message || 'AutoPilot live run failed.');
        vscode.window.showErrorMessage(`WP AutoPilot live run failed: ${err.message}`);
      }
    })
  );

  appendLog('info', 'WP Control prototype activated.');
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};
