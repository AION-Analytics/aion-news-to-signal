# AION Sentiment Analysis

[![Python Versions](https://img.shields.io/pypi/pyversions/aion-sentiment-in.svg)](https://pypi.org/project/aion-sentiment-in/)
[![License](https://img.shields.io/pypi/l/aion-sentiment-in.svg)](https://github.com/aion/aion-sentiment-in/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/aion-sentiment-in.svg)](https://pypi.org/project/aion-sentiment-in/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-aion--analytics-yellow)](https://huggingface.co/AION-Analytics/aion-sentiment-in-v1)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**AION Sentiment Analysis** is an open-source Python package for analyzing sentiment and emotions in financial news text. Part of the [AION open-source ecosystem](https://github.com/aion), it provides pre-trained models and emotion analysis tools for financial NLP applications.

## Overview

AION-Sentiment-IN provides:

- **Sentiment Classification**: Classify financial news as negative, neutral, or positive
- **Emotion Analysis**: Fine-grained emotion detection across 8 categories (anger, fear, joy, sadness, trust, disgust, surprise, anticipation)
- **HuggingFace Integration**: Load models directly from HuggingFace Hub
- **Local Fallback**: Support for offline development with local model paths
- **Batch Processing**: Efficient processing of multiple texts
- **Type-Safe API**: Comprehensive type hints and error handling

## Installation

### From PyPI (Recommended)

```bash
pip install aion-sentiment-in
```

### From Source (Development)

```bash
git clone https://github.com/aion/aion-sentiment-in.git
cd aion-sentiment-in
pip install -e ".[dev]"
```

### Requirements

- Python 3.9+
- PyTorch 2.0+
- Transformers 4.35+

## Quick Start

```python
from aion_sentiment import AIONSentimentIN, EmotionAnalyzer

# Initialize sentiment model (loads from HuggingFace by default)
model = AIONSentimentIN()

# Predict sentiment
result = model.predict("AAPL stock soars on earnings beat")
print(f"Sentiment: {result['sentiment_label']}")  # positive
print(f"Confidence: {result['confidence']:.2%}")  # 95.23%
print(f"Emotions: {result['emotion_scores']}")    # {'joy': 0.8, ...}

# Initialize emotion analyzer
analyzer = EmotionAnalyzer()
emotion_result = analyzer.analyze("Market crashes amid uncertainty")
print(f"Dominant emotion: {emotion_result.dominant_emotion}")  # fear
```

## API Reference

### AIONSentimentIN

The main class for sentiment prediction.

#### Constructor

```python
AIONSentimentIN(
    model_name_or_path: str = "aion-analytics/aion-sentiment-in-v1",
    local_path: Optional[str] = None
)
```

**Parameters:**
- `model_name_or_path` (str): HuggingFace model identifier or local path. Defaults to the official AION model.
- `local_path` (Optional[str]): Local path for model files. Used for development/offline mode.

#### Methods

##### `predict(text: str) -> dict`

Predict sentiment for a single text.

**Parameters:**
- `text` (str): Input text to analyze.

**Returns:**
```python
{
    "sentiment_label": "positive",  # negative, neutral, or positive
    "confidence": 0.95,             # confidence score (0.0-1.0)
    "emotion_scores": {...},        # emotion scores for 8 categories
    "all_scores": {                 # raw scores for all classes
        "negative": 0.02,
        "neutral": 0.03,
        "positive": 0.95
    }
}
```

**Example:**
```python
model = AIONSentimentIN()
result = model.predict("Stock market reaches new highs")
print(result["sentiment_label"])  # positive
```

##### `predict_batch(texts: list) -> list`

Predict sentiment for multiple texts.

**Parameters:**
- `texts` (list): List of input texts.

**Returns:**
- List of prediction dictionaries (same structure as `predict()`).

**Example:**
```python
texts = ["Stock rises", "Market falls", "Fed announces rates"]
results = model.predict_batch(texts)
for text, result in zip(texts, results):
    print(f"{text}: {result['sentiment_label']}")
```

---

### EmotionAnalyzer

Class for fine-grained emotion analysis using the NRC Emotion Lexicon.

#### Constructor

```python
EmotionAnalyzer(lexicon: Optional[dict] = None)
```

**Parameters:**
- `lexicon` (Optional[dict]): Pre-loaded lexicon. Auto-downloads if not provided.

#### Methods

##### `analyze(text: str) -> EmotionResult`

Analyze emotions in text.

**Parameters:**
- `text` (str): Input text to analyze.

**Returns:**
- `EmotionResult` object with:
  - `text`: Original input
  - `emotions`: Dict of emotion scores
  - `dominant_emotion`: Highest-scoring emotion
  - `dominant_score`: Score of dominant emotion
  - `word_count`: Number of words analyzed
  - `matched_words`: Words matched in lexicon

**Example:**
```python
analyzer = EmotionAnalyzer()
result = analyzer.analyze("Market crashes dramatically")
print(f"Dominant: {result.dominant_emotion}")  # fear
print(f"Scores: {result.emotions}")            # {'fear': 0.8, ...}
```

##### `analyze_batch(texts: list) -> list`

Analyze emotions for multiple texts.

**Parameters:**
- `texts` (list): List of input texts.

**Returns:**
- List of `EmotionResult` objects.

---

## Emotion Categories

The NRC Emotion Lexicon supports eight primary emotions:

| Emotion | Description | Example Triggers |
|---------|-------------|------------------|
| **anger** | Hostility, irritation, rage | "crash", "fraud", "scandal" |
| **fear** | Anxiety, worry, apprehension | "crisis", "risk", "uncertainty" |
| **joy** | Happiness, delight, pleasure | "soars", "beat", "record" |
| **sadness** | Sorrow, grief, unhappiness | "loss", "decline", "failure" |
| **trust** | Acceptance, confidence, reliance | "stable", "reliable", "growth" |
| **disgust** | Revulsion, contempt, aversion | "corrupt", "manipulation" |
| **surprise** | Astonishment, unexpectedness | "shock", "unexpected", "sudden" |
| **anticipation** | Expectation, looking forward | "expected", "forecast", "outlook" |

## Development Installation

```bash
# Clone repository
git clone https://github.com/aion/aion-sentiment-in.git
cd aion-sentiment-in

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aion_sentiment --cov-report=html

# Run specific test file
pytest tests/test_model.py
```

## Attribution Requirement

When using AION-Sentiment-IN in your projects, please include the following attribution in your documentation:

> This product includes software developed by the AION Project (https://github.com/aion).

For academic publications, please cite:

```bibtex
@software{aion_sentiment_2026,
  title = {AION Sentiment Analysis},
  author = {{AION Contributors}},
  year = {2026},
  url = {https://github.com/aion/aion-sentiment-in},
  license = {Apache-2.0}
}
```

## Colab Notebook

Try AION-Sentiment-IN in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/aion/aion-sentiment-in/blob/main/demo.py)

*(Note: Colab notebook link is a placeholder - update when available)*

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).

```
Copyright 2026 AION Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Code style requirements
- Pull request process
- Issue reporting guidelines
- Development setup

## Disclaimer

**This software is provided for research and educational purposes only.** 

- Not intended for trading or investment decisions
- No warranty or guarantee of accuracy
- Users assume all risks associated with use
- Consult financial professionals for investment advice

## Links

- [GitHub Repository](https://github.com/aion/aion-sentiment-in)
- [Issue Tracker](https://github.com/aion/aion-sentiment-in/issues)
- [HuggingFace Model](https://huggingface.co/AION-Analytics/aion-sentiment-in-v1)
- [AION Organization](https://github.com/aion)
- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
