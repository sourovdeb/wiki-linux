# WP Control Prototype (Redesigned)

This folder is a clean recreation of the WordPress control prototype for Sourov Deb.
It combines proven patterns from five reference repositories while keeping local-first privacy and safe publishing defaults.
It is implemented as a separate app surface in VS Code that uses OpenWebUI-first automation.

## Step-by-step guide (start here)

1. Place wp-plugin/wordpress-control.php in wp-content/plugins/ and activate it.
2. Open vscode-extension in VS Code and run Extension Development Host with F5.
3. Run command WP Control: Open Studio.
4. In Settings, configure WordPress URL, auth, and AI provider.
5. In Queue, click Ping AutoPilot to verify wordpress-control automation environment.
6. Add posts to queue (Generate or Import Articles Folder).
7. Run AutoPilot Dry Run and review Logs output.
8. Run AutoPilot Live Run when dry run output is valid.

## What this redesign integrates

| Source repository | Adopted ideas in this prototype |
| --- | --- |
| sourovdeb/wordpress-control | VS Code panel workflow, approval-first publishing, REST bridge model |
| sourovdeb/smart-browser2 | Hybrid execution thinking, task queue mindset, operational logging |
| microsoft/api-guidelines | Explicit contracts, idempotent mutation design, pagination and error shape |
| WordPress/WordPress | register_rest_route patterns, permission callbacks, sanitize and validate args |
| oswaldo/ollama-view | Layered extension architecture, local Ollama workflows, model discovery patterns |

## Core goals

1. Safety first: no accidental direct publish paths.
2. Privacy first: Ollama local by default.
3. Fast workflow: draft, schedule, review, publish from one panel.
4. Contract clarity: every endpoint documented with stable request and response patterns.
5. Separate-app operation: isolated workflow under `prototype/` with no coupling to wiki-linux runtime scripts.

## Folder layout

- AGENTS.md: agent execution rules and guardrails.
- scope.md: roadmap and status tracking.
- docs/API_CONTRACT.md: v2 endpoint and envelope design.
- docs/REDESIGN_MATRIX.md: source-to-feature traceability.
- vscode-extension/: extension scaffold in plain JavaScript.
- wp-plugin/: WordPress plugin scaffold with versioned REST API.
- tests/: lightweight regression checks for critical safety behavior.
- articles/: example frontmatter markdown content for bulk import.

## Safety defaults

- Draft is the default post status.
- Publish must use explicit publish endpoint.
- Schedule endpoint rejects past dates.
- Mutating requests support idempotency keys.
- Audit log is appended for every state change.

## Quick start notes

- Keep provider on OpenWebUI by default unless you need another provider.
- Keep AutoPilot on dry mode first for every new environment.
- Publish only through explicit review actions.
