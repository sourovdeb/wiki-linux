/**
 * Sidebar JavaScript: Main assistant interface
 */

let currentPageSnapshot = null;
let currentModel = 'llama3.2:3b';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  checkSystemStatus();
  loadModel();
  loadPageSnapshot();
});

/**
 * Setup all event listeners
 */
function setupEventListeners() {
  document.getElementById('modelSelect').addEventListener('change', (e) => {
    currentModel = e.target.value;
    browser.storage.local.set({ activeModel: currentModel });
  });

  document.getElementById('summarizeBtn').addEventListener('click', handleSummarize);
  document.getElementById('searchBtn').addEventListener('click', handleSearch);
  document.getElementById('crawlBtn').addEventListener('click', handleCrawlLinks);
  document.getElementById('pdfBtn').addEventListener('click', handleFindPDFs);
  document.getElementById('formBtn').addEventListener('click', handleForms);
  document.getElementById('saveWikiBtn').addEventListener('click', handleSaveToWiki);
  document.getElementById('sendBtn').addEventListener('click', handleSendPrompt);

  document.getElementById('promptInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSendPrompt();
  });
}

/**
 * Display response in response area
 */
function displayResponse(content, type = 'text') {
  const responseArea = document.getElementById('responseArea');
  responseArea.innerHTML = '';

  if (type === 'text') {
    const div = document.createElement('div');
    div.className = 'response-text';
    div.textContent = content;
    responseArea.appendChild(div);
  } else if (type === 'list') {
    const ul = document.createElement('ul');
    ul.className = 'response-list';
    content.forEach(item => {
      const li = document.createElement('li');
      if (typeof item === 'object' && item.href) {
        const a = document.createElement('a');
        a.href = item.href;
        a.textContent = item.text || item.href;
        a.target = '_blank';
        li.appendChild(a);
      } else {
        li.textContent = item;
      }
      ul.appendChild(li);
    });
    responseArea.appendChild(ul);
  }
}

/**
 * Load current page snapshot
 */
async function loadPageSnapshot() {
  const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
  
  browser.tabs.sendMessage(tab.id, { action: 'getPageSnapshot' })
    .then(snapshot => {
      currentPageSnapshot = snapshot;
      console.log('Page snapshot loaded:', snapshot.title);
    })
    .catch(err => console.log('Could not get page snapshot:', err));
}

/**
 * Summarize current page
 */
async function handleSummarize() {
  if (!currentPageSnapshot) {
    displayResponse('No page loaded. Please refresh the page and try again.', 'text');
    return;
  }

  displayResponse('Summarizing page...', 'text');

  const content = currentPageSnapshot.text.substring(0, 3000);
  
  browser.runtime.sendMessage({
    action: 'summarize',
    content: content,
    model: currentModel
  }).then(response => {
    displayResponse(response, 'text');
  }).catch(err => {
    displayResponse(`Error: ${err.message}`, 'text');
  });
}

/**
 * Search page for specific information
 */
async function handleSearch() {
  if (!currentPageSnapshot) {
    displayResponse('No page loaded.', 'text');
    return;
  }

  const query = prompt('What would you like to find on this page?');
  if (!query) return;

  displayResponse(`Searching for: "${query}"...`, 'text');

  const content = currentPageSnapshot.text.substring(0, 3000);

  browser.runtime.sendMessage({
    action: 'search',
    content: content,
    query: query,
    model: currentModel
  }).then(response => {
    displayResponse(response, 'text');
  }).catch(err => {
    displayResponse(`Error: ${err.message}`, 'text');
  });
}

/**
 * Crawl visible links
 */
async function handleCrawlLinks() {
  if (!currentPageSnapshot || !currentPageSnapshot.links.length) {
    displayResponse('No links found on this page.', 'text');
    return;
  }

  const links = currentPageSnapshot.links.slice(0, 20);
  displayResponse(links, 'list');
}

/**
 * Find PDFs on page
 */
async function handleFindPDFs() {
  if (!currentPageSnapshot) {
    displayResponse('No page loaded.', 'text');
    return;
  }

  const pdfs = currentPageSnapshot.pdfs;
  if (!pdfs.length) {
    displayResponse('No PDFs found on this page.', 'text');
  } else {
    displayResponse(pdfs, 'list');
  }
}

/**
 * Show forms on page
 */
async function handleForms() {
  if (!currentPageSnapshot || !currentPageSnapshot.forms.length) {
    displayResponse('No forms found on this page.', 'text');
    return;
  }

  const formsText = currentPageSnapshot.forms.map((form, i) => {
    const fields = Object.keys(form).join(', ');
    return `Form ${i + 1}: ${fields}`;
  }).join('\n\n');

  displayResponse(formsText, 'text');
}

/**
 * Save page to wiki_ingestor
 */
async function handleSaveToWiki() {
  if (!currentPageSnapshot) {
    displayResponse('No page loaded.', 'text');
    return;
  }

  displayResponse('Converting to wiki format...', 'text');

  browser.runtime.sendMessage({
    action: 'saveToWiki',
    title: currentPageSnapshot.title,
    url: currentPageSnapshot.url,
    content: currentPageSnapshot.text.substring(0, 5000)
  }).then(response => {
    if (response.success) {
      const msg = `✅ Page converted successfully!\n\nFilename: ${response.filename}\n\n${response.message}\n\nYou can now:\n1. Copy the markdown to your wiki folder\n2. Run wiki_ingestor watch to auto-monitor\n3. Or place in ~/wiki/converted/ for processing`;
      displayResponse(msg, 'text');
    } else {
      displayResponse(`Error: ${response.error}`, 'text');
    }
  }).catch(err => {
    displayResponse(`Error: ${err.message}`, 'text');
  });
}

/**
 * Send custom prompt to Ollama
 */
async function handleSendPrompt() {
  const prompt = document.getElementById('promptInput').value.trim();
  if (!prompt) return;

  displayResponse(`Asking Ollama (${currentModel})...`, 'text');
  document.getElementById('promptInput').value = '';

  browser.runtime.sendMessage({
    action: 'queryOllama',
    prompt: prompt,
    model: currentModel
  }).then(response => {
    displayResponse(response.response || response, 'text');
  }).catch(err => {
    displayResponse(`Error: ${err.message}`, 'text');
  });
}

/**
 * Check system status and update indicator
 */
async function checkSystemStatus() {
  browser.runtime.sendMessage({ action: 'checkStatus' })
    .then(status => {
      const indicator = document.getElementById('systemStatus');
      const isOnline = status.ollama?.running && status.openwebui?.running;
      
      if (isOnline) {
        indicator.classList.remove('offline');
        indicator.title = '✅ Ollama & OpenWebUI online';
      } else {
        indicator.classList.add('offline');
        indicator.title = '❌ Services offline';
      }
    })
    .catch(err => console.log('Status check failed:', err));
}

/**
 * Load saved model preference
 */
async function loadModel() {
  browser.storage.local.get(['activeModel'], (result) => {
    if (result.activeModel) {
      currentModel = result.activeModel;
      document.getElementById('modelSelect').value = currentModel;
    }
  });
}

// Refresh page snapshot every 5 seconds to keep it updated
setInterval(loadPageSnapshot, 5000);

// Check system status periodically
setInterval(checkSystemStatus, 30000);
