# AION Open-Source Ecosystem

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive open-source suite for Indian financial market sentiment analysis, sector mapping, and news impact analytics.

---

## 📦 Packages

| Package | Description | PyPI | Docs |
|---------|-------------|------|------|
| **aion-sentiment** | Sentiment + Emotion analysis for financial headlines | Coming Soon | [Docs](aion-sentiment/README.md) |
| **aion-sentiment-in** | Training pipeline for India-tuned model | Coming Soon | [Docs](aion-sentiment-in/README.md) |
| **aion-sectormap** | NSE ticker → Sector/Industry/Group mapping | Coming Soon | [Docs](aion-sectormap/README.md) |
| **aion-volweight** | VIX-based sentiment confidence adjustment | Coming Soon | [Docs](aion-volweight/README.md) |
| **aion-newsimpact** | Historical news impact analysis with FAISS | Coming Soon | [Docs](aion-newsimpact/README.md) |

---

## 🚀 Quick Start

### Installation

```bash
# Install individual packages
pip install aion-sentiment
pip install aion-sectormap
pip install aion-volweight
pip install aion-newsimpact

# Or install all
pip install aion-sentiment aion-sectormap aion-volweight aion-newsimpact
```

### End-to-End Example

```python
import pandas as pd
from aion_sentiment import AIONSentimentAnalyzer
from aion_sectormap import SectorMapper
from aion_volweight import weight_confidence

# Sample data
df = pd.DataFrame({
    'ticker': ['RELIANCE', 'TCS', 'HDFCBANK'],
    'headline': [
        'Reliance reports record profits',
        'TCS wins major deal',
        'HDFC Bank expands presence'
    ]
})

# 1. Map sectors
mapper = SectorMapper()
df = mapper.map(df, ticker_column='ticker')

# 2. Analyze sentiment
analyzer = AIONSentimentAnalyzer()
df = analyzer.analyze(df, text_column='headline')

# 3. Adjust for VIX (assuming VIX=18 - HIGH regime)
df = weight_confidence(df, vix_value=18)

print(df[['ticker', 'sector', 'sentiment_label', 'sentiment_confidence_adjusted']])
```

---

## 📊 Data Assets

- **NSE Sector Constituents**: 188 companies across 14 sectors
- **NSE Group Companies**: 591 companies, 44 sectors, 340 groups (from GIN database)
- **NRC Emotion Lexicon**: 14,182 words bundled with aion-sentiment

## 🤖 Models

| Model | Description | Accuracy | Location |
|-------|-------------|----------|----------|
| **AION-Sentiment-IN-v1** | Transformer model tuned on Indian financial news | 98.55% | [HuggingFace](https://huggingface.co/aion-analytics/aion-sentiment-in-v1) |

**Note:** The `aion-sentiment` package automatically downloads the India-tuned model from HuggingFace on first use. Users can override with any other model via the `model_name` parameter.

---

## 🔧 Development

```bash
# Clone repository
git clone https://github.com/AionAnalytics/aion-open-source.git
cd aion-open-source

# Install with dev dependencies
cd aion-sentiment && pip install -e ".[dev]"
cd ../aion-sectormap && pip install -e ".[dev]"
cd ../aion-volweight && pip install -e ".[dev]"
cd ../aion-newsimpact && pip install -e ".[dev]"

# Run tests
pytest
```

---

## 📋 License

All packages are licensed under the [Apache License 2.0](LICENSE).

**Attribution Requirement:**
When using these packages in your research or products, please include:
```
This project uses AION Analytics open-source packages.
Visit https://github.com/AionAnalytics for more information.
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Contact

- **Email**: aionlabs@tutamail.com
- **GitHub**: [@AionAnalytics](https://github.com/AionAnalytics)

---

## 🙏 Acknowledgments

- **NRC Emotion Lexicon** - Emotion analysis dataset (NRC Canada)
- **FAISS** (Meta) - Similarity search engine
- **Sentence Transformers** - Text embeddings
- **HuggingFace Transformers** - Model infrastructure

---

*Built with ❤️ for the Indian financial community*
# Verification - No FinBERT References
