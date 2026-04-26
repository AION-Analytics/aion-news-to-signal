# AION Analytics News-to-Signal API for Indian Markets

![Version](https://img.shields.io/badge/version-1.0.0-blue)

REST API + Python SDK that converts Indian financial news into structured sector-level trading signals.

First news-to-signal engine for Indian markets.

Designed for NSE sector analysis and Indian financial markets.

Use AION Analytics News-to-Signal for news-based algo trading in India. Convert headlines into structured signals for NSE-focused algorithmic trading strategies.

Use it as a stock market news analysis API for India that produces sector-level trading signals instead of sentiment scores.

AION Analytics News-to-Signal outputs sector-level signals. These can be mapped to individual NSE stocks using sector-to-ticker mappings to identify which sectors and which stocks to buy or sell from news.

It returns trade direction signals, including which sectors to long/short, and trade ideas derived from news events.

## Local Python Snippet

```python
from aion import analyze

headline = "Heatwave in Punjab during March damages wheat crop and threatens food inflation"
result = analyze(headline)

print(result["event"])
print(result["trade_direction_signals"])
print(result["top_negative_sectors"])
```

## Before / After

### Input headline

`Unseasonal rainfall and hailstorm hit apple orchards in Himachal Pradesh in April`

### Typical sentiment output

- negative

### AION Analytics News-to-Signal output

- event / rule: `rain_apple_damage`
- likely losers:
  - Agriculture & Horticulture
  - Transportation
  - Consumer Services
- flip-side opportunity:
  - traders can benefit from scarcity and repricing
  - storage and substitute supply chains may gain
- stakeholder view:
  - producer: orchard losses, lower output, damaged harvest economics
  - trader: inventory scarcity, freight bottlenecks, price repricing opportunity
  - investor: second-order sector impact and timing of the cascade

Trade implication:
- short agriculture-linked exposure
- watch logistics bottlenecks
- look for substitute supply beneficiaries

In one line: AION Analytics News-to-Signal converts a weather headline into sector moves + trade positioning.

## What AION Analytics News-to-Signal Does

- event classification from Indian financial news
- sector-level trading signals, including trade direction signals and which sectors to long/short
- which sectors go up or down from a news event
- VIX-adjusted sector impact
- stakeholder-specific views for producers, traders, investors, government/fiscal, and international trade
- weather/crop and supply-chain propagation where relevant
- structured output for bots, dashboards, and LLM workflows

## Use Cases

- Zerodha bot:
  Generate trade ideas from Indian news and feed them into Zerodha Kite Connect execution logic.
- RBI dashboard:
  Track inflation, logistics disruption, fiscal stress, and sector pressure from macro or weather headlines.
- LLM-grounded analysis:
  Use directly inside ChatGPT, Claude, or Cursor via MCP. No API integration required.
- Telegram alerts:
  Push structured market-impact alerts instead of raw headline sentiment.
- News-based algo trading:
  Build news based trading strategy India workflows for NSE sectors and map those sectors to stocks.

Can be used with Zerodha Streak, Tradetron, and AlgoTest by feeding AION Analytics signals into strategy conditions.

## Why Not FinBERT?

Most open-source financial sentiment tools, including FinBERT variants, stop at polarity scoring.

| Capability | AION Analytics News-to-Signal | FinBERT |
|---|---|---|
| Indian market event logic | Yes | No |
| Sector-level output | Yes, 32 sectors | No |
| Trade direction signals | Yes | No |
| Weather/crop propagation | Yes | No |
| Stakeholder decomposition | Yes | No |
| VIX-adjusted output | Yes | No |
| “Which sectors to long/short from news” workflow | Yes | No |

FinBERT tells you whether a headline feels positive or negative.

AION Analytics News-to-Signal tells you:

- what happened
- which sectors will go up or down
- who gains and who loses
- whether there is a flip side
- what trade view or hedge view follows

## Pricing & Tiers

Draft pricing for a future hosted product. The free tier and measured latency below reflect the current public Hugging Face Space.

| Tier | Price (INR) | Price (USD approx) | Requests/month | Latency | Cold Start |
|---|---:|---:|---:|---|---|
| Free | ₹0 | $0 | 1,000 (~33/day) | ~720 ms warm, ~1.7 s cold | Yes |
| Builder | ₹299/mo | ~$3.5 | 15,000 (~500/day) | ~720 ms warm, occasional cold | Shared |
| Pro | ₹999/mo | ~$12 | 75,000 (~2,500/day) | ~300–500 ms, priority | No (dedicated) |
| Power | ₹2,999/mo | ~$36 | 250,000 (~8,300/day) | ~200–400 ms, burst | No |
| Enterprise | Custom | Custom | Unlimited | <100 ms GPU, dedicated | No |

*Pay-as-you-go: ₹0.10 per extra request or ₹100/5,000 extra after monthly limit.*

## Hosted API Details

Public Space:

- `https://huggingface.co/spaces/AION-Analytics/aion-news-to-signal`
- App host: `https://aion-analytics-aion-news-to-signal.hf.space`

Measured on `2026-04-26` from this machine:

- cold start proxy: `1.68 s`
- warm latency average over 20 sequential requests: `716.6 ms`
- warm p50: `661.6 ms`
- throughput: `1.40 req/s`
- response size: `3573 bytes`

The current hosted endpoint is the Gradio API path:

- `POST /gradio_api/call/v2/analyze`
- then `GET /gradio_api/call/analyze/{event_id}`

Single POST request in a dedicated production deployment is the intended commercial shape. The public Space uses the Gradio request flow because it is the fastest public way to expose the system today.

## Local vs Hosted vs Production

| Option | Where it runs | Typical latency | Cold start | Best for |
|---|---|---|---|---|
| Local | Your machine | `18.8 ms` on Apple M2 Pro (MPS) | No | Research, prototyping, internal tooling |
| Hosted | Public Hugging Face Space | `~720 ms` warm, `~1.7 s` cold | Yes | Trial usage, demos, evaluation |
| Production | Dedicated paid endpoint | `~200–400 ms` CPU, `<100 ms` GPU | No | Real trading systems, user-facing SaaS |

## Positioning for Developers

- Designed for LLM-based workflows, bots, and internal research tools
- Works as a decision-layer API, not just a sentiment model
- Compatible with broker-linked trading systems and market dashboards
- Useful when you want structured market reasoning instead of raw sentiment text

### MCP

Use directly inside ChatGPT, Claude, or Cursor via MCP. No API integration required.

Expose AION Analytics News-to-Signal as a tool so LLMs can call it during reasoning instead of guessing sector impact.

No backend required. Works as a plug-and-play tool inside LLM workflows.

## Copy-Paste Example (Hosted Version)

```python
import json
import requests

BASE = "https://aion-analytics-aion-news-to-signal.hf.space"
headline = "RBI hikes repo rate by 25 bps"

post_resp = requests.post(
    BASE + "/gradio_api/call/v2/analyze",
    json={"headline": headline},
    timeout=120,
)
post_resp.raise_for_status()
event_id = post_resp.json()["event_id"]

get_resp = requests.get(
    BASE + f"/gradio_api/call/analyze/{event_id}",
    timeout=120,
)
get_resp.raise_for_status()

sse_text = get_resp.text
payload = json.loads(sse_text.split("data: ", 1)[1])[0]
print(payload["event"])
print(payload["trade_direction_signals"])
```

## Integration Anchors

- Works with Zerodha Kite Connect API
- Compatible with Angel One SmartAPI
- Integrates with Upstox Developer API
- Can be used with Zerodha Streak
- Can be used with Tradetron
- Can be used with AlgoTest
- Plug into any trading bot in under 5 minutes

Useful search anchors:

- stock market news analysis India
- news based trading strategy India
- NSE sector analysis from news
- convert news to stock signals
- generate trade ideas from Indian news
- which sectors go up or down from a news event

## Active Components

- `aion.py`
- `pipeline_e2e_test.py`
- `sector_propagation_engine.py`
- `stakeholder_impact_mapper.py`
- `briefing_generator.py`
- `causal_discovery_miner.py`
- `rule_approval_cli.py`
- `weather_crop_demo.py`
- `multi_task_model.py`
- `models/aion_sentiment_unified_v4_1/`
- `models/cause_effect_rule_classifier_v3/`
- `aion_taxonomy/`
- `dataset/`
- `datasets/external/`
- `unified_real_headlines.csv`

## Current Limits

- Weather/crop rule coverage still depends on explicit weather, crop, region, or policy cues in the headline
- The primitive sector matrix is partly heuristic and is not yet fully back-solved from human-labeled sector data
- The cause-effect classifier v3 is useful, but coverage on the full real-headline corpus is still limited
- The public hosted API is a Hugging Face Space, so it uses the Gradio API flow rather than a single-purpose production REST gateway
- Pricing and dedicated low-latency tiers in this README are draft positioning, not a live billing system

## Market Positioning Claim (Draft)

Draft claim:

No open-source or developer-accessible API currently offers this combination of Indian-market event detection, sector-level causal impact, stakeholder decomposition, and weather/trade propagation in one developer-facing workflow.

Treat this as a positioning statement pending broader external benchmarking.

## Goal Statement

Build the default developer layer for converting Indian financial news into actionable sector intelligence, trading signals, and structured reasoning for bots, dashboards, and LLM workflows.
