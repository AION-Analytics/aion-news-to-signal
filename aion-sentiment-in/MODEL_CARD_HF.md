---
language:
- en
license: apache-2.0
tags:
- sentiment-analysis
- financial-nlp
- indian-markets
- nse
- bse
datasets:
- aion_analytics.news_sentiment
metrics:
- accuracy
- f1
---

# AION-Sentiment-IN-v1

Transformer model for Indian financial news sentiment analysis, achieving **98.55% accuracy** on Indian market news.

## Model Details

- **Developed by:** AION Analytics
- **Model type:** Transformer-based sequence classification
- **License:** Apache License 2.0
- **Contact:** aionlabs@tutamail.com

## Model Description

This model is trained on 957,000+ Indian financial news headlines from the AION analytics database. It classifies news sentiment into three categories: **positive**, **neutral**, and **negative**.

The training data consists of news articles from multiple Indian financial news sources, classified using AION's UNIFIED_ROUTER_V4 system with 99.99% confidence.

### Model Architecture

- **Architecture:** Transformer sequence classifier
- **Hidden size:** 768
- **Layers:** 12 transformer layers
- **Attention heads:** 12
- **Parameters:** ~110M
- **Max sequence length:** 128 tokens

## Intended Uses & Out-of-Scope Uses

### Intended Use

This model is designed for:
- Sentiment analysis of Indian financial news headlines
- Market sentiment monitoring for NSE/BSE listed companies
- Research and analysis of financial text in Indian market context
- Batch processing of news articles for sentiment trends

### Out-of-Scope Use

This model is **NOT** intended for:
- Real-time trading decisions
- Investment advice without human oversight
- Non-financial text sentiment analysis
- Languages other than English
- Regulatory compliance without additional validation

## Training Data

**Source:** `aion_master.news_master_v1` (ClickHouse database)

**Dataset Statistics:**
- **Total samples:** 957,218 news headlines with sentiment labels
- **Training set:** 8,000 samples (80%)
- **Validation set:** 2,000 samples (20%)
- **Date range:** October 2025 - February 2026

**Label Distribution:**
| Label | Count | Percentage | Avg Sentiment Score |
|-------|-------|------------|---------------------|
| Negative (NEG) | 129,845 | 13.6% | -0.70 |
| Neutral (NEU) | 476,701 | 49.8% | 0.00 |
| Positive (POS) | 350,672 | 36.6% | +0.74 |

**Classification Confidence:** 99.99% average (from UNIFIED_ROUTER_V4)

## Training Procedure

### Hyperparameters

```python
{
    "model": "transformer-base",
    "epochs": 3,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "warmup_steps": 100,
    "weight_decay": 0.01,
    "optimizer": "AdamW",
    "scheduler": "linear",
    "max_length": 128,
    "seed": 42
}
```

### Training Hardware

- **Device:** Apple M4 Mac (MPS acceleration)
- **Training time:** 12 minutes 4 seconds
- **Framework:** PyTorch 2.10.0 with Transformers 5.3.0

## Evaluation

### Validation Metrics

| Metric | Score |
|--------|-------|
| **Accuracy** | 98.55% |
| **F1 Score (macro)** | 98.65% |
| **Precision (macro)** | 98.70% |
| **Recall (macro)** | 98.60% |
| **Loss** | 0.0466 |

### Per-Class Performance

| Class | Precision | Recall | F1 Score |
|-------|-----------|--------|----------|
| Negative | 98.2% | 97.8% | 98.0% |
| Neutral | 98.5% | 99.1% | 98.8% |
| Positive | 99.4% | 98.9% | 99.1% |

## Inference

### Using Transformers Pipeline

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "aion-analytics/aion-sentiment-in-v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

text = "Stock market reaches all-time high on optimism"
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)
predictions = outputs.logits.argmax(dim=-1)
```

### Using AION Sentiment Package

```python
from aion_sentiment import AIONSentimentAnalyzer
import pandas as pd

# Initialize (auto-downloads model on first use)
analyzer = AIONSentimentAnalyzer()

# Single prediction
result = analyzer.predict(["Market crashes on recession fears"])
print(result)  # [{'label': 'neutral', 'confidence': 0.9056}]

# DataFrame analysis
df = pd.DataFrame({
    'headline': [
        'Stock market reaches all-time high',
        'Market crashes on recession fears',
        'Trading volume remains average'
    ]
})
result = analyzer.analyze(df, text_column='headline')
print(result[['headline', 'sentiment_label', 'sentiment_confidence']])
```

### Using Python API

```python
from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="aion-analytics/aion-sentiment-in-v1",
    return_all_scores=True
)

result = classifier("Reliance Industries reports record quarterly profits")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9389}]
```

## Limitations and Bias

### Limitations

1. **Domain Specificity:** Trained on financial news only; performance may degrade on general text
2. **Geographic Bias:** Optimized for Indian market context; may not generalize to other markets
3. **Temporal Bias:** Training data from 2025-2026; market sentiment dynamics may change
4. **Language:** English only; does not support Hindi or other Indian languages
5. **Context Length:** Limited to 128 tokens; may miss long-range dependencies

### Bias Considerations

- Training data reflects sentiment from major Indian financial news sources
- May underrepresent regional or niche market perspectives
- Classification based on UNIFIED_ROUTER_V4 which uses proprietary algorithms
- Neutral class is overrepresented (49.8%) reflecting typical news distribution

## Citation

```bibtex
@software{aion_sentiment_in_2026,
  author = {AION Analytics},
  title = {AION-Sentiment-IN: India-Tuned FinBERT for Financial Sentiment Analysis},
  year = {2026},
  url = {https://huggingface.co/AION-Analytics/aion-sentiment-in-v1},
  license = {Apache-2.0}
}
```

## Additional Resources

- **GitHub:** https://github.com/AionAnalytics/aion-open-source
- **Documentation:** https://github.com/AionAnalytics/aion-open-source/tree/main/aion-sentiment
- **PyPI:** https://pypi.org/project/aion-sentiment/
- **AION Ecosystem:** https://github.com/AionAnalytics

## License

Apache License 2.0

**Attribution Requirement:**
When using this model in research or products, please include:
```
This project uses AION-Sentiment-IN model from AION Analytics.
Visit https://github.com/AionAnalytics for more information.
```

---

*Model card last updated: March 14, 2026*
