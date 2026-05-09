# tests

These tests focus on safety-critical regressions.

## Targets

- No direct publish through patch endpoint.
- Scheduling rejects past timestamps and accepts future timestamps.

## Run

Set environment variables:

- WPC_BASE_URL
- WPC_USER
- WPC_APP_PASSWORD
- WPC_PLUGIN_KEY (optional)

Then run:

python -m unittest discover -s tests -p "test_*.py"
