const fs = require('fs');
const path = require('path');

const DEFAULT_TEMPLATE = `You are a WordPress content writer.
Return only valid JSON with this schema:
{
  "title": "",
  "content": "",
  "meta_desc": "",
  "seo_title": "",
  "tags": [],
  "excerpt": ""
}

Topic: {{topic}}
Tone: {{tone}}
Word count: {{wordCount}}
`;

async function getFetch() {
  if (typeof fetch === 'function') {
    return fetch;
  }
  const mod = await import('node-fetch');
  return mod.default;
}

class AIClient {
  constructor(getConfig, log) {
    this.getConfig = getConfig;
    this.log = log;
  }

  buildPrompt(topic, tone, wordCount) {
    const promptPath = path.join(__dirname, '..', 'templates', 'post-json.prompt.txt');
    let template = DEFAULT_TEMPLATE;

    try {
      template = fs.readFileSync(promptPath, 'utf8');
    } catch {
      this.log('warn', 'Prompt template file missing, using built-in template.');
    }

    return template
      .replaceAll('{{topic}}', topic)
      .replaceAll('{{tone}}', tone)
      .replaceAll('{{wordCount}}', String(wordCount));
  }

  async discoverOllamaModels() {
    const cfg = this.getConfig();
    const base = String(cfg.get('ollamaUrl') || 'http://127.0.0.1:11434').replace(/\/$/, '');
    const fetchFn = await getFetch();
    const res = await fetchFn(`${base}/api/tags`);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Failed to discover Ollama models.');
    }
    const models = (data.models || []).map((m) => m.name).sort();
    return models;
  }

  async discoverOpenWebUIModels() {
    const cfg = this.getConfig();
    const base = String(cfg.get('openwebuiUrl') || 'http://127.0.0.1:8080').replace(/\/$/, '');
    const key = String(cfg.get('openwebuiApiKey') || '');
    const headers = {};
    if (key) {
      headers.Authorization = `Bearer ${key}`;
    }

    const fetchFn = await getFetch();
    const res = await fetchFn(`${base}/api/models`, {
      method: 'GET',
      headers
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || data.detail || 'Failed to discover OpenWebUI models.');
    }

    const rows = Array.isArray(data) ? data : Array.isArray(data.data) ? data.data : [];
    return rows
      .map((m) => m.id || m.model || m.name)
      .filter(Boolean)
      .map((m) => String(m))
      .sort();
  }

  async discoverModels() {
    const cfg = this.getConfig();
    const provider = String(cfg.get('aiProvider') || 'openwebui');

    if (provider === 'openwebui') {
      return this.discoverOpenWebUIModels();
    }

    return this.discoverOllamaModels();
  }

  async generatePost({ topic, tone = 'professional', wordCount = 700 }) {
    const cfg = this.getConfig();
    const provider = String(cfg.get('aiProvider') || 'openwebui');
    this.log('info', `AI generation requested via provider: ${provider}`);

    if (provider === 'openwebui') {
      return this.generateWithOpenWebUI(topic, tone, wordCount);
    }
    if (provider === 'ollama') {
      return this.generateWithOllama(topic, tone, wordCount);
    }
    if (provider === 'claude') {
      return this.generateWithClaude(topic, tone, wordCount);
    }
    if (provider === 'deepseek') {
      return this.generateWithDeepSeek(topic, tone, wordCount);
    }

    throw new Error(`Unsupported AI provider: ${provider}`);
  }

  async generateWithOpenWebUI(topic, tone, wordCount) {
    const cfg = this.getConfig();
    const base = String(cfg.get('openwebuiUrl') || 'http://127.0.0.1:8080').replace(/\/$/, '');
    const model = String(cfg.get('openwebuiModel') || 'llama3.2');
    const key = String(cfg.get('openwebuiApiKey') || '');
    const prompt = this.buildPrompt(topic, tone, wordCount);

    const headers = {
      'Content-Type': 'application/json'
    };
    if (key) {
      headers.Authorization = `Bearer ${key}`;
    }

    const fetchFn = await getFetch();
    const res = await fetchFn(`${base}/api/chat/completions`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        model,
        stream: false,
        messages: [
          {
            role: 'system',
            content: 'Return only valid JSON with the required keys. Do not wrap in markdown.'
          },
          {
            role: 'user',
            content: prompt
          }
        ]
      })
    });

    const data = await res.json();
    if (!res.ok) {
      const msg = data.error?.message || data.error || data.detail || 'OpenWebUI generate failed.';
      throw new Error(msg);
    }

    const text = data.choices?.[0]?.message?.content || '';
    return this.parseModelJson(text);
  }

  async generateWithOllama(topic, tone, wordCount) {
    const cfg = this.getConfig();
    const base = String(cfg.get('ollamaUrl') || 'http://127.0.0.1:11434').replace(/\/$/, '');
    const model = String(cfg.get('ollamaModel') || 'llama3.2');
    const prompt = this.buildPrompt(topic, tone, wordCount);

    const fetchFn = await getFetch();
    const res = await fetchFn(`${base}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        prompt,
        stream: false
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Ollama generate failed.');
    }

    return this.parseModelJson(data.response || '');
  }

  async generateWithClaude(topic, tone, wordCount) {
    const cfg = this.getConfig();
    const key = String(cfg.get('claudeKey') || '');
    if (!key) {
      throw new Error('Claude key is missing.');
    }

    const prompt = this.buildPrompt(topic, tone, wordCount);
    const fetchFn = await getFetch();
    const res = await fetchFn('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 2500,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error?.message || 'Claude request failed.');
    }

    const text = data.content?.[0]?.text || '';
    return this.parseModelJson(text);
  }

  async generateWithDeepSeek(topic, tone, wordCount) {
    const cfg = this.getConfig();
    const key = String(cfg.get('deepseekKey') || '');
    if (!key) {
      throw new Error('DeepSeek key is missing.');
    }

    const prompt = this.buildPrompt(topic, tone, wordCount);
    const fetchFn = await getFetch();
    const res = await fetchFn('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${key}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [{ role: 'user', content: prompt }]
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error?.message || 'DeepSeek request failed.');
    }

    const text = data.choices?.[0]?.message?.content || '';
    return this.parseModelJson(text);
  }

  parseModelJson(raw) {
    const clean = String(raw)
      .replace(/```json/gi, '')
      .replace(/```/g, '')
      .trim();

    try {
      return JSON.parse(clean);
    } catch {
      throw new Error('AI returned non-JSON content.');
    }
  }
}

module.exports = {
  AIClient
};
