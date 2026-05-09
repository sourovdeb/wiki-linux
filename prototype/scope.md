# scope.md

Project scope, completion status, and roadmap for the recreated prototype.

## Project Goals

Provide safe, local-first AI-assisted control of WordPress from VS Code.

Priority order:

1. Safety: no accidental publish, reversible operations, auditable mutations.
2. Privacy: local Ollama default, no telemetry.
3. Speed: generate, review, queue, and post without leaving editor workflow.

## Rebuild Completed (v3.0.0-prototype)

### Foundation

- [x] Recreated prototype from minimal baseline.
- [x] Added full architecture docs and redesign source matrix.
- [x] Added API contract and site profile constraints.

### VS Code extension scaffold

- [x] Multi-tab webview: Generate, Posts, Queue, Logs, Settings.
- [x] Provider abstraction for Ollama, Claude, and DeepSeek.
- [x] OpenWebUI-first provider mode with model discovery.
- [x] Model discovery command for local Ollama.
- [x] Approval-aware generation flow.
- [x] Queue execution for draft-only bulk actions.
- [x] Bulk queue import from frontmatter markdown in articles folder.
- [x] Integrated WordPress AutoPilot queue execution (ping, dry run, live run).
- [x] Centralized service layer for WP and AI clients.

### User onboarding

- [x] Step-by-step quick start guide shown at beginning of Studio UI.
- [x] Step-by-step quick start documented at top of prototype and extension README files.

### WordPress plugin scaffold

- [x] Versioned API namespace at /wp-json/sourov/v2.
- [x] Standardized success and error envelopes.
- [x] Idempotency key handling for mutating endpoints.
- [x] Explicit publish endpoint with direct publish blocked in patch.
- [x] Future date validation on schedule endpoint.
- [x] Audit log option store with capped retention.
- [x] Per-IP basic rate limiting.
- [x] Allowed-category policy enforcement.

### Recreated supporting files

- [x] README.md
- [x] AGENTS.md
- [x] SITE_PROFILE.md
- [x] CHANGELOG.md
- [x] docs/API_CONTRACT.md
- [x] docs/REDESIGN_MATRIX.md

## Source Integration Checklist

- [x] sourovdeb/wordpress-control patterns integrated.
- [x] sourovdeb/smart-browser2 patterns integrated.
- [x] microsoft/api-guidelines principles integrated.
- [x] WordPress/WordPress route conventions integrated.
- [x] oswaldo/ollama-view layered architecture integrated.

## Current Sprint (v3.1)

### In Progress

- [x] Frontmatter bulk import from articles folder into queue.
- [x] Richer scheduling via integrated WordPress AutoPilot queue execution.
- [ ] Optional chat workflow in extension panel.

### Planned

- [ ] Attachment upload and featured image endpoint.
- [ ] Multi-site profile switching in extension settings.
- [ ] Calendar-style schedule board.

## Out Of Scope

- Theme and plugin file editing over REST.
- WooCommerce workflows.
- Comment moderation automation.

## Decisions Log

- 2026-05-08: Rebuild kept JavaScript for extension scaffold to lower maintenance cost.
- 2026-05-08: Idempotency required for all mutating plugin routes.
- 2026-05-08: Publish remains explicit action endpoint only.
- 2026-05-08: API keeps path-based versioning for readability and operational debugging.
- 2026-05-09: Prototype defaults to OpenWebUI for local-first automation while preserving direct Ollama/remote provider fallbacks.
- 2026-05-09: Reused existing wordpress-control AutoPilot package as the scheduler engine instead of duplicating scheduling logic in extension JS.