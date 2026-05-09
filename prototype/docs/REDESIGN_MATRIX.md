# Redesign Matrix

This matrix records how each required upstream repository influenced this prototype.

## Mandatory source usage mapping

### 1) sourovdeb/wordpress-control

- Multi-tab panel workflow for chat, generate, posts, logs, settings.
- Approval mode behavior before content mutation actions.
- Dedicated WordPress request client layer.
- Scope and AGENTS style for explicit safety rules.

### 2) sourovdeb/smart-browser2

- Hybrid execution philosophy: API-first, browser automation only if needed.
- Queue and operational log mindset for transparent automation.
- Daily-operation orientation and practical task ergonomics.
- Security reminder pattern: never hardcode secrets.

### 3) microsoft/api-guidelines

- Idempotent mutation behavior using repeatable-request semantics.
- Strong, machine-parseable error envelope.
- Standard status code usage including 429 and 503 guidance.
- Pagination contract with stable ordering assumptions.

### 4) WordPress/WordPress

- register_rest_route shape with namespace and rest base.
- permission_callback on each route.
- Endpoint arg schema with sanitize and validate callbacks.
- WP_Error centered validation and permission behavior.

### 5) oswaldo/ollama-view

- Layered extension architecture (UI, orchestration, service, contract).
- Local Ollama API usage patterns: list tags, list running, generate.
- Runtime model discovery and user-facing setup support.
- Persistence-oriented extension state design.

## Resulting architecture

1. VS Code UI and orchestration in plain JavaScript.
2. Service layer for AI provider and WordPress client abstraction.
3. WordPress plugin with versioned REST endpoints and strict validations.
4. Testable contracts via documented request and response envelopes.
