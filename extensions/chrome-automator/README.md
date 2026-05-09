# Wiki Automator (Chrome Extension + Local Server)

`chrome-automator` automates:
- batch email drafting/sending (Gmail, ProtonMail)
- social posting (LinkedIn, Medium)
- session-cookie capture for Playwright
- activity recording + selector analysis

It is designed for local-first usage with:
- extension UI in Chromium
- FastAPI server at `http://127.0.0.1:7070`
- optional Ollama model integration for rewrite/personalization

## Upgrade Notes (May 2026)

This extension was upgraded to fix reliability issues:
- MV3 background status updates now use `chrome.alarms` (service-worker-safe).
- CSV parsing now supports quoted commas and header-based mapping.
- Email row-level `provider` override now works as documented.
- Dry run now performs real validation without launching Playwright/browser.
- Social posting also supports dry-run validation mode.
- AI model dropdown now auto-refreshes from installed local Ollama models.
- Live sidepanel events now receive `JOB_UPDATE`, `SESSION_CAPTURED`, `RECORDING_SAVED`.

## Install

1. Run installer:
   ```bash
   cd /home/sourov/Documents/wiki-linux/wiki-linux/extensions/chrome-automator
   bash install.sh
   ```
2. Load extension:
   - Open `chrome://extensions`
   - Enable Developer mode
   - Load unpacked:
     `/home/sourov/Documents/wiki-linux/wiki-linux/extensions/chrome-automator`
3. Start server:
   ```bash
   cd /home/sourov/Documents/wiki-linux/wiki-linux/extensions/chrome-automator/server
   .venv/bin/python server.py
   ```

## First Run Flow

1. Open target platform(s) and log in manually.
2. In extension popup, open `Sessions` tab and capture cookies per platform.
3. Load CSV / markdown content.
4. Keep `Dry run` enabled first.
5. Run job and confirm output/progress.
6. Disable `Dry run` only when ready for live automation.

## CSV Format

Header row is required. Supported columns:

- `recipient` (required)
- `subject`
- `body_file` (relative paths resolve under `templates/`)
- `body` (inline text body; fallback if `body_file` empty or missing)
- `attachments` (`;`-separated paths; relative paths resolve under `templates/`)
- `provider` (`gmail` or `proton`; overrides global provider)
- `delay` (seconds between rows; default `3`)

See example:
- `templates/email_batch_template.csv`

## Dry Test (No Browser Launch)

Dry run now validates input rows and file resolution without opening Playwright.

### API dry test

```bash
curl -s http://127.0.0.1:7070/api/jobs/run \
  -H 'Content-Type: application/json' \
  -d '{
    "type":"email_batch",
    "provider":"gmail",
    "ai_model":"none",
    "dry_run":true,
    "rows":[
      {"recipient":"test@example.com","subject":"Hello","body":"Dry-run body","provider":"gmail","delay":1}
    ]
  }'
```

Then poll:

```bash
curl -s http://127.0.0.1:7070/api/jobs/status/<job_id>
```

## Troubleshooting

- Server offline in popup:
  - Start server at `server/server.py`
  - Check `http://127.0.0.1:7070/api/health`
- No Ollama models in AI dropdown:
  - Ensure Ollama is running (`http://127.0.0.1:11434/api/tags`)
  - Keep `None` selected if local models are unavailable
- Session cookies old/red:
  - Re-capture sessions in `Sessions` tab
- Browser automation fails after site UI change:
  - Use `Learn` tab analysis and refresh selectors

## API Endpoints

- `GET /api/health`
- `GET /api/ollama/models`
- `POST /api/sessions/save`
- `POST /api/recordings/save`
- `POST /api/jobs/run`
- `GET /api/jobs/status/{job_id}`
- `POST /api/learn/analyse`
