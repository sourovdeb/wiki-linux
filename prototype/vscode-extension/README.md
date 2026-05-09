# vscode-extension

This is the recreated VS Code extension scaffold for the redesigned prototype.

## Step-by-step quick start

1. Open this folder in VS Code.
2. Press F5 to launch Extension Development Host.
3. Run command: WP Control: Open Studio.
4. In Settings, configure WordPress URL and credentials.
5. In Queue, click Ping AutoPilot to validate automation environment.
6. Generate or import posts into queue.
7. Run AutoPilot Dry Run and review output in Logs.
8. Run AutoPilot Live Run only after dry run looks correct.

## Commands

- WP Control: Open Studio
- WP Control: Site Health Check
- WP Control: Import Articles To Queue
- WP Control: AutoPilot Ping
- WP Control: AutoPilot Dry Run
- WP Control: AutoPilot Live Run

## Design highlights

- Layered architecture inspired by ollama-view.
- WordPress operations isolated in services/wp-client.js.
- AI provider abstraction in services/ai-client.js.
- OpenWebUI-first local automation flow (with Ollama/Claude/DeepSeek fallback options).
- Approval-first workflow in the webview and extension orchestration.
- Queue execution for safe draft-only bulk creation.
- Frontmatter markdown article import into queue for batch draft automation.
- Native integration with existing wordpress-control AutoPilot pipeline (ping, dry run, live run).

## Run locally

1. Follow the step-by-step quick start above.
2. Use Logs tab after every AutoPilot run to verify pipeline output.

## Notes

- The extension scaffold targets the plugin contract defined in docs/API_CONTRACT.md.
- Mutating calls send Idempotency-Key automatically.
- Set `wpControl.articlesDir` only if you do not want the default `../articles` directory.
- By default the extension resolves AutoPilot under workspace/user/development/tools/wordpress-control/automation.
