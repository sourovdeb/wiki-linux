# SITE_PROFILE.md

This profile is consumed by the extension and plugin to constrain automation behavior.

## Site

- canonical_url: https://sourovdeb.com
- timezone: Asia/Dhaka
- default_language: en

## Publishing policy

- default_status: draft
- approval_mode: required
- minimum_content_chars_for_publish: 100
- require_explicit_publish_endpoint: true

## Allowed categories

- AI
- Automation
- English Learning
- Productivity
- Tech Notes

## Required SEO fields

- seo_title
- meta_desc

## Meta constraints

- seo_title_max: 60
- meta_desc_max: 160

## Safety constraints

- never create unknown categories
- never schedule in the past
- never publish from generic update endpoint
- all mutating requests must include idempotency key
