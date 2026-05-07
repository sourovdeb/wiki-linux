# Ollama Local Assistant Extension

Local Chromium side-panel assistant connected to Ollama at http://127.0.0.1:11434.

## Features

- Side-panel chat workflow similar to assistant panels.
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

## Notes

- Extension is local-first and uses your local model endpoint.
- For best results use small fast models for browsing actions and larger models for long summaries.
