# AION Unified Sentiment Model

Multi-task transformer for Indian financial news analysis. Predicts sentiment, event classification, macro signal, and sector impacts from a single headline.

- Model: https://huggingface.co/AION-Analytics/aion-sentiment-unified-v1
- Dataset: https://huggingface.co/datasets/AION-Analytics/indian_financial_news_42k
- PyPI: https://pypi.org/project/aion-sentiment/0.2.0/

## What It Does

- Sentiment: negative / neutral / positive (temperature-calibrated with T=1.5)
- Event classification: 95 Indian market events (RBI rate change, corporate earnings, geopolitical, etc.)
- Macro signal: overall market impact score from -1 to +1
- Sector impacts: 32 NSE sector scores with bias propagation (e.g. rupee appreciation = negative for IT, positive for Aviation)

## Quick Start

```bash
pip install aion-sentiment
```

```python
from aion_sentiment import AIONUnifiedModel

model = AIONUnifiedModel.from_pretrained("AION-Analytics/aion-sentiment-unified-v1")

result = model.predict("RBI cuts repo rate by 25 bps to boost growth")
print(result['sentiment'])             # positive
print(result['sentiment_confidence'])  # 0.89
print(result['macro_signal'])          # +0.53

# Sector impacts (32 sectors)
print(result['sector_impacts']['Banks'])      # positive
print(result['sector_impacts']['Realty'])     # positive
```

## Model Details

- Base: distilbert-base-uncased, 67M parameters, 270MB
- Trained on 42,214 Indian financial headlines (2024-2026)
- Sentiment accuracy: 97.2%
- Event classification accuracy: 99.5%
- Macro signal correlation: 0.990

## Sector Bias Rules

The model learns from taxonomy context rules that define how each event affects sectors:

Inverse bias (sector moves opposite to macro signal): IT, Healthcare
Aligned bias (sector moves with macro signal): Oil, Aviation, Metals, Consumer Durables, Capital Goods, Chemicals

## License

Apache 2.0
