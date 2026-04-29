# aion-news-to-signal

Thin Python client for the public AION News-to-Signal endpoint.

AION converts Indian financial news into signals for Indian financial markets, NSE workflows, and news-based trading India use cases.

AION converts Indian financial news into:

- event classifications
- sector-level trading signals
- which sectors to long or short
- stakeholder views

This first PyPI release is intentionally minimal. It does not bundle model
weights. It calls the live hosted endpoint:

- Space: `https://huggingface.co/spaces/AION-Analytics/aion-news-to-signal`
- App: `https://aion-analytics-aion-news-to-signal.hf.space`

## Install

```bash
pip install aion-news-to-signal
```

## Quick Start

```python
from aion import analyze

result = analyze("RBI hikes repo rate by 25 bps")
print(result["event"])
print(result["trade_direction_signals"])
```

Also supported:

```python
from aion_news_to_signal import analyze
```

## Hosted API Notes

The current public endpoint is backed by a Hugging Face Space, so the client
uses the Gradio API flow internally.

Measured on `2026-04-26`:

- cold start proxy: `~1.68 s`
- warm latency average: `~716.6 ms`

## Links

- GitHub: `https://github.com/AION-Analytics/aion-news-to-signal`
- Hosted API: `https://aion-analytics-aion-news-to-signal.hf.space`
