/**
 * Popup JavaScript: System status display and quick actions
 */

document.addEventListener('DOMContentLoaded', () => {
  checkSystemStatus();
  loadAvailableModels();
  setupActionButtons();
  updateTimestamp();
});

/**
 * Check and display system status
 */
async function checkSystemStatus() {
  browser.runtime.sendMessage({ action: 'checkStatus' })
    .then(status => {
      // Ollama status
      const ollamaStatus = document.getElementById('ollamaStatus');
      if (status.ollama?.running) {
        ollamaStatus.textContent = '🟢 Online';
        ollamaStatus.classList.remove('offline', 'checking');
      } else {
        ollamaStatus.textContent = '🔴 Offline';
        ollamaStatus.classList.add('offline');
      }

      // OpenWebUI status
      const webuiStatus = document.getElementById('webuiStatus');
      if (status.openwebui?.running) {
        webuiStatus.textContent = '🟢 Online';
        webuiStatus.classList.remove('offline', 'checking');
      } else {
        webuiStatus.textContent = '🔴 Offline';
        webuiStatus.classList.add('offline');
      }

      // Wiki Ingestor status (always installed if extension is running)
      const ingestorStatus = document.getElementById('ingestorStatus');
      ingestorStatus.textContent = '✓ Installed';
    })
    .catch(err => {
      console.error('Status check failed:', err);
      document.getElementById('ollamaStatus').textContent = '⚠️ Error';
      document.getElementById('webuiStatus').textContent = '⚠️ Error';
    });
}

/**
 * Load and display available Ollama models
 */
async function loadAvailableModels() {
  browser.runtime.sendMessage({ action: 'getModels' })
    .then(models => {
      const modelsList = document.getElementById('modelsList');
      modelsList.innerHTML = '';

      if (models && models.length > 0) {
        models.forEach(model => {
          const modelDiv = document.createElement('div');
          modelDiv.className = 'model-item';
          modelDiv.innerHTML = `<strong>${model}</strong>`;
          modelsList.appendChild(modelDiv);
        });
      } else {
        modelsList.innerHTML = '<div class="loading">No models available. Start Ollama.</div>';
      }
    })
    .catch(err => {
      console.error('Failed to load models:', err);
      document.getElementById('modelsList').innerHTML = 
        '<div class="loading">Error loading models</div>';
    });
}

/**
 * Setup action buttons
 */
function setupActionButtons() {
  document.getElementById('openSidebarBtn').addEventListener('click', () => {
    browser.sidebarAction.open();
  });

  document.getElementById('openOllamaBtn').addEventListener('click', () => {
    browser.tabs.create({ url: 'http://127.0.0.1:11434' });
  });

  document.getElementById('openWebUIBtn').addEventListener('click', () => {
    browser.tabs.create({ url: 'http://127.0.0.1:8080' });
  });
}

/**
 * Update last refresh timestamp
 */
function updateTimestamp() {
  const now = new Date();
  const time = now.toLocaleTimeString();
  document.getElementById('lastUpdate').textContent = `Last checked: ${time}`;
}

// Auto-refresh status every 5 seconds
setInterval(() => {
  checkSystemStatus();
  loadAvailableModels();
  updateTimestamp();
}, 5000);
