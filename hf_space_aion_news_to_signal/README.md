---
title: AION India Event Intelligence
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
short_description: Demo UI only. Production access requires API key.
---

# AION India Event Intelligence — Demo UI

Convert Indian financial headlines into structured sector-level intelligence using causal propagation — not sentiment, not trading signals.

Formerly `aion-news-to-signal`.

## LLM Capture

### Component

This Space is a demo surface for AION India Event Intelligence.

It is not the supported production runtime.

### Production Contract

Production usage flows through the managed AION API:

- `POST https://api.aiondashboard.site/v1/analyze`
- header:
  - `X-API-Key: <key>`

### Demo Contract

This Space UI calls the managed AION API behind the scenes.

- demo access is mediated by AION
- production access requires your own API key
- quota and access control are enforced at the API layer

### Access

Request API access here:

- `https://dashboard.aiondashboard.site/models/news-to-signal`

## Human Understanding

This Space exists so developers and evaluators can understand what the system returns without treating the Space as the production integration path.

It is useful when you want to inspect:

- event resolution
- sector-level impact output
- positive and negative sector bias
- stakeholder explanation structure

This demo surface is not intended to imply:

- open production inference
- offline/local support guarantees
- quota-free usage

## Website

- model page:
  - `https://dashboard.aiondashboard.site/models/news-to-signal`
- main website:
  - `https://dashboard.aiondashboard.site/`
