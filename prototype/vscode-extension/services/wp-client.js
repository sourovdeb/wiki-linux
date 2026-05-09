const crypto = require('crypto');

async function getFetch() {
  if (typeof fetch === 'function') {
    return fetch;
  }
  const mod = await import('node-fetch');
  return mod.default;
}

class WPClient {
  constructor(getConfig, log) {
    this.getConfig = getConfig;
    this.log = log;
  }

  async request(path, { method = 'GET', body = null, idempotencyKey = '' } = {}) {
    const cfg = this.getConfig();
    const site = String(cfg.get('wordpressUrl') || '').replace(/\/$/, '');

    if (!site) {
      throw new Error('WordPress URL is not configured.');
    }

    const url = `${site}/wp-json/sourov/v2${path}`;
    const headers = {
      'Content-Type': 'application/json'
    };

    const pluginKey = String(cfg.get('pluginKey') || '');
    if (pluginKey) {
      headers['X-Sourov-Key'] = pluginKey;
    }

    const user = String(cfg.get('wpUser') || '');
    const pass = String(cfg.get('wpAppPassword') || '');
    if (user && pass) {
      const token = Buffer.from(`${user}:${pass}`).toString('base64');
      headers.Authorization = `Basic ${token}`;
    }

    const isMutation = ['POST', 'PATCH', 'DELETE'].includes(method.toUpperCase());
    if (isMutation) {
      headers['Idempotency-Key'] = idempotencyKey || crypto.randomUUID();
    }

    const options = { method, headers };
    if (body) {
      options.body = JSON.stringify(body);
    }

    this.log('info', `WP ${method} ${path}`);

    const fetchFn = await getFetch();
    const res = await fetchFn(url, options);

    let data = {};
    const text = await res.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = { raw: text };
      }
    }

    if (!res.ok) {
      const msg = data.error?.message || data.message || `Request failed with ${res.status}`;
      const err = new Error(msg);
      err.status = res.status;
      err.payload = data;
      throw err;
    }

    return data;
  }

  health() {
    return this.request('/health');
  }

  info() {
    return this.request('/info');
  }

  listPosts(params = {}) {
    const query = new URLSearchParams(params).toString();
    const suffix = query ? `?${query}` : '';
    return this.request(`/posts${suffix}`);
  }

  createPost(postData) {
    return this.request('/posts', { method: 'POST', body: postData });
  }

  publishPost(postId) {
    return this.request(`/posts/${postId}/publish`, { method: 'POST', body: {} });
  }

  schedulePost(postId, scheduleDate) {
    return this.request(`/posts/${postId}/schedule`, {
      method: 'POST',
      body: { date: scheduleDate }
    });
  }

  deletePost(postId, force = false) {
    return this.request(`/posts/${postId}?force=${force ? 'true' : 'false'}`, {
      method: 'DELETE'
    });
  }
}

module.exports = {
  WPClient
};
