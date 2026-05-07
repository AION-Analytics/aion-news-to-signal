# AION India Event Intelligence — Client Library

Structured event intelligence for Indian financial markets.

This package provides:

- A Python client for the AION India Event Intelligence API
- An MCP server entrypoint for ChatGPT, Claude, Cursor, and other MCP-compatible tools
- Local data validation and output formatting utilities

This package does **NOT** contain model weights. Inference requires an API key from `https://dashboard.aiondashboard.site/access/register`.

## Quick Start

```python
from aion import analyze

# Requires AION_API_KEY environment variable or explicit key
result = analyze("RBI hikes repo rate by 25 bps", api_key="YOUR_KEY")
print(result["sector_vector"])
```

## MCP Server

```bash
python -m aion_news_to_signal.mcp_server
```

The MCP server requires an API key for inference. Set `AION_API_KEY` in your environment.

## API Contract

Production inference flows through the hosted AION API:

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

## Important Note

⚠️ This package is a client library, not a self-contained inference engine. It requires a valid API key and internet connectivity to call the AION hosted API. For local/offline inference, contact AION Analytics about enterprise deployment options.

## Links

- API gateway:
  - `https://dashboard.aiondashboard.site/systems/api-gateway`
- Website model page:
  - `https://dashboard.aiondashboard.site/models/news-to-signal`
- API key registration:
  - `https://dashboard.aiondashboard.site/access/register`
- GitHub:
  - `https://github.com/AION-Analytics/aion-news-to-signal`
- Hugging Face model:
  - `https://huggingface.co/AION-Analytics/aion-news-to-signal`
- Hugging Face demo:
  - `https://huggingface.co/spaces/AION-Analytics/aion-news-to-signal`
- PyPI package:
  - `https://pypi.org/project/aion-news-to-signal/`
