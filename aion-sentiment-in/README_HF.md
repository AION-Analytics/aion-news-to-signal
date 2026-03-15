---
license: apache-2.0
tags:
- sentiment-analysis
- financial-nlp
- indian-markets
- nse
- bse
- text-classification
- transformer
- pytorch
- safetensors
- trading
- market-intelligence
- quant
- algorithmic-trading
language:
- en
library_name: transformers
pipeline_tag: text-classification
inference: false
---

# AION Market Sentiment Engine

**Real-time sentiment intelligence for Indian financial markets**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub](https://img.shields.io/badge/GitHub-AION--Analytics-green)](https://github.com/AION-Analytics/market-sentiments)

---

## Overview

Financial markets react rapidly to news and macro signals. **AION-Sentiment-IN-v1** aggregates multi-source sentiment signals to generate structured market sentiment indicators for Indian markets (NSE/BSE).

**Designed for:**
- Algorithmic trading systems
- Quantitative research
- Market intelligence platforms
- Risk management systems

---

## Problem Statement

Indian financial markets lack open-source, production-ready sentiment analysis tools optimized for:
- **Local context** - NSE/BSE specific news and tickers
- **Low latency** - Intraday trading requires <100ms inference
- **High accuracy** - Trading decisions need 95%+ accuracy
- **Sector mapping** - News must map to tradable instruments

AION-Sentiment-IN-v1 solves this with a transformer model tuned on 957K Indian financial news headlines.

---

## Key Capabilities

| Capability | Description |
|------------|-------------|
| **News Sentiment Extraction** | Classifies headlines as positive/neutral/negative |
| **Multi-Source Aggregation** | Works with news APIs, RSS feeds, social media |
| **Sector Mapping** | Maps sentiment to 592 NSE tickers across 44 sectors |
| **VIX Adjustment** | Adjusts confidence based on market volatility regime |
| **Historical Impact** | Matches current news to historical patterns with price impact |

---

## Quick Start

### Using Transformers

```python
from transformers import pipeline

# Load model
sentiment = pipeline("text-classification", model="AION-Analytics/aion-sentiment-in-v1")

# Analyze news
result = sentiment("Oil prices surge after geopolitical tensions rise")
print(result)
# [{'label': 'positive', 'score': 0.9389}]
```

### Using AION SDK

```python
from aion_sentiment import AIONSentimentAnalyzer

analyzer = AIONSentimentAnalyzer()
result = analyzer.predict("RBI announces surprise rate cut")
print(result)
# [{'label': 'positive', 'confidence': 0.9150}]
```

---

## Architecture

```
┌─────────────────┐
│ News Sources    │
│ • APIs          │
│ • RSS Feeds     │
│ • Social Media  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Sentiment Model │
│ • Transformer   │
│ • 98.55% Acc    │
│ • <100ms        │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Sector Mapper   │
│ • 592 Tickers   │
│ • 44 Sectors    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ VIX Adjustment  │
│ • LOW <12       │
│ • HIGH 15-25    │
│ • PANIC ≥25     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Signal Output   │
│ • JSON API      │
│ • DataFrame     │
│ • WebSocket     │
└─────────────────┘
```

---

## Performance Benchmarks

### Model Accuracy

| Metric | Score |
|--------|-------|
| **Accuracy** | 98.55% |
| **F1 Score (macro)** | 98.65% |
| **Precision (macro)** | 98.70% |
| **Recall (macro)** | 98.60% |

### Latency

| Task | Latency | Throughput |
|------|---------|------------|
| **Single headline** | <50ms | - |
| **Batch (100)** | <200ms | 500/sec |
| **Sector mapping** | <10ms | 10,000/sec |

### Model Evaluation

| Metric | Score |
|--------|-------|
| **Accuracy** | 98.55% |
| **F1 Score (macro)** | 98.65% |
| **Precision (macro)** | 98.70% |
| **Recall (macro)** | 98.60% |
| **Training Samples** | 957K headlines |
| **Validation Samples** | 2K headlines |

*Dataset: 957K Indian financial news headlines (Oct 2025 - Feb 2026)*
*Classification source: UNIFIED_ROUTER_V4 (99.99% confidence)*

###

```python
from aion_sentiment import AIONSentimentAnalyzer

analyzer = AIONSentimentAnalyzer()

# Analyze breaking news
news = "RBI announces surprise rate cut"
result = analyzer.predict(news)

if result[0]['label'] == 'positive' and result[0]['confidence'] > 0.9:
    print("BUY Signal: Banking sector")
```

### 2. Sector Rotation

```python
from aion_sentiment import AIONSentimentAnalyzer
from aion_sectormap import SectorMapper

mapper = SectorMapper()
analyzer = AIONSentimentAnalyzer()

# Get sentiment by sector
for sector in mapper.get_all_sectors():
    tickers = mapper.get_tickers_in_sector(sector)[:10]
    # Analyze news for each ticker
    # Aggregate sector sentiment
    # Rotate to highest sentiment sectors
```

### 3. Risk Management

```python
from aion_volweight import get_regime

# Check VIX regime
regime = get_regime(vix=28)  # Returns "PANIC"

# Adjust position sizing
if regime == "PANIC":
    position_size = 0.5  # Reduce by 50%
```

---

## Example Outputs

### Single Headline

| Input | Output | Confidence |
|-------|--------|------------|
| "Stock market reaches all-time high" | positive | 93.8% |
| "Market crashes on recession fears" | negative | 90.5% |
| "Trading volume remains average" | neutral | 94.5% |

### Sector Sentiment

| Sector | Bullish | Neutral | Bearish | Net |
|--------|---------|---------|---------|-----|
| Banking | 65% | 25% | 10% | +55% |
| IT | 72% | 20% | 8% | +64% |
| Auto | 45% | 35% | 20% | +25% |
| FMCG | 58% | 30% | 12% | +46% |
| Metal | 30% | 40% | 30% | 0% |

---

## Installation

### Option 1: Direct Model Usage

```bash
pip install transformers torch
```

### Option 2: Full AION SDK

```bash
pip install aion-sentiment aion-sectormap aion-volweight aion-newsimpact
```

---

## Related Resources

| Resource | Link |
|----------|------|
| **GitHub Repository** | https://github.com/AION-Analytics/market-sentiments |
| **Documentation** | https://github.com/AION-Analytics/market-sentiments/blob/main/README.md |
| **Environment Setup** | https://github.com/AION-Analytics/market-sentiments/blob/main/ENV_SETUP.md |
| **Example Notebook** | https://github.com/AION-Analytics/market-sentiments/blob/main/examples/sentiment_analysis.ipynb |
| **Issue Tracker** | https://github.com/AION-Analytics/market-sentiments/issues |

---

## Citation

```bibtex
@software{aion_sentiment_in_2026,
  author = {AION Analytics},
  title = {AION-Sentiment-IN-v1: India-Tuned Sentiment Analysis for Financial News},
  year = {2026},
  url = {https://huggingface.co/AION-Analytics/aion-sentiment-in-v1},
  license = {Apache-2.0}
}
```

---

## License

Apache License 2.0

**Attribution Requirement:**
When using this model in research or products, please include:
```
This project uses AION-Sentiment-IN model from AION Analytics.
Visit https://github.com/AION-Analytics for more information.
```

---

## Contact

- **Email:** aionlabs@tutamail.com
- **GitHub:** https://github.com/AION-Analytics
- **HuggingFace:** https://huggingface.co/AION-Analytics

---

*Model card last updated: March 14, 2026*  
*Built for the Indian financial community*
