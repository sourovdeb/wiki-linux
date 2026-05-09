# Ollama Local Assistant Extension

Local Chromium side-panel assistant connected to Ollama at http://127.0.0.1:11434.

## Features

- Side-panel chat workflow similar to assistant panels.
- Installed-model dropdown from Ollama (`/api/tags`) with auto refresh.
- Summarize current website content.
- Search specific information from visible page text.
- Crawl visible links and prioritize next links.
- Detect and download PDF links.
- Form-fill helper: generates JSON field mapping and applies values.

## Manual Load (Unpacked)

1. Open Chromium.
2. Go to chrome://extensions.
3. Enable Developer mode.
4. Click Load unpacked.
5. Select this folder:
   /home/sourov/Documents/wiki-linux/wiki-linux/extensions/ollama-local-assistant

## Manual Upload Package (ZIP)

Build package:

bash /home/sourov/Documents/wiki-linux/wiki-linux/WIKI-TOOLS/handoff/16-package-ollama-extension.sh

Latest output zip is created in:

/home/sourov/Documents/wiki-linux/wiki-linux/_meta/reports/extension-build/

## Runtime Requirements

- Ollama API running at 127.0.0.1:11434
- Chromium with extension side panel support
- Access to current webpage content via content script

### Fixing `403` from Ollama (browser extensions)

Ollama blocks unknown web origins by default. To allow browser extensions, set `OLLAMA_ORIGINS` to include your extension origin pattern, then restart Ollama. Official guidance: set it to include `chrome-extension://*` (and optionally `moz-extension://*`, `safari-web-extension://*`).

If you use the wiki-linux service (`wiki-ollama.service`), re-run:

```bash
bash /home/sourov/Documents/wiki-linux/wiki-linux/WIKI-TOOLS/handoff/09-ai-stack-configure.sh
```

### Fixing `Could not establish connection. Receiving end does not exist.`

This means the side panel tried to talk to a page where `content.js` is unavailable.

Common cases:
- You are on a restricted tab (`chrome://*`, extension pages, Chrome Web Store, etc.).
- The extension was reloaded but the page was not refreshed yet.

Quick fix:
1. Open a normal `http://` or `https://` page.
2. Reload that tab once.
3. Reload the extension in `chrome://extensions`.

### Fixing `Ollama API failed: 404`

Official Ollama API docs mark `404` as not found (most commonly model missing). The API returns JSON in the form `{ "error": "..." }`.

Common causes:
- Model in the panel is not installed locally.
- A tool/integration is calling a wrong endpoint path.

Quick checks:
1. Confirm models: `curl http://127.0.0.1:11434/api/tags`
2. Test chat endpoint:
   `curl http://127.0.0.1:11434/api/chat -d '{"model":"llama3.2:3b","messages":[{"role":"user","content":"hi"}],"stream":false}'`

The panel now auto-switches to an installed local model if the selected one is missing, and can fall back to `/api/generate` if `/api/chat` is unavailable.

## Notes

- Extension is local-first and uses your local model endpoint.
- For best results use small fast models for browsing actions and larger models for long summaries.
