# Changelog

## 3.0.2-prototype - 2026-05-09

### Added

- Integrated existing wordpress-control AutoPilot pipeline into prototype extension queue flow.
- Queue tab controls for AutoPilot Ping, Dry Run, and Live Run.
- Extension settings for AutoPilot automation directory, Python path, and DeepSeek toggle.
- Command palette actions for AutoPilot ping and runs.

### Changed

- Added visible step-by-step quick start guide at the beginning of the Studio UI.
- Updated prototype and extension README files to start with user onboarding steps.

### Validation

- JS syntax checks passed for extension.js, webview.js, ai-client.js, article-importer.js, and autopilot-runner.js.
- PHP lint remains clean for plugin scaffold.

## 3.0.1-prototype - 2026-05-09

### Added

- OpenWebUI provider mode in extension settings and generation flow.
- OpenWebUI model discovery support.
- Articles folder importer that parses frontmatter markdown and pushes safe queue drafts.
- Command `WP Control: Import Articles To Queue` for direct automation workflow.

### Changed

- Default AI provider switched to OpenWebUI (local URL `http://127.0.0.1:8080`).
- Queue tab now supports one-click import from articles folder.

### Validation

- JS syntax checks passed for extension orchestration, webview, and services.
- PHP lint passed for plugin scaffold.
- Regression tests executed (integration tests skipped when `WPC_BASE_URL` is unset).

## 3.0.0-prototype - 2026-05-08

### Added

- Recreated prototype structure from near-empty baseline.
- Added redesigned extension scaffold under vscode-extension.
- Added redesigned WordPress plugin scaffold under wp-plugin.
- Added API contract and redesign source matrix documentation.
- Added site profile, sample articles, and safety regression tests.

### Changed

- Reframed architecture as layered system inspired by ollama-view patterns.
- Standardized API behavior against Microsoft guideline principles.
- Aligned plugin route patterns with WordPress core REST controller conventions.

### Safety

- Explicit publish endpoint model retained.
- Schedule date future validation included.
- Idempotency and audit logging included in plugin scaffold.
