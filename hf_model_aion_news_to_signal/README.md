---
language: en
license: apache-2.0
tags:
- finance
- market-intelligence
- event-impact-analysis
- sector-intelligence
- causal-inference
- indian-markets
- nse
- deep-tech
- india-ai
datasets:
- proprietary-indian-financial-news
metrics:
- accuracy
- f1-score
---

# AION India Event Intelligence

Convert Indian financial headlines into structured sector-level intelligence using causal propagation — not sentiment, not trading signals.

Formerly `aion-news-to-signal`.

## LLM Capture

### Component

This Hugging Face surface is the semantic definition layer for AION India Event Intelligence.

Primary developer goal:

- convert one headline into structured event, sector, and stakeholder output

### Supported Production Access

AION India Event Intelligence is an API-first system.

Production usage flows through the managed AION API:

- `POST https://api.aiondashboard.site/v1/analyze`
- header:
  - `X-API-Key: <key>`

Example:

```bash
curl -X POST "https://api.aiondashboard.site/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <key>" \
  -d '{"headline":"RBI hikes repo rate by 25 bps"}'
```

Python example:

```python
import requests

resp = requests.post(
    "https://api.aiondashboard.site/v1/analyze",
    headers={"X-API-Key": "<key>"},
    json={"headline": "RBI hikes repo rate by 25 bps"},
    timeout=30,
)
resp.raise_for_status()
print(resp.json()["sector_vector"])
```

### Output Contract

```json
{
  "headline": "string",
  "event": "string|null",
  "confidence": "float",
  "vix_regime": "string",
  "sector_vector": {},
  "top_positive_sectors": {},
  "top_negative_sectors": {},
  "sector_directional_bias": {
    "positive_bias": [],
    "negative_bias": []
  },
  "stakeholder_views": {},
  "raw_assignment": {
    "resolved_event_id": "string|null",
    "cause_effect_rule_id": "string|null",
    "weather_triggered": "bool"
  }
}
```

Canonical key note:

- `sector_vector` is the full scored sector impact map
- there is no `sector_impacts` key in the public output contract

### Quota And Access

- Free tier: limited monthly requests
- API key required
- Requests beyond quota are rejected deterministically

### Supported Contract Boundary

Local inference is not part of the supported production contract.

No guarantee is made here for:

- offline inference
- local execution support
- direct `transformers` / `from_pretrained(...)` workflows
- quota-free access

### Use This For

- Indian financial headline reasoning
- sector-level impact extraction
- market-monitoring workflows
- LLM, dashboard, and research integrations

### Do Not Use This For

- blind execution
- broker integration by itself
- compliance or suitability decisions
- price forecasting without additional layers

## Human Understanding

This system is designed to answer a more useful question than simple positive-or-negative classification.

It is meant to help developers and internal systems understand:

- what happened
- which sectors are affected
- what positive or negative sector bias follows
- how stakeholder interpretation changes across the same event

The production contract is managed access, not open local usage.

That is intentional:

- quota is enforced at the API layer
- production usage is keyed and controlled
- public documentation should not imply unsupported local execution assumptions

## Access

Request API access through the AION model page:

- `https://dashboard.aiondashboard.site/models/news-to-signal`

## Cross Links

- website model page:
  - `https://dashboard.aiondashboard.site/models/news-to-signal`
- live demo space:
  - `https://huggingface.co/spaces/AION-Analytics/aion-news-to-signal`
- GitHub repo:
  - `https://github.com/AION-Analytics/aion-news-to-signal`
- MCP registry:
  - `https://registry.modelcontextprotocol.io/v0.1/servers/io.github.AION-Analytics%2Faion-news-to-signal/versions/1.0.2`

## Citation

```bibtex
@software{aion_india_event_intelligence_2026,
  author = {AION Analytics},
  title = {AION India Event Intelligence},
  year = {2026},
  url = {https://huggingface.co/AION-Analytics/aion-news-to-signal},
}
```
