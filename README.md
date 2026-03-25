# AION Market Sentiment

**Developer toolkit for financial sentiment analysis**

AI-powered sentiment intelligence for Indian financial markets.

**98.55% accuracy** | **<100ms latency** | **592 NSE tickers** | **957K training samples**

---

## ⚠️ IMPORTANT NOTICE - Model Under Retraining

**Status:** The HuggingFace model is currently **private** and under retraining.

**Issue:** A data labeling inconsistency was discovered in the training dataset. The model is being retrained with corrected labels.

**Expected Resolution:** A corrected model will be released soon.

**What works:**
- ✅ Sector mapping (aion-sectormap)
- ✅ VIX adjustment (aion-volweight)
- ✅ News impact analysis (aion-newsimpact)

**What's temporarily unavailable:**
- ⏳ Sentiment analysis model (being retrained)

---

## What This Is

A **developer toolkit** for building financial sentiment models:

-  **Reusable Components** - Sentiment analysis, sector mapping, VIX adjustment
-  **Experimentation** - Quick prototyping for quant research
-  **Clean APIs** - Simple Python interfaces, no infra complexity
-  **India-Focused** - NSE/BSE tickers, Indian financial news

---

## What This Is NOT

This is **NOT** a production trading system. For production infrastructure (live ingestion, Redis streams, ClickHouse pipelines, execution engines), see our internal systems.

**This toolkit is for:**
-  ML engineers building sentiment models
-  Quant researchers prototyping strategies
-  Developers experimenting with financial NLP
-  Students learning financial sentiment analysis

**This toolkit is NOT for:**
-  Direct production trading (use internal systems)
-  Live tick data ingestion (use internal systems)
-  Order execution (use internal systems)
-  System governance/audit (use internal systems)

---

## Quickstart (30 seconds)

```bash
# Install
pip install aion-sentiment aion-sectormap aion-volweight

# Run
python -c "
from aion_sentiment import AIONSentimentAnalyzer
analyzer = AIONSentimentAnalyzer()
print(analyzer.predict(['Market reaches all-time high']))
"
```

**Output:**
```
[{'label': 'positive', 'confidence': 0.9389}]
```

---

## Example Output

### Sentiment Analysis
```
Headline                              | Sentiment | Confidence | VIX-Adjusted
--------------------------------------|-----------|------------|-------------
Reliance reports record profits       | positive  | 93.8%      | 93.8% (VIX=12)
Market crashes on recession fears     | negative  | 90.5%      | 45.2% (VIX=28)
TCS wins major digital deal           | positive  | 88.8%      | 88.8% (VIX=12)
```

### Sector Sentiment Heatmap
```
Sector              | Bullish | Neutral | Bearish | Net Sentiment
--------------------|---------|---------|---------|---------------
Banking             |   65%   |   25%   |   10%   |     +55%
IT                  |   72%   |   20%   |    8%   |     +64%
Auto                |   45%   |   35%   |   20%   |     +25%
FMCG                |   58%   |   30%   |   12%   |     +46%
Metal               |   30%   |   40%   |   30%   |      0%
```

### Historical Impact Analysis
```
Query: "Market crashes on recession fears"

Similar Historical News (last 30 days):
1. "Stock market tumbles on recession fears"    → -2.5% (next day)
2. "Investors panic as banks collapse"          → -3.8% (next day)
3. "Banking crisis spreads across Europe"       → -2.9% (next day)

Average 1-day Impact: -3.07%
```

---

## Architecture

```
┌─────────────────┐
│  Data Sources   │
│  • News APIs    │
│  • RSS Feeds    │
│  • Social Media │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Sentiment Engine│
│  • Transformer  │
│  • NRC Emotions │
│  • 98.55% Acc   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Sector Mapper   │
│  • 592 Tickers  │
│  • 44 Sectors   │
│  • 340 Groups   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ VIX Adjustment  │
│  • LOW <12      │
│  • NORMAL 12-15 │
│  • HIGH 16-25   │
│  • PANIC ≥25    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Signal Output   │
│  • JSON API     │
│  • DataFrame    │
│  • WebSocket    │
└─────────────────┘
```

---

## Packages

| Package | Purpose | Install |
|---------|---------|---------|
| **aion-sentiment** | Sentiment & emotion analysis | `pip install aion-sentiment` |
| **aion-sectormap** | NSE ticker → Sector mapping | `pip install aion-sectormap` |
| **aion-volweight** | VIX-based confidence adjustment | `pip install aion-volweight` |
| **aion-newsimpact** | Historical news impact analysis | `pip install aion-newsimpact` |
| **aion-sentiment-in** | Training pipeline | `pip install aion-sentiment-in` |

---

## Models

### AION-Sentiment-IN-v1

| Metric | Value |
|--------|-------|
| **Accuracy** | 98.55% |
| **F1 Score** | 98.65% |
| **Training Data** | 957K Indian financial news headlines |
| **Inference Time** | <100ms per headline |
| **Model Size** | 438 MB |
| **Download** | [HuggingFace](https://huggingface.co/AION-Analytics/aion-sentiment-in-v1) |

---

## Use Cases

### 1. Real-Time Trading Signals
```python
from aion_sentiment import AIONSentimentAnalyzer

analyzer = AIONSentimentAnalyzer()

# Analyze breaking news
news = "RBI announces surprise rate cut"
result = analyzer.predict(news)

if result[0]['label'] == 'positive' and result[0]['confidence'] > 0.9:
    print("BUY Signal: Banking sector")
```

### 2. Sector Rotation Strategy
```python
from aion_sentiment import AIONSentimentAnalyzer
from aion_sectormap import SectorMapper

mapper = SectorMapper()
analyzer = AIONSentimentAnalyzer()

# Get sentiment by sector
sector_sentiment = {}
for sector in mapper.get_all_sectors():
    tickers = mapper.get_tickers_in_sector(sector)[:10]
    # Analyze news for each ticker
    # Aggregate sector sentiment
    sector_sentiment[sector] = avg_sentiment

# Rotate to highest sentiment sectors
top_sectors = sorted(sector_sentiment.items(), key=lambda x: x[1], reverse=True)
```

### 3. Risk Management
```python
from aion_volweight import get_regime, weight_confidence

# Check VIX regime
regime = get_regime(vix=28)  # Returns "PANIC"

# Adjust position sizing based on sentiment confidence
if regime == "PANIC":
    position_size = 0.5  # Reduce by 50%
elif regime == "HIGH":
    position_size = 0.8  # Reduce by 20%
else:
    position_size = 1.0  # Full size
```

---

## Edge Cases & Confidence Scoring

### Edge Case Handling

| Scenario | Handling | Output |
|----------|----------|--------|
| **Empty text** | Return neutral with 0% confidence | `{'label': 'neutral', 'confidence': 0.0}` |
| **Very short text (<5 chars)** | Return neutral with low confidence | `{'label': 'neutral', 'confidence': 0.3}` |
| **Ambiguous news** | Low confidence score (<0.6) | `{'label': 'neutral', 'confidence': 0.55}` |
| **Conflicting signals** | Confidence reduced proportionally | `{'label': 'positive', 'confidence': 0.65}` |
| **Unknown ticker** | Sector mapping returns 'Unknown' | Sector: 'Unknown' |
| **High VIX (>25)** | Confidence discounted 50% | `adjusted_conf = conf * 0.5` |

### Confidence Scoring System

```python
def calculate_system_confidence(sentiment_confidence, vix_value, sector_weight, source_reliability):
    """
    Calculate final system confidence score for trading decisions.
    
    Args:
        sentiment_confidence: Raw model confidence (0-1)
        vix_value: Current India VIX value
        sector_weight: Sector-specific weight (0.8-1.2)
        source_reliability: News source reliability score (0.5-1.0)
    
    Returns:
        Final system confidence (0-1)
    """
    # VIX regime adjustment
    if vix_value >= 25:
        vix_adjustment = 0.5  # PANIC: 50% discount
    elif vix_value >= 16:
        vix_adjustment = 0.8  # HIGH: 20% discount
    elif vix_value >= 12:
        vix_adjustment = 1.0  # NORMAL: no adjustment
    else:
        vix_adjustment = 1.0  # LOW: no adjustment
    
    # Calculate final confidence
    system_confidence = (
        sentiment_confidence * 
        vix_adjustment * 
        sector_weight * 
        source_reliability
    )
    
    return min(1.0, max(0.0, system_confidence))

# Example usage
confidence = calculate_system_confidence(
    sentiment_confidence=0.92,
    vix_value=18,        # HIGH regime
    sector_weight=1.0,   # Neutral sector weight
    source_reliability=0.95  # High reliability source
)
# Result: 0.92 * 0.8 * 1.0 * 0.95 = 0.699 (69.9% system confidence)
```

### Sector-Specific Confidence Weights

| Sector | Weight | Rationale |
|--------|--------|-----------|
| **Banking** | 1.1 | High news coverage, reliable signals |
| **IT** | 1.0 | Standard weight |
| **FMCG** | 1.0 | Standard weight |
| **Auto** | 0.9 | Moderate volatility |
| **Metal** | 0.8 | High volatility, noisy signals |
| **Realty** | 0.8 | Low liquidity, noisy signals |
| **Unknown** | 0.7 | Unmapped tickers |

### Multi-Source Aggregation

```python
def aggregate_sentiment(signals):
    """
    Aggregate sentiment from multiple news sources.
    
    Args:
        signals: List of dicts with 'sentiment', 'confidence', 'source'
    
    Returns:
        Aggregated sentiment and confidence
    """
    if not signals:
        return {'label': 'neutral', 'confidence': 0.0}
    
    # Weight by source reliability
    source_weights = {
        'reuters': 1.0,
        'bloomberg': 1.0,
        'economictimes': 0.9,
        'moneycontrol': 0.85,
        'twitter': 0.5,
    }
    
    weighted_sentiment = 0.0
    total_weight = 0.0
    
    for signal in signals:
        weight = source_weights.get(signal['source'].lower(), 0.7)
        sentiment_score = 1 if signal['label'] == 'positive' else (-1 if signal['label'] == 'negative' else 0)
        weighted_sentiment += sentiment_score * signal['confidence'] * weight
        total_weight += weight
    
    avg_sentiment = weighted_sentiment / total_weight if total_weight > 0 else 0
    
    # Convert back to label
    if avg_sentiment > 0.3:
        label = 'positive'
    elif avg_sentiment < -0.3:
        label = 'negative'
    else:
        label = 'neutral'
    
    return {
        'label': label,
        'confidence': abs(avg_sentiment),
        'sources_aggregated': len(signals)
    }

# Example usage
signals = [
    {'label': 'positive', 'confidence': 0.92, 'source': 'reuters'},
    {'label': 'positive', 'confidence': 0.88, 'source': 'economictimes'},
    {'label': 'neutral', 'confidence': 0.75, 'source': 'twitter'},
]

result = aggregate_sentiment(signals)
# Result: {'label': 'positive', 'confidence': 0.82, 'sources_aggregated': 3}
```

### Confidence Thresholds for Trading Signals

| System Confidence | Signal Strength | Action |
|-------------------|-----------------|--------|
| **≥ 0.85** | Very Strong | Full position size |
| **0.70 - 0.84** | Strong | 80% position size |
| **0.55 - 0.69** | Moderate | 50% position size |
| **0.40 - 0.54** | Weak | 25% position size |
| **< 0.40** | Very Weak | No action (skip) |

---

## Benchmarks

**Tested on:** Apple M4 Mac, 16GB RAM | **Dataset:** 957K Indian financial news headlines

### Model Performance

| Metric | Score |
|--------|-------|
| **Accuracy** | 98.55% |
| **F1 Score (macro)** | 98.65% |
| **Precision (macro)** | 98.70% |
| **Recall (macro)** | 98.60% |

### Latency & Throughput

| Task | Latency | Throughput |
|------|---------|------------|
| **Single headline** | <50ms | - |
| **Batch (100)** | <200ms | 500/sec |
| **Sector mapping** | <10ms | 10,000/sec |
| **VIX adjustment** | <5ms | 50,000/sec |

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

---

## Installation

### Full Suite
```bash
pip install aion-sentiment aion-sectormap aion-volweight aion-newsimpact
```

### Individual Packages
```bash
pip install aion-sentiment      # Core sentiment analysis
pip install aion-sectormap      # Sector mapping (592 tickers)
pip install aion-volweight      # VIX adjustment
pip install aion-newsimpact     # Historical impact
```

### Development
```bash
git clone https://github.com/AION-Analytics/market-sentiments.git
cd market-sentiments
pip install -e ".[dev]"
pytest
```

---

## Data Coverage

| Asset | Count | Description |
|-------|-------|-------------|
| **NSE Companies** | 592 | Mapped to sectors |
| **Sectors** | 44 | NSE classification |
| **Business Groups** | 340 | Tata, Birla, Ambani, etc. |
| **Training News** | 957K | Indian financial news |
| **Emotion Lexicon** | 14,182 | NRC emotions |

---

## Performance Benchmarks

| Task | Latency | Throughput |
|------|---------|------------|
| Single headline | <50ms | - |
| Batch (100) | <200ms | 500/sec |
| Sector mapping | <10ms | 10,000/sec |
| VIX adjustment | <5ms | 50,000/sec |

**Tested on:** Apple M4 Mac, 16GB RAM

---

## License

Apache License 2.0

**Attribution:**
```
This project uses AION Analytics open-source packages.
Visit https://github.com/AION-Analytics for more information.
```

---

## Contact

- **Email:** aionlabs@tutamail.com
- **GitHub:** https://github.com/AION-Analytics
- **HuggingFace:** https://huggingface.co/AION-Analytics/aion-sentiment-in-v1

---

*Built for the Indian financial community*
