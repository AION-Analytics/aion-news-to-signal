---
language: en
license: agpl-3.0
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

[![Version](https://img.shields.io/badge/version-1.0.2-blue)](https://dashboard.aiondashboard.site/models/news-to-signal)

# AION India Event Intelligence

Structured event intelligence for Indian financial markets.

AION India Event Intelligence converts a single Indian financial headline into structured event, sector, stakeholder, and meta-factor output. It answers "what happened, which sectors are affected, and who gains or loses" — not just "is this positive or negative."

Formerly `aion-news-to-signal`.

## Why This Exists

Most financial NLP tools stop at sentiment polarity. Indian markets require more: 32 NSE sectors move differently on the same RBI announcement. A crude oil shock lifts energy but pressures aviation. A weather event cascades through agriculture, logistics, and food retail. AION India Event Intelligence models these causal chains explicitly — through a maintained taxonomy of 152 Indian financial event types, sector-level propagation rules, and 5 meta-factor decomposition (interest rate, crude oil, rupee, risk sentiment, liquidity). This is not sentiment. It is structured event intelligence.

## Supported Production Access

AION India Event Intelligence is exposed as a managed API.

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

## Output Contract

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

- Free tier: limited monthly requests via API key
- The public Hugging Face Space is a demo environment with rate limits and cold starts — it is not intended for production usage
- Production access requires an API key from the AION dashboard
- Requests are metered; over-quota requests are rejected

### Deployment Model

AION India Event Intelligence is an API-first system. The model weights are not publicly distributed. Production access is through the managed AION API only. The PyPI package (`aion-news-to-signal`) provides client-side tooling and MCP server entrypoints — it does not bundle model weights.

### Licensing Note

The public client/code surface for AION India Event Intelligence is distributed under AGPL-3.0-or-later. Some deterministic taxonomy rule files in the main GitHub repository are governed separately under Business Source License 1.1 with a future AGPL change date. See the repository `LICENSE` and `LICENSE.BSL11` files for the exact split.

### Use This For

- Indian financial headline reasoning
- event classification with sector propagation
- stakeholder-level interpretation
- dashboard, agent, and research integrations

### Do Not Use This For

- blind execution
- broker integration by itself
- compliance or suitability decisions
- unsupported local inference workflows

### Next Steps

1. Try the demo: `https://huggingface.co/spaces/AION-Analytics/aion-news-to-signal`
2. Get an API key: `https://dashboard.aiondashboard.site/access/register`
3. View full documentation: `https://dashboard.aiondashboard.site/models/news-to-signal`
4. Integrate via MCP: `https://dashboard.aiondashboard.site/models/news-to-signal`

## Cross Links

- API gateway:
  - `https://dashboard.aiondashboard.site/systems/api-gateway`
- GitHub repository:
  - `https://github.com/AION-Analytics/aion-news-to-signal`
- PyPI package:
  - `https://pypi.org/project/aion-news-to-signal/`
- website model page:
  - `https://dashboard.aiondashboard.site/models/news-to-signal`
- registration:
  - `https://dashboard.aiondashboard.site/access/register`
- live demo space:
  - `https://huggingface.co/spaces/AION-Analytics/aion-news-to-signal`

## Citation

```bibtex
@software{aion_india_event_intelligence_2026,
  author = {AION Analytics},
  title = {AION India Event Intelligence},
  year = {2026},
  url = {https://huggingface.co/AION-Analytics/aion-news-to-signal},
}
```
