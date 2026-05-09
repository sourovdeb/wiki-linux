# wp-plugin

This folder contains the recreated WordPress plugin prototype.

## File

- wordpress-control.php: versioned REST bridge at /wp-json/sourov/v2

## Features implemented in scaffold

- Explicit publish endpoint and blocked direct publish in patch.
- Future-date validation for scheduling.
- Idempotency key support for mutating requests.
- Audit logging for state-changing operations.
- Allowed-category enforcement and category endpoint.
- Basic per-IP rate limiting.

## Install

1. Copy wordpress-control.php to wp-content/plugins/.
2. Activate plugin in WordPress admin.
3. Set optional plugin key in wp option wpc_plugin_key.
4. Test endpoint: /wp-json/sourov/v2/health
