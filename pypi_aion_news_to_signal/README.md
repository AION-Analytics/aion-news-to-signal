# AION India Event Intelligence

Convert Indian financial headlines into structured sector-level intelligence using causal propagation — not sentiment, not trading signals.

Formerly `aion-news-to-signal`.

## LLM Capture

### Component

`aion-news-to-signal` is a thin Python client for the public AION India Event Intelligence endpoint.

It converts one Indian financial headline into:

- an event classification
- sector-level impact output
- a compact sector bias summary
- stakeholder-specific views

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

This alias remains supported and still routes through the managed AION API.

### Python API

```python
analyze(headline: str, published_at: str | None = None) -> dict
```

### Output Shape

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
  "raw_assignment": {}
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

### Use This For

- Indian financial headline analysis
- sector-aware market intelligence
- LLM workflows that need structured market output
- dashboards, bots, and SaaS layers built on top of structured market intelligence

### Do Not Use This For

- direct execution without your own risk controls
- broker connectivity
- portfolio advice
- legal/compliance decisions

## Human Understanding

Most finance NLP tools stop at sentiment.

That is not enough if you are trying to build something operational for Indian markets.

Developers usually need to know:

- what event occurred
- which sectors are affected
- whether the event creates positive or negative sector bias
- whether the structured output still makes sense under the current volatility regime

This package is intentionally small because its job is integration, not bundling the full model stack into your local environment.

## Basic English Example

A plain sentiment model might say a repo-rate hike headline is negative.

A trading system usually needs more than that:

- which sectors benefit?
- which sectors get pressured?
- what compact positive/negative sector bias is implied?
- what is the justification for that output?

## Technical Example

```python
from aion_news_to_signal import analyze

headline = "Heatwave in Punjab damages wheat crop and threatens food inflation"
result = analyze(headline)

print(result["event"])
print(result["sector_vector"])
print(result["sector_directional_bias"])
print(result["stakeholder_views"])
```

## Hosted API Notes

- API key required for production usage
- monthly quota is enforced at the API layer
- use your website access flow for key provisioning

## Links

- PyPI:
  - `https://pypi.org/project/aion-news-to-signal/`
- Managed API:
  - `https://api.aiondashboard.site/v1/analyze`
- Hugging Face Space:
  - `https://huggingface.co/spaces/AION-Analytics/aion-news-to-signal`
- Website model page:
  - `https://dashboard.aiondashboard.site/models/news-to-signal`
