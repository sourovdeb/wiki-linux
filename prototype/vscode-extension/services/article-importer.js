const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

function resolveArticlesDir(getConfig) {
  const cfg = getConfig();
  const override = String(cfg.get('articlesDir') || '').trim();
  if (override) {
    return path.resolve(override);
  }

  const workspace = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath;
  if (workspace) {
    return path.join(workspace, 'articles');
  }

  return path.resolve(__dirname, '..', '..', 'articles');
}

function parseFrontmatter(text) {
  const src = String(text || '');
  if (!src.startsWith('---\n')) {
    return { meta: {}, body: src.trim() };
  }

  const end = src.indexOf('\n---\n', 4);
  if (end < 0) {
    return { meta: {}, body: src.trim() };
  }

  const header = src.slice(4, end).split('\n');
  const body = src.slice(end + 5).trim();
  const meta = {};

  let listKey = '';
  for (const raw of header) {
    const line = raw.trimEnd();
    if (!line.trim()) {
      continue;
    }

    if (line.startsWith('  - ') || line.startsWith('- ')) {
      if (listKey) {
        const v = line.replace(/^\s*-\s*/, '').trim();
        if (!Array.isArray(meta[listKey])) {
          meta[listKey] = [];
        }
        if (v) {
          meta[listKey].push(v);
        }
      }
      continue;
    }

    const idx = line.indexOf(':');
    if (idx < 0) {
      continue;
    }

    const key = line.slice(0, idx).trim();
    let value = line.slice(idx + 1).trim();

    if (!key) {
      continue;
    }

    if (!value) {
      meta[key] = [];
      listKey = key;
      continue;
    }

    listKey = '';
    value = value.replace(/^"|"$/g, '').replace(/^'|'$/g, '');
    meta[key] = value;
  }

  return { meta, body };
}

function buildPostFromMarkdown(filePath, text) {
  const { meta, body } = parseFrontmatter(text);
  const title = String(meta.title || path.basename(filePath, path.extname(filePath))).trim();
  const seoTitle = String(meta.seo_title || title).trim();
  const metaDesc = String(meta.meta_desc || '').trim();
  const excerpt = metaDesc || body.replace(/\s+/g, ' ').slice(0, 160);

  const tags = Array.isArray(meta.tags)
    ? meta.tags.map((t) => String(t).trim()).filter(Boolean)
    : String(meta.tags || '')
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

  const category = String(meta.category || '').trim();
  const categories = category ? [category] : [];

  return {
    title,
    content: body,
    excerpt,
    seo_title: seoTitle,
    meta_desc: metaDesc || excerpt,
    tags,
    categories,
    source_file: path.basename(filePath)
  };
}

function importArticlesForQueue(getConfig, log) {
  const dir = resolveArticlesDir(getConfig);

  if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
    throw new Error(`Articles directory not found: ${dir}`);
  }

  const files = fs.readdirSync(dir)
    .filter((name) => name.toLowerCase().endsWith('.md'))
    .sort((a, b) => a.localeCompare(b));

  if (!files.length) {
    throw new Error(`No markdown files found in: ${dir}`);
  }

  const posts = [];
  for (const name of files) {
    const fullPath = path.join(dir, name);
    const raw = fs.readFileSync(fullPath, 'utf8');
    const post = buildPostFromMarkdown(fullPath, raw);

    if (!post.title || !post.content) {
      log('warn', `Skipping article with missing title/content: ${name}`);
      continue;
    }

    posts.push(post);
  }

  if (!posts.length) {
    throw new Error('No valid articles parsed for queue import.');
  }

  return {
    dir,
    count: posts.length,
    posts
  };
}

module.exports = {
  importArticlesForQueue
};
