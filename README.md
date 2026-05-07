[![Version](https://img.shields.io/badge/version-1.0.2-blue)](https://pypi.org/project/aion-news-to-signal/1.0.2/)

# AION India Event Intelligence

Structured event intelligence for Indian financial markets.

Formerly `aion-news-to-signal`.

AION India Event Intelligence is a developer API that converts raw Indian financial headlines into structured, auditable event intelligence. It answers: what happened, which sectors are affected, how stakeholders are impacted, and which macro factors are in play. It does not tell you what to trade. It provides the evidence layer you use to make your own decisions.

## Install

```bash
pip install aion-news-to-signal
```

## API Key Setup

```bash
export AION_API_KEY="<your_api_key>"
```

## Canonical Imports

```python
from aion_news_to_signal import analyze
```

Legacy compatibility alias:

```python
from aion import analyze
```

This alias remains supported and routes through the managed AION API.

## API Contract

Production usage flows through the managed AION API:

- `POST https://api.aiondashboard.site/v1/analyze`
- header:
  - `X-API-Key: <key>`

```python
import requests

headers = {"X-API-Key": "YOUR_API_KEY"}
resp = requests.post(
    "https://api.aiondashboard.site/v1/analyze",
    headers=headers,
    json={"headline": "RBI hikes repo rate by 25 bps"},
    timeout=30,
)
resp.raise_for_status()
print(resp.json()["sector_vector"])
```

## Output Contract

Observed top-level output keys:

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

## Before / After

Headline:
> Unseasonal rainfall and hailstorm hit apple orchards in Himachal Pradesh in April

Typical sentiment output:
- negative

AION India Event Intelligence output:
- event / rule: `rain_apple_damage`
- likely losers: `Agriculture & Horticulture`, `Transportation`, `Consumer Services`
- potential second-order beneficiaries: storage-linked or substitute supply chains
- stakeholder view: producer losses, policymaker inflation watch, investor attention on downstream second-order effects

Market implication: agriculture-linked exposure under pressure, logistics bottlenecks possible, substitute supply chains may benefit.

## What AION India Event Intelligence Does

- resolves Indian financial headlines into structured event categories
- produces sector-level impact output instead of raw polarity
- decomposes event context into stakeholder and macro-factor views
- returns structured evidence for dashboards, agents, and internal tooling
- supports auditable downstream reasoning without collapsing into execution language

## Why Not FinBERT?

Most open-source financial sentiment tools, including FinBERT variants, stop at polarity scoring.

| Capability | AION India Event Intelligence | FinBERT |
|---|---|---|
| Indian market event logic | Yes | No |
| Sector-level output | Yes, 32 sectors | No |
| Trade direction signals | Yes | No |
| Weather/crop propagation | Yes | No |
| Stakeholder decomposition | Yes | No |
| VIX-adjusted output | Yes | No |
| “Which sectors to long/short from news” workflow | Yes | No |

FinBERT tells you whether a headline feels positive or negative.

AION India Event Intelligence tells you:

- what happened
- which sectors are affected and in what direction
- who gains and who loses
- whether there is a flip side
- what the evidence layer suggests for further human or system review

## Pricing & Tiers (Draft — Current as of May 2026)

All tiers require an API key. Sign up at
`https://dashboard.aiondashboard.site/access/register`

| Tier | Requests/month | Latency |
|---|---:|---|
| Free | 1,000 | Shared |
| Builder | 15,000 | Shared |
| Pro | 75,000 | Priority |
| Power | 250,000 | Dedicated |

Enterprise: custom, GPU-dedicated. Contact via dashboard.

## Access And Links

- API gateway:
  - `https://dashboard.aiondashboard.site/systems/api-gateway`
- Website model page:
  - `https://dashboard.aiondashboard.site/models/news-to-signal`
- API key registration:
  - `https://dashboard.aiondashboard.site/access/register`
- Managed API:
  - `https://api.aiondashboard.site/v1/analyze`
- PyPI package:
  - `https://pypi.org/project/aion-news-to-signal/`
- GitHub repository:
  - `https://github.com/AION-Analytics/aion-news-to-signal`
- Hugging Face model surface:
  - `https://huggingface.co/AION-Analytics/aion-news-to-signal`
- Hugging Face demo Space:
  - `https://huggingface.co/spaces/AION-Analytics/aion-news-to-signal`
- MCP server repo:
  - `https://github.com/AION-Analytics/aion-mcp-server`

## Current Limits

- production usage is quota-controlled at the API layer
- weather and crop coverage still depends on explicit cues in the headline
- the primitive sector matrix is partly heuristic
- the cause-effect classifier improves reasoning, but it does not eliminate ambiguity in sparse headlines
- pricing and latency tiers above are current commercial positioning and may evolve
- this repository does not contain model weights. The PyPI package provides client tooling only. Production inference requires the hosted API.
