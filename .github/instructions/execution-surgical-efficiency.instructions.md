---
description: "Use when executing terminal work, automation, backups, system setup, or multi-step changes. Enforce think-before-execute planning, token-efficient communication, surgical script-first execution, and result verification/fine-tuning."
name: "Surgical Execution and Token Efficiency"
applyTo: "**"
---
# Surgical Execution and Token Efficiency

- Think before execute: decide the minimum safe sequence before running commands.
- Be token efficient: keep updates short and avoid repeating unchanged context.
- Prefer surgical automated scripts over ad-hoc command chains for operational tasks.
- Use one focused script per objective and keep side effects narrow.
- Run with strict mode for scripts:
```bash
#!/usr/bin/env bash
set -euo pipefail
```
- Validate outputs after each script run (exit code, key state checks, and expected artifacts).
- If results are partial, fine-tune and rerun only the minimal affected steps.
- Avoid speculative execution; confirm assumptions first with read-only checks.
- For destructive or system-level actions, add pre-checks and post-checks in the same script.
- Report only important outcomes: what changed, what was verified, and what remains.

## Preferred pattern

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1) Pre-checks
# 2) Targeted change
# 3) Verification
```

- Keep scripts idempotent where possible.
- When a one-liner is enough and safe, use it; otherwise script it.
