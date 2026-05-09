# AGENTS.md

Context and operating rules for agents working in this recreated prototype.

## 1. Project Overview

- Name: wordpress-control-prototype
- Version: 3.0.0-prototype
- Target: safe local-first WordPress control from VS Code
- Primary site profile: sourovdeb.com

## 2. Why this rewrite exists

This prototype was recreated from a near-empty baseline to unify five sources:

1. sourovdeb/wordpress-control
2. sourovdeb/smart-browser2
3. microsoft/api-guidelines
4. WordPress/WordPress
5. oswaldo/ollama-view

Use docs/REDESIGN_MATRIX.md for the exact mapping.

## 3. Architecture

Use layered boundaries. Do not bypass services.

1. UI layer: webview.js
2. Orchestration: extension.js
3. Services: wp-client.js, ai-client.js, validator.js, log-store.js
4. WordPress bridge: wp-plugin/wordpress-control.php

## 4. Mandatory Safety Rules

1. Never publish through generic update endpoint.
2. Use explicit /posts/{id}/publish only.
3. Validate schedule date future server-side.
4. Use idempotency key for all POST/PATCH/DELETE.
5. Keep approval mode on unless user explicitly disables.
6. Do not create categories outside SITE_PROFILE.md allow list.

## 5. API Rules

- Base path: /wp-json/sourov/v2
- Use noun resources and action sub-resources.
- Return normalized error envelope on failures.
- Use standard HTTP status semantics.
- Keep pagination stable: page and per_page.

## 6. WordPress Route Design Rules

Follow WordPress core patterns:

1. Register routes under rest_api_init.
2. Always provide permission callback.
3. Use sanitize and validate callbacks where possible.
4. Return WP_REST_Response for successful responses.
5. Use WP_Error only where WP internals require it.

## 7. Extension Design Rules

Follow ollama-view style service separation:

1. Keep panel logic in webview.js.
2. Keep network calls in service files.
3. Keep queue and logs visible to user.
4. Keep provider abstraction behind ai-client.js.
5. Prefer local Ollama by default.

## 8. Documentation and Change Discipline

When changing behavior:

1. Update scope.md.
2. Update CHANGELOG.md.
3. Update docs/API_CONTRACT.md for API changes.
4. Add or update tests for safety regressions.

## 9. Known Risk Areas

1. Accidental publish paths.
2. Scheduling with incorrect timezone or past date.
3. Missing idempotency keys causing duplicate actions.
4. Category drift outside defined profile.

## 10. Non-goals for this prototype

1. Full production-grade migration framework.
2. Complete UI parity with all historical tools.
3. Theme editing or general server file management.