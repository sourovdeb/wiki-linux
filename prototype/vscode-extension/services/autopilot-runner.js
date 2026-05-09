const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const vscode = require('vscode');

function resolveAutomationDir(getConfig) {
  const cfg = getConfig();
  const override = String(cfg.get('autopilotAutomationDir') || '').trim();
  if (override) {
    return path.resolve(override);
  }

  const workspace = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath;
  if (workspace) {
    return path.join(workspace, 'user', 'development', 'tools', 'wordpress-control', 'automation');
  }

  return path.resolve(__dirname, '..', '..', '..', 'user', 'development', 'tools', 'wordpress-control', 'automation');
}

function resolvePythonPath(getConfig, automationDir) {
  const cfg = getConfig();
  const override = String(cfg.get('autopilotPythonPath') || '').trim();
  if (override) {
    return path.resolve(override);
  }
  return path.join(automationDir, '.venv', 'bin', 'python');
}

function ensureAutomationReady(automationDir, pythonPath) {
  if (!fs.existsSync(automationDir) || !fs.statSync(automationDir).isDirectory()) {
    throw new Error(`AutoPilot automation directory not found: ${automationDir}`);
  }

  const mainPy = path.join(automationDir, 'main.py');
  if (!fs.existsSync(mainPy)) {
    throw new Error(`AutoPilot entrypoint missing: ${mainPy}`);
  }

  if (!fs.existsSync(pythonPath)) {
    throw new Error(`AutoPilot Python executable not found: ${pythonPath}`);
  }
}

function csvCell(value) {
  const s = String(value ?? '');
  return `"${s.replaceAll('"', '""')}"`;
}

function postToAutoPilotRow(post, index) {
  const title = String(post.title || '').trim();
  const content = String(post.content || '').trim();
  const categories = Array.isArray(post.categories)
    ? post.categories.map((v) => String(v).trim()).filter(Boolean)
    : [];
  const tags = Array.isArray(post.tags)
    ? post.tags.map((v) => String(v).trim()).filter(Boolean)
    : String(post.tags || '').split(',').map((v) => v.trim()).filter(Boolean);

  const seoKeyword = String(post.focus_keyword || tags[0] || '').trim();

  return {
    title,
    content,
    category: categories.join(', '),
    tags: tags.join(', '),
    seo_keyword: seoKeyword,
    publish_date: '',
    status: 'ready',
    priority: String(index + 1)
  };
}

function writeQueueCsv(posts, automationDir) {
  const queuePath = path.join(automationDir, '_studio_autopilot_queue.csv');
  const headers = ['title', 'content', 'category', 'tags', 'seo_keyword', 'publish_date', 'status', 'priority'];

  const lines = [headers.join(',')];
  posts.forEach((post, index) => {
    const row = postToAutoPilotRow(post, index);
    if (!row.title || !row.content) {
      return;
    }
    const csvRow = headers.map((h) => csvCell(row[h] || '')).join(',');
    lines.push(csvRow);
  });

  if (lines.length < 2) {
    throw new Error('Queue has no valid posts for AutoPilot export.');
  }

  fs.writeFileSync(queuePath, `${lines.join('\n')}\n`, 'utf8');
  return queuePath;
}

function runProcess(command, args, cwd) {
  return new Promise((resolve, reject) => {
    const proc = spawn(command, args, {
      cwd,
      env: process.env,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let out = '';
    let err = '';

    proc.stdout.on('data', (chunk) => {
      out += String(chunk);
    });

    proc.stderr.on('data', (chunk) => {
      err += String(chunk);
    });

    proc.on('error', (spawnErr) => {
      reject(spawnErr);
    });

    proc.on('close', (code) => {
      resolve({
        code: Number(code || 0),
        stdout: out,
        stderr: err,
        output: `${out}${err}`.trim()
      });
    });
  });
}

async function pingAutoPilot(getConfig) {
  const automationDir = resolveAutomationDir(getConfig);
  const pythonPath = resolvePythonPath(getConfig, automationDir);
  ensureAutomationReady(automationDir, pythonPath);

  const result = await runProcess(pythonPath, ['main.py', 'ping'], automationDir);
  return {
    success: result.code === 0,
    automationDir,
    pythonPath,
    output: result.output,
    exitCode: result.code
  };
}

async function runAutoPilotQueue({ getConfig, posts, dryRun = true, useDeepSeek = false }) {
  const automationDir = resolveAutomationDir(getConfig);
  const pythonPath = resolvePythonPath(getConfig, automationDir);
  ensureAutomationReady(automationDir, pythonPath);

  if (!Array.isArray(posts) || !posts.length) {
    throw new Error('Queue is empty. Add or import posts before AutoPilot run.');
  }

  const queueFile = writeQueueCsv(posts, automationDir);
  const args = ['main.py', 'run', queueFile, '--yes'];

  if (dryRun) {
    args.push('--dry');
  }

  if (!useDeepSeek) {
    args.push('--no-ai');
  }

  const result = await runProcess(pythonPath, args, automationDir);

  return {
    success: result.code === 0,
    dryRun,
    useDeepSeek,
    queueFile,
    automationDir,
    pythonPath,
    output: result.output,
    exitCode: result.code
  };
}

module.exports = {
  pingAutoPilot,
  runAutoPilotQueue
};