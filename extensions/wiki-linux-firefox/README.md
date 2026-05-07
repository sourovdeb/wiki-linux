# Wiki-Linux Firefox Assistant

Local Ollama-powered Firefox extension with wiki_ingestor integration for webpage summarization, searching, form-filling, and wiki archiving.

## Features

### Core Capabilities
- **Sidebar Panel**: Side-by-side assistant interface while browsing
- **System Popup**: Real-time status of Ollama, Open WebUI, and wiki_ingestor
- **Page Summarization**: Generate concise summaries of webpage content
- **Smart Search**: Find specific information on the current page
- **Link Crawling**: Browse and analyze all visible links
- **PDF Detection**: Identify and list all PDF links on a page
- **Form Analysis**: Detect forms and their fields
- **Wiki Integration**: Save webpages as markdown with YAML frontmatter for wiki_ingestor processing

### System Integration
- Detects Ollama running on `127.0.0.1:11434`
- Connects to Open WebUI on `127.0.0.1:8080`
- Integrates with wiki_ingestor for automated page conversion
- Uses local models for fast, private processing
- Supports multiple Ollama models simultaneously

## Installation

### Prerequisites
- Firefox 109+ (supports Manifest V3)
- Ollama running: `ollama serve` on port 11434
- Optional: Open WebUI service for UI access
- Optional: wiki_ingestor installed for wiki processing

### Load Extension in Firefox

#### Method 1: Manual Load (Development)
1. Open Firefox
2. Navigate to `about:debugging`
3. Click "This Firefox" (left sidebar)
4. Click "Load Temporary Add-on"
5. Navigate to this folder and select `manifest.json`
6. Extension will be installed temporarily (active until Firefox restart)

#### Method 2: Permanent Installation (Recommended)
1. Package the extension:
   ```bash
   bash /path/to/WIKI-TOOLS/handoff/16-package-ollama-extension.sh
   ```
2. Export to ZIP:
   ```bash
   cd extensions/wiki-linux-firefox
   zip -r wiki-linux-firefox.xpi manifest.json *.js *.html *.css icons/
   ```
3. Open Firefox Settings → Extensions
4. Drag and drop `wiki-linux-firefox.xpi` to install
5. Allow permissions when prompted

#### Method 3: Sign and Submit to Firefox Add-ons (Optional)
For official distribution, follow [Firefox Developer Hub](https://addons.mozilla.org/en-US/developers/) guidelines.

## Usage

### Sidebar Panel

Click the extension icon in the toolbar to open the sidebar panel:

```
[Model Selector dropdown]
[Action Buttons Grid]:
  📝 Summarize  | 🔍 Search
  🕷️ Crawl    | 📄 Find PDFs
  📋 Forms    | 💾 Save to Wiki
[Composer: Input + Send]
[Response Area with Results]
```

### Quick Actions

#### 📝 Summarize
Generates a concise summary of the current page using Ollama.
- Shows top key points
- Uses selected model (default: llama3.2:3b)
- Maximum 3-5 bullet points

#### 🔍 Search
Find specific information on the current page.
- Prompts for search query
- Returns relevant excerpts
- Highlights matching context

#### 🕷️ Crawl Links
Display all clickable links on the current page.
- Shows link text and URL
- Click to open in new tab
- Limited to 20 links per page

#### 📄 Find PDFs
Detect all PDF downloads available on the page.
- Extracts PDF link metadata
- Shows file names and URLs
- Direct download links

#### 📋 Forms
Analyze form fields on the current page.
- Lists all available forms
- Shows field names and types
- Prepare for automated form-filling

#### 💾 Save to Wiki
Convert the current page to wiki format with YAML frontmatter.

**Generated Markdown Format:**
```markdown
---
title: "Page Title"
url: "https://example.com/page"
date: "2026-05-07T12:34:56.789Z"
source: "firefox-extension"
tags: [web-capture, ollama]
---

# Page Content (HTML to Markdown)

- Converted sections
- Preserved links and images
- Clean formatting for wiki
```

**Processing:**
1. Click "💾 Save to Wiki"
2. Page converts to markdown format
3. Shows filename and conversion details
4. Save the markdown file to:
   ```
   ~/wiki/converted/    (if using wiki_ingestor watch)
   or
   [Your wiki_ingestor watch folder]
   ```
5. wiki_ingestor automatically picks up the file on next cycle

### System Popup

Click the extension icon to view a popup with:

**Status Cards:**
- 🤖 **Ollama**: Shows connection status (127.0.0.1:11434)
- 🌐 **Open WebUI**: Shows web UI status (127.0.0.1:8080)
- 📚 **Wiki Ingestor**: Shows installation status

**Quick Actions:**
- 📖 **Open Sidebar**: Launch the full assistant panel
- 🤖 **Open Ollama**: Direct link to Ollama service
- 🌐 **Open Web UI**: Direct link to Open WebUI

**Available Models:**
- Lists all Ollama models currently available
- Auto-updates every 5 seconds

## Configuration

### Model Selection
Select the active model from the sidebar dropdown:

Default Models:
- `llama3.2:3b` (Fast, 3B parameters) — Good for summarization
- `qwen2.5-coder:3b` (Code-optimized) — Better for technical content

Add custom models:
1. Run `ollama pull [model-name]`
2. Sidebar will auto-detect and show in dropdown
3. Select to use for queries

### Ollama Endpoint (Advanced)
To use a non-standard Ollama endpoint, edit `background.js`:
```javascript
const OLLAMA_API = 'http://127.0.0.1:11434/api';  // Change this line
```

### wiki_ingestor Integration

**Automatic Processing:**
1. Save pages from Firefox
2. Extension creates markdown in `~/wiki/converted/`
3. Run wiki_ingestor watcher:
   ```bash
   python -m wiki_ingestor watch
   ```
4. Files auto-convert with YAML metadata

**Manual Processing:**
1. Save page from Firefox
2. Copy markdown to your wiki folder
3. Run wiki_ingestor batch:
   ```bash
   python -m wiki_ingestor batch
   ```

**Configure Watch Folders:**
Edit `~/.config/wiki-linux/config.json`:
```json
{
  "wiki": {
    "root": "~/wiki",
    "monitor": {
      "watch_dirs": [
        "~/wiki/converted",
        "~/wiki/inbox",
        "~/Downloads"
      ]
    }
  }
}
```

## Permissions Explained

- **activeTab**: Access current webpage content for analysis
- **scripting**: Inject content scripts for page interaction
- **storage**: Store model preferences and settings
- **tabs**: Manage tabs for link/PDF opening
- **webRequest**: Monitor network requests for system status
- **All URLs**: Access any webpage for analysis and conversion

## Troubleshooting

### "Ollama is offline" error
**Solution:**
```bash
# Start Ollama service
ollama serve

# Or if using systemd:
systemctl --user start wiki-ollama.service
```

### "No page loaded" message
**Solution:**
- Ensure you're on a regular webpage (not special pages like about:blank)
- Refresh the page and wait 2-3 seconds
- Try again

### Models not appearing
**Solution:**
```bash
# Pull a model first
ollama pull llama3.2:3b

# Verify it's available
curl http://127.0.0.1:11434/api/tags
```

### PDF detection not working
**Solution:**
- Ensure page has PDFs linked as standard `<a href="file.pdf">` tags
- Some PDFs embedded via JavaScript won't be detected
- Check browser console for errors

### Wiki conversion fails
**Solution:**
1. Check wiki_ingestor is installed:
   ```bash
   python -m wiki_ingestor --version
   ```
2. Verify watch folder exists:
   ```bash
   ls ~/wiki/converted/
   ```
3. Check wiki_ingestor logs:
   ```bash
   python -m wiki_ingestor status
   ```

## Security & Privacy

✅ **Local-First**: All processing happens on your local machine
✅ **No Tracking**: Extension doesn't send data to external servers
✅ **Private Models**: Uses your local Ollama models
✅ **Source Available**: Full source code in this directory
⚠️ **Permission Note**: Needs access to all URLs for page analysis; no data is logged

## Development

### File Structure
```
wiki-linux-firefox/
├── manifest.json          # Firefox extension manifest
├── background.js          # Service worker with Ollama API
├── content.js            # Page analysis content script
├── sidebar.html/js/css   # Main assistant panel
├── popup.html/js/css     # System status popup
├── icons/                # Extension icons
└── README.md             # This file
```

### Testing Changes

1. Edit any file
2. Go to `about:debugging`
3. Click "Reload" on "Wiki-Linux Firefox"
4. Changes apply immediately

### Building for Distribution

```bash
# Create a signed package for Firefox Add-ons
cd extensions/wiki-linux-firefox

# Install web-ext CLI
npm install --global web-ext

# Build and sign
web-ext build --overwrite-dest

# Creates: ../web-ext-artifacts/wiki-linux-firefox-*.zip
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Alt+Shift+A | Toggle sidebar panel (configurable) |
| Enter (in composer) | Send prompt to Ollama |
| Ctrl+F (in sidebar) | Browser find-in-page |

## Integration with wiki_ingestor

The Firefox extension directly supports wiki_ingestor's markdown conversion format:

1. **YAML Frontmatter**: Automatically generated with metadata
2. **Markdown Conversion**: HTML to Markdown with link/image preservation
3. **Tag System**: Pages tagged with `web-capture` and `ollama`
4. **Watch Folder**: Saves to `~/wiki/converted/` by default
5. **Auto-Processing**: wiki_ingestor picks up new files automatically

Example workflow:
```bash
# Terminal 1: Start wiki_ingestor watcher
cd /path/to/wiki-linux
python -m wiki_ingestor watch

# Browser: Use Firefox extension
# 1. Browse to webpage
# 2. Click "💾 Save to Wiki"
# 3. Markdown file saved to ~/wiki/converted/

# Terminal 1: Will auto-process the file
# - Converts to wiki format
# - Applies YAML metadata
# - Stores in wiki structure
```

## Performance Tips

- Use **llama3.2:3b** for fast operations (summarize, search)
- Use **qwen2.5-coder:3b** for code-heavy pages
- Summarize pages with **< 3000 characters** for best results
- Close sidebar when not in use to save memory
- Monitor Ollama with `ollama ps` during heavy use

## Updates & Support

- Check GitHub: https://github.com/sourovdeb/wiki-linux
- Report issues: Include Firefox version, Ollama status, error messages
- Contribute: Submit PRs with improvements

## License

Same as wiki-linux repository

---

**Created**: May 2026  
**Version**: 1.0.0  
**Compatible**: Firefox 109+, Ollama, wiki_ingestor
