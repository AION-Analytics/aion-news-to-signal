# AION India Event Intelligence

Convert Indian financial headlines into structured sector-level intelligence using causal propagation — not sentiment, not trading signals.

Formerly `aion-news-to-signal`.

API-first Python and MCP client for Indian financial headline intelligence.

<!-- mcp-name: io.github.AION-Analytics/aion-news-to-signal -->

## API Key Setup

```bash
export AION_API_KEY="<your_api_key>"
```

```python
from aion_news_to_signal import analyze

result = analyze("RBI hikes repo rate by 25 bps")
print(result["sector_vector"])
```

Legacy compatibility alias:

```python
from aion import analyze
```

This alias remains supported and still routes through the managed AION API.

## API Contract

This package is a client interface for the AION API.

- Requires API key
- Enforces quota limits
- No local model execution guaranteed
- All production usage flows through API endpoints

Managed endpoint:

- `POST https://api.aiondashboard.site/v1/analyze`

API access page:

- `https://dashboard.aiondashboard.site/models/news-to-signal`

## MCP server

This package also includes the AION India Event Intelligence MCP server entrypoint.

The MCP layer:

- requires `AION_API_KEY`
- is quota-controlled
- returns structured sector intelligence, not trading signals
- does not execute trades or generate executable orders

```bash
python -m aion_news_to_signal.mcp_server
```
