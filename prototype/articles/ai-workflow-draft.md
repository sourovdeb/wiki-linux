---
title: AI Workflow Drafting in VS Code
status: draft
category: Automation
tags:
  - ai
  - workflow
  - vscode
seo_title: AI Workflow Drafting in VS Code
meta_desc: Build a safe AI-assisted drafting workflow for WordPress directly inside VS Code.
---

## Why this workflow matters

A single editor-centered workflow reduces context switching and prevents accidental publishing.

## Core process

1. Generate content in approval mode.
2. Review and edit draft content in panel.
3. Queue multiple drafts for safe creation.
4. Publish only through explicit publish endpoint.

## Recommended controls

- Keep default status as draft.
- Require idempotency key on mutating requests.
- Validate schedule timestamps server-side.
