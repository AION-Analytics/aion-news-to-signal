# AION Market Sentiment Engine

Real-time sentiment intelligence for Indian financial markets.

Aggregates news, sector data, and volatility signals to produce actionable sentiment indicators for trading systems. Designed for low-latency algorithmic trading environments.

**Model Accuracy:** 98.55% on Indian financial news | **Coverage:** 592 NSE tickers | **Latency:** <100ms inference

---

## Quick Start

```python
from aion_sentiment import AIONSentimentAnalyzer
from aion_sectormap import SectorMapper
from aion_volweight import weight_confidence

# Initialize
analyzer = AIONSentimentAnalyzer()  # Downloads model automatically
mapper = SectorMapper()

# Analyze news
df = mapper.map(pd.DataFrame({
    'ticker': ['RELIANCE', 'TCS', 'HDFCBANK'],
    'headline': ['Record profits', 'Major deal win', 'Rural expansion']
}), ticker_column='ticker')

df = analyzer.analyze(df, text_column='headline')
df = weight_confidence(df, vix_value=18)

print(df[['ticker', 'sector', 'sentiment_label', 'sentiment_confidence_adjusted']])
```

---

## Packages

| Package | Purpose | Status |
|---------|---------|--------|
| **aion-sentiment** | Sentiment & emotion analysis | Ready |
| **aion-sentiment-in** | Training pipeline (98.55% accuracy) | Ready |
| **aion-sectormap** | NSE ticker → Sector mapping (592 tickers) | Ready |
| **aion-volweight** | VIX-based confidence adjustment | Ready |
| **aion-newsimpact** | Historical news impact analysis | Ready |

---

## Models

### AION-Sentiment-IN-v1

| Metric | Value |
|--------|-------|
| **Accuracy** | 98.55% |
| **F1 Score** | 98.65% |
| **Training Data** | 957K Indian financial news headlines |
| **Inference Time** | <100ms per headline |
| **Download** | [HuggingFace](https://huggingface.co/AION-Analytics/aion-sentiment-in-v1) |

---

## Installation

```bash
# Install all packages
pip install aion-sentiment aion-sectormap aion-volweight aion-newsimpact

# Or install individually
pip install aion-sentiment  # Core sentiment analysis
pip install aion-sectormap  # Sector mapping
pip install aion-volweight  # VIX adjustment
pip install aion-newsimpact # Impact analysis
```

---

## Data Assets

| Asset | Count | Description |
|-------|-------|-------------|
| **NSE Sector Constituents** | 188 companies | 14 sectors |
| **NSE Group Companies** | 591 companies | 44 sectors, 340 groups |
| **NRC Emotion Lexicon** | 14,182 words | Bundled with aion-sentiment |

---

## Development

```bash
# Clone repository
git clone https://github.com/AION-Analytics/market-sentiments.git
cd market-sentiments

# Install with dev dependencies
cd aion-sentiment && pip install -e ".[dev]"

# Run tests
pytest
```

---

## License

Apache License 2.0

**Attribution:** When using these packages, include:
```
This project uses AION Analytics open-source packages.
Visit https://github.com/AION-Analytics for more information.
```

---

## Contact

- **Email:** aionlabs@tutamail.com
- **GitHub:** https://github.com/AION-Analytics
- **HuggingFace:** https://huggingface.co/AION-Analytics

---

*Built for the Indian financial community*
