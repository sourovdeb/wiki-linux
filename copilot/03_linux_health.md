---
title: Linux Health Check
slug: linuxcheck
description: Read-only sysinfo + one safe fix.
---

Call `linux_sysinfo` (no args). Then:

1. Summarise system state in ≤ 5 bullets.
2. Flag anything yellow/red (disk > 85 %, memory swap > 25 %, failed services).
3. Propose **one** safe command to address the worst issue. Show it in a fenced block. Do **not** run it — explain what it does and ask the user to confirm.

Focus area (optional, default "everything"): {{focus}}
