/**
 * Firefox Background Service Worker for Wiki-Linux Assistant
 * Manages Ollama API calls, wiki_ingestor integration, and system status
 */

const OLLAMA_API = 'http://127.0.0.1:11434/api';
const WIKI_INGESTOR_PATH = '/home/sourov/Documents/wiki-linux/wiki-linux';
const WIKI_CONVERTED_PATH = process.env.HOME + '/wiki/converted';

// Initialize extension storage
browser.storage.local.get(['models', 'systemStatus'], (result) => {
  if (!result.models) {
    browser.storage.local.set({
      models: ['llama3.2:3b', 'qwen2.5-coder:3b'],
      activeModel: 'llama3.2:3b',
      systemStatus: {}
    });
  }
});

/**
 * Query Ollama local endpoint
 */
async function queryOllama(prompt, model = 'llama3.2:3b') {
  try {
    const response = await fetch(`${OLLAMA_API}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: model,
        prompt: prompt,
        stream: false,
        temperature: 0.7
      })
    });
    
    if (!response.ok) throw new Error(`Ollama error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Ollama query failed:', error);
    throw error;
  }
}

/**
 * Get available models from Ollama
 */
async function getAvailableModels() {
  try {
    const response = await fetch(`${OLLAMA_API}/tags`);
    if (!response.ok) throw new Error(`Failed to fetch models: ${response.status}`);
    const data = await response.json();
    return data.models ? data.models.map(m => m.name) : [];
  } catch (error) {
    console.error('Failed to get models:', error);
    return [];
  }
}

/**
 * Generate page summary
 */
async function summarizePage(pageContent, model) {
  const prompt = `Summarize the following webpage content in 3-5 bullet points. Be concise and highlight key information:\n\n${pageContent}`;
  try {
    const result = await queryOllama(prompt, model);
    return result.response;
  } catch (error) {
    return `Error: ${error.message}`;
  }
}

/**
 * Search content for specific information
 */
async function searchPageContent(content, query, model) {
  const prompt = `Search the following content and extract information related to: "${query}"\n\nContent:\n${content}\n\nReturn relevant excerpts or answer directly.`;
  try {
    const result = await queryOllama(prompt, model);
    return result.response;
  } catch (error) {
    return `Error: ${error.message}`;
  }
}

/**
 * Convert HTML to Markdown with YAML frontmatter (wiki_ingestor compatible)
 */
function convertToMarkdown(pageTitle, pageUrl, pageContent) {
  const date = new Date().toISOString();
  const slug = pageTitle.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '');
  
  // Create YAML frontmatter matching wiki_ingestor format
  const frontmatter = `---
title: "${pageTitle}"
url: "${pageUrl}"
date: "${date}"
source: "firefox-extension"
tags: [web-capture, ollama]
---

`;

  // Basic HTML to Markdown conversion
  let markdown = pageContent
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n')
    .replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n')
    .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n')
    .replace(/<h4[^>]*>(.*?)<\/h4>/gi, '#### $1\n\n')
    .replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n')
    .replace(/<a[^>]*href=["\'](.*?)["\']*>(.*?)<\/a>/gi, '[$2]($1)')
    .replace(/<img[^>]*src=["\'](.*?)["\']*[^>]*>/gi, '![$1]($1)')
    .replace(/<[^>]+>/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  return frontmatter + markdown;
}

/**
 * Save page to wiki_ingestor watch folder
 */
async function savePageToWiki(pageTitle, pageUrl, pageContent) {
  const markdown = convertToMarkdown(pageTitle, pageUrl, pageContent);
  
  return {
    success: true,
    message: `Page converted to markdown (${markdown.length} chars). Ready for wiki_ingestor processing.`,
    markdown: markdown,
    filename: `${pageTitle.replace(/\s+/g, '-')}-${Date.now()}.md`
  };
}

/**
 * Check system status (Ollama, OpenWebUI, wiki_ingestor)
 */
async function checkSystemStatus() {
  const status = {
    ollama: { running: false, port: 11434 },
    openwebui: { running: false, port: 8080 },
    wiklingestor: { installed: false, path: WIKI_INGESTOR_PATH }
  };

  // Check Ollama
  try {
    const ollamaResp = await fetch(`http://127.0.0.1:11434/api/tags`);
    status.ollama.running = ollamaResp.ok;
  } catch (e) {
    status.ollama.running = false;
  }

  // Check Open WebUI
  try {
    const uiResp = await fetch(`http://127.0.0.1:8080/`, { method: 'HEAD' });
    status.openwebui.running = uiResp.ok || uiResp.status === 404;
  } catch (e) {
    status.openwebui.running = false;
  }

  // Store status
  browser.storage.local.set({ systemStatus: status });
  return status;
}

/**
 * Message handler from popup and sidebar
 */
browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received:', request.action);

  switch (request.action) {
    case 'checkStatus':
      checkSystemStatus().then(sendResponse);
      return true;

    case 'getModels':
      getAvailableModels().then(sendResponse);
      return true;

    case 'summarize':
      summarizePage(request.content, request.model).then(sendResponse);
      return true;

    case 'search':
      searchPageContent(request.content, request.query, request.model).then(sendResponse);
      return true;

    case 'saveToWiki':
      savePageToWiki(request.title, request.url, request.content).then(sendResponse);
      return true;

    case 'queryOllama':
      queryOllama(request.prompt, request.model).then(sendResponse);
      return true;

    default:
      sendResponse({ error: 'Unknown action' });
  }
});
