# AION India Event Intelligence

Convert Indian financial headlines into structured sector-level intelligence using causal propagation — not sentiment, not trading signals.

Formerly `aion-news-to-signal`.

![Version](https://img.shields.io/badge/version-1.0.2-blue)

## LLM Capture

### Component

The `aion-news-to-signal` package exposes AION India Event Intelligence for NSE-focused workflows.

### Install

```bash
pip install aion-news-to-signal
```

### API Key Setup

```bash
export AION_API_KEY="<your_api_key>"
```

### Canonical Imports

```python
from aion_news_to_signal import analyze
```

Legacy compatibility alias:

```python
from aion import analyze
```

This alias is still supported, but it routes to the managed AION API rather than a local runtime.

### Python API

Signature:

```python
analyze(headline: str, published_at: str | None = None) -> dict
```

### Output Contract

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

### Usage

```python
from aion_news_to_signal import analyze

result = analyze("RBI hikes repo rate by 25 bps")
print(result["sector_vector"])
```

### API Contract

This package is a client interface for the AION API.

- Requires API key
- Enforces quota limits
- No local model execution guaranteed
- All production usage flows through API endpoints

Managed endpoint:

- `POST https://api.aiondashboard.site/v1/analyze`

Copy-paste example:

```python
import requests

response = requests.post(
    "https://api.aiondashboard.site/v1/analyze",
    headers={"X-API-Key": "<your_api_key>"},
    json={"headline": "Heatwave in Punjab damages wheat crop and threatens food inflation"},
    timeout=30,
)
response.raise_for_status()
print(response.json()["sector_vector"])
```

### Use This For

- Indian financial headline classification
- sector-level impact estimation
- compact sector bias extraction
- stakeholder-aware market explanation
- bots, dashboards, research tools, and LLM workflows

### Do Not Use This For

- direct order execution without your own risk layer
- price prediction from text alone
- broker connectivity
- compliance, advisory, or portfolio suitability decisions

### Runtime Surfaces

- managed Python client:
  - `aion_news_to_signal/`
- managed API:
  - `https://api.aiondashboard.site/v1/analyze`
- API access page:
  - `https://dashboard.aiondashboard.site/models/news-to-signal`
- PyPI package:
  - `https://pypi.org/project/aion-news-to-signal/`

## Human Understanding

Indian market news is usually more complex than positive-or-negative sentiment.

A headline can affect:

- one sector directly
- a second sector through supply chains
- another stakeholder through fiscal, policy, or import/export effects
- the final market-context read differently depending on volatility regime

That is why this system is built as a market-intelligence layer, not just a sentiment model.

It tries to answer questions like:

- what happened?
- which sectors are likely to benefit or get hurt?
- what compact positive/negative sector bias follows from the headline?
- how should a trader, producer, investor, or policymaker read the same event differently?

For an aspiring developer, the practical takeaway is:

- sentiment alone is not enough for trading logic
- you need event resolution
- you need sector propagation
- you need justification fields so your downstream layer can decide whether to trust or ignore the structured output

For LLM workflows, the value is that the output is already structured. The model is easier to chain into:

- market-monitoring dashboards
- screening pipelines
- broker-side validation layers
- explanation layers in SaaS tools

## Basic English Example

Headline:

`Unseasonal rainfall and hailstorm hit apple orchards in Himachal Pradesh`

What a basic sentiment model usually says:

- negative

What this system tries to say instead:

- the event is agricultural weather damage
- agriculture-linked sectors may be pressured
- transportation and downstream supply chains may also feel it
- some substitute suppliers or storage-linked segments may benefit
- the downstream system may want a different response than a policymaker or producer

## Technical Example

```python
from aion_news_to_signal import analyze

headline = "Unseasonal rainfall and hailstorm hit apple orchards in Himachal Pradesh"
result = analyze(headline)

print(result["event"])
print(result["sector_vector"])
print(result["stakeholder_views"])
print(result["sector_directional_bias"])
```

## Access And Links

- PyPI:
  - `https://pypi.org/project/aion-news-to-signal/`
- Hugging Face model surface:
  - `https://huggingface.co/AION-Analytics/aion-news-to-signal`
- Hugging Face live demo:
  - `https://huggingface.co/spaces/AION-Analytics/aion-news-to-signal`
- Website model page:
  - `https://dashboard.aiondashboard.site/models/news-to-signal`
- MCP server repo:
  - `https://github.com/AION-Analytics/aion-mcp-server`
- MCP Registry:
  - `https://registry.modelcontextprotocol.io/v0.1/servers/io.github.AION-Analytics%2Faion-news-to-signal/versions/1.0.2`
- Use cases:
  - `docs/USE_CASES.md`

## Pricing And Access Notes

Draft access model:

| Tier | Price (INR) | Requests/month | Best for |
|---|---:|---:|---|
| Free | ₹0 | 1,000 | evaluation and prototypes |
| Builder | ₹299 | 15,000 | small tools and side projects |
| Pro | ₹999 | 75,000 | production SaaS or internal desks |
| Power | ₹2,999 | 250,000 | larger teams and heavier workloads |
| Enterprise | Custom | Unlimited | dedicated deployment needs |

Public signup links:

- free:
  - `https://api.aiondashboard.site/signup/free`
- paid:
  - `https://api.aiondashboard.site/signup/paid?plan=pro`

## Current Limits

- production usage is quota-controlled at the API layer
- weather and crop coverage still depends on explicit cues in the headline
- the primitive sector matrix is partly heuristic
- the cause-effect classifier improves reasoning, but it does not eliminate ambiguity in sparse headlines
- pricing and dedicated low-latency tiers above are still draft commercial positioning, not a live billing system

## Internal Repository Components

- `aion.py`
- `sector_propagation_engine.py`
- `stakeholder_impact_mapper.py`
- `briefing_generator.py`
- `causal_discovery_miner.py`
- `rule_approval_cli.py`
- `multi_task_model.py`
- `models/aion_sentiment_unified_v4_1/`
- `models/cause_effect_rule_classifier_v3/`
- `aion_taxonomy/`

## AION Positioning

AION Analytics builds developer infrastructure for Indian financial AI and deeptech.

This project is part of that goal:

- free layers reduce infrastructure pain
- structured model outputs reduce repeated trial-and-error
- developers can build their own reasoning, execution, and SaaS layers on top
