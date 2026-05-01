---
title: "{{ title }}"
source: "{{ source_path }}"
ingested: "{{ ingested }}"
updated: "{{ updated }}"
tags: [{{ tags | join(', ') }}]
sources:
  - "{{ source_path }}"
---

# {{ title }}

> **Source:** `{{ source_path }}`
> **Ingested:** {{ ingested }}

## Summary

{{ explanation }}

## Contents

{{ contents }}

{% if links %}
## Related Pages

{% for link in links %}
- [[{{ link }}]]
{% endfor %}
{% endif %}
