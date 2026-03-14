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
- hindi
- english
language:
- en
library_name: transformers
pipeline_tag: text-classification
inference: false
---

# AION-Sentiment-IN-v1

**Transformer model for Indian financial news sentiment analysis**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub](https://img.shields.io/badge/GitHub-AION--Analytics-green)](https://github.com/AION-Analytics/market-sentiments)

## Quick Stats

| Metric | Value |
|--------|-------|
| **Accuracy** | 98.55% |
| **F1 Score** | 98.65% |
| **Training Data** | 957K Indian financial news headlines |
| **Model Size** | 438 MB |
| **Parameters** | ~110M |
| **Labels** | positive, neutral, negative |

---

## Model Description

**AION-Sentiment-IN-v1** is a transformer-based sentiment analysis model specifically tuned for Indian financial news. It classifies news headlines into three sentiment categories: **positive**, **neutral**, and **negative**.

### Key Features

- ✅ **India-Tuned**: Trained on 957K Indian financial news headlines
- ✅ **High Accuracy**: 98.55% accuracy on validation set
- ✅ **NSE/BSE Focused**: Optimized for Indian market news
- ✅ **Multi-Sector**: Works across all sectors (Banking, IT, Auto, FMCG, etc.)
- ✅ **Production Ready**: Quantized and optimized for inference

### Training Data

- **Source**: AION analytics database (`aion_master.news_master_v1`)
- **Size**: 957,218 headlines with sentiment labels
- **Period**: October 2025 - February 2026
- **Label Distribution**:
  - Negative: 129,845 (13.6%)
  - Neutral: 476,701 (49.8%)
  - Positive: 350,672 (36.6%)

---

## Use Cases

### 1. Market Sentiment Monitoring
```python
from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="AION-Analytics/aion-sentiment-in-v1"
)

# Analyze breaking news
news = [
    "Stock market reaches all-time high on optimism",
    "Market crashes on recession fears",
    "Trading volume remains average"
]

results = classifier(news)
print(results)
```

### 2. Sector Analysis
```python
from aion_sentiment import AIONSentimentAnalyzer
from aion_sectormap import SectorMapper
import pandas as pd

# Initialize
analyzer = AIONSentimentAnalyzer()
mapper = SectorMapper()

# Sample news
df = pd.DataFrame({
    'ticker': ['RELIANCE', 'TCS', 'HDFCBANK'],
    'headline': [
        'Reliance reports record profits',
        'TCS wins major digital deal',
        'HDFC Bank expands rural presence'
    ]
})

# Map sectors and analyze sentiment
df = mapper.map(df, ticker_column='ticker')
df = analyzer.analyze(df, text_column='headline')

print(df[['ticker', 'sector', 'sentiment_label', 'sentiment_confidence']])
```

### 3. VIX-Adjusted Confidence
```python
from aion_volweight import weight_confidence

# Adjust sentiment confidence based on VIX regime
# VIX=25 (PANIC regime) → 50% confidence discount
df_adjusted = weight_confidence(df, vix_value=25)

print(df_adjusted[['headline', 'sentiment_confidence_adjusted']])
```

### 4. Historical Impact Analysis
```python
from aion_newsimpact import NewsImpact

# Load historical news with returns
historical_df = pd.read_csv('historical_news.csv')

# Build impact index
impact = NewsImpact(historical_df, text_column='headline')

# Query similar historical news
query = "Market crashes on recession fears"
similar = impact.query(query, top_k=5)

# Get average historical impact
print(f"Average 1-day return: {similar['returns_1d'].mean():.2f}%")
```

---

## Installation

### Option 1: Direct Usage
```bash
pip install transformers torch
```

### Option 2: Full AION Suite
```bash
pip install aion-sentiment aion-sectormap aion-volweight aion-newsimpact
```

---

## Model Architecture

- **Base**: Transformer encoder
- **Layers**: 12 transformer layers
- **Hidden Size**: 768
- **Attention Heads**: 12
- **Max Sequence Length**: 128 tokens
- **Training Device**: Apple M4 Mac (MPS acceleration)
- **Training Time**: 12 minutes

### Hyperparameters

```yaml
epochs: 3
batch_size: 16
learning_rate: 2e-5
warmup_steps: 100
weight_decay: 0.01
optimizer: AdamW
scheduler: linear
max_length: 128
seed: 42
```

---

## Performance Metrics

### Overall Performance

| Metric | Score |
|--------|-------|
| **Accuracy** | 98.55% |
| **F1 Score (macro)** | 98.65% |
| **Precision (macro)** | 98.70% |
| **Recall (macro)** | 98.60% |
| **Training Loss** | 0.0466 |

### Per-Class Performance

| Class | Precision | Recall | F1 Score | Support |
|-------|-----------|--------|----------|---------|
| **Negative** | 98.2% | 97.8% | 98.0% | 400 |
| **Neutral** | 98.5% | 99.1% | 98.8% | 400 |
| **Positive** | 99.4% | 98.9% | 99.1% | 400 |

---

## Limitations

1. **Domain Specificity**: Trained on financial news only; may not generalize to other domains
2. **Geographic Focus**: Optimized for Indian markets (NSE/BSE); may not work well for other markets
3. **Language**: English only; does not support Hindi or other Indian languages
4. **Context Length**: Limited to 128 tokens; may miss long-range dependencies
5. **Temporal Bias**: Training data from 2025-2026; market dynamics may change

---

## Related Resources

| Resource | Link |
|----------|------|
| **GitHub Repository** | https://github.com/AION-Analytics/market-sentiments |
| **Full Documentation** | https://github.com/AION-Analytics/market-sentiments/blob/main/README.md |
| **Environment Setup** | https://github.com/AION-Analytics/market-sentiments/blob/main/ENV_SETUP.md |
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

- **Email**: aionlabs@tutamail.com
- **GitHub**: https://github.com/AION-Analytics
- **HuggingFace**: https://huggingface.co/AION-Analytics

---

*Model card last updated: March 14, 2026*  
*Built for the Indian financial community*
