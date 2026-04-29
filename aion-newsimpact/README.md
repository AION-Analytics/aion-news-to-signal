# AION NewsImpact

**Historical News Impact Analysis using Semantic Search for the AION Open Source Ecosystem**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Overview

**AION NewsImpact** is a Python package that analyzes the potential market impact of news headlines by finding semantically similar historical headlines and their observed price effects. Using state-of-the-art sentence embeddings and FAISS vector search, it enables fast, accurate similarity matching against historical news data.

### Key Features

- **Semantic Search**: Find historically similar headlines using sentence-transformers embeddings
- **FAISS Index**: Lightning-fast approximate nearest neighbor search at scale
- **Impact Analysis**: Retrieve observed 1-day returns for similar historical headlines
- **Rich Results**: Get similarity scores, dates, tickers, and custom metadata
- **Incremental Updates**: Add new headlines without rebuilding from scratch
- **Type-Safe**: Full type hints for IDE support and static analysis

### How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  New Headline   │────▶│  Sentence        │────▶│  FAISS Index    │
│  "Earnings      │     │  Transformer     │     │  Similarity     │
│   Beat"         │     │  Embedding       │     │  Search         │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Impact Stats   │◀────│  Historical      │◀────│  Top-K Similar  │
│  Avg Return     │     │  Headlines +     │     │  Headlines      │
│  Volatility     │     │  Returns         │     │  + Returns      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Installation

### From PyPI (Recommended)

```bash
pip install aion-newsimpact
```

### From Source

```bash
git clone https://github.com/aion-analytics/aion-newsimpact.git
cd aion-newsimpact
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

---

## Quick Start

```python
import pandas as pd
from aion_newsimpact import NewsImpact

# Prepare historical news data
df = pd.DataFrame({
    'headline': [
        'Company A reports strong quarterly earnings beat',
        'Company B misses revenue expectations',
        'Tech sector rallies on positive economic data',
        'Market volatility increases amid uncertainty',
    ],
    'date': ['2025-01-15', '2025-01-20', '2025-02-01', '2025-02-10'],
    'returns_1d': [0.025, -0.032, 0.018, -0.015],
    'ticker': ['AAPL', 'GOOGL', 'QQQ', 'SPY'],
})

# Initialize NewsImpact (index built automatically)
analyzer = NewsImpact(df, text_column='headline')

# Query for similar historical headlines
results = analyzer.query('Company exceeds profit expectations')

print(f"Found {len(results)} similar headlines")
print(f"Average 1-day return: {results.average_return:.2%}")
print(results.to_dataframe())
```

---

## Usage Examples

### Basic Usage

```python
from aion_newsimpact import NewsImpact
import pandas as pd

# Load historical data
df = pd.read_csv('historical_news.csv')

# Initialize analyzer
analyzer = NewsImpact(
    historical_df=df,
    text_column='headline',
    model_name='sentence-transformers/all-MiniLM-L6-v2'
)

# Query for similar headlines
results = analyzer.query(
    'Federal Reserve announces interest rate decision',
    top_k=5
)

# View results
for i, (headline, date, similarity, ret) in enumerate(
    zip(results.headlines, results.dates, 
        results.similarity_scores, results.returns_1d)
):
    print(f"{i+1}. [{similarity:.2f}] {date}: {headline}")
    print(f"   1-day return: {ret:.2%}")
```

### Getting Impact Statistics

```python
# Get aggregate statistics
stats = analyzer.get_impact_stats()

print(f"Total headlines in index: {stats['total_headlines']}")
print(f"Average 1-day return: {stats['avg_return_1d']:.2%}")
print(f"Return std dev: {stats['std_return_1d']:.2%}")
print(f"Positive impact: {stats['positive_impact_pct']:.1f}%")
print(f"Negative impact: {stats['negative_impact_pct']:.1f}%")
print(f"Date range: {stats['date_range']}")
```

### Adding New Headlines

```python
# New data to add
new_data = pd.DataFrame({
    'headline': ['New headline about market conditions'],
    'date': ['2025-12-01'],
    'returns_1d': [0.012],
    'ticker': ['SPY'],
})

# Add to existing index
analyzer.add_headlines(new_data, rebuild_index=True)

# Or add without rebuilding (call build_index() manually later)
analyzer.add_headlines(new_data, rebuild_index=False)
analyzer.build_index()  # Rebuild when ready
```

### Custom Model

```python
# Use a different sentence-transformers model
analyzer = NewsImpact(
    df,
    text_column='headline',
    model_name='sentence-transformers/all-mpnet-base-v2'  # More accurate, slower
)
```

### Integration with Sentiment Pipeline

```python
from aion_newsimpact import NewsImpact
from aion_volweight import adjust_confidence, get_regime

def analyze_news_impact(headline, current_vix, impact_analyzer):
    """
    Analyze news impact with volatility adjustment.
    
    Args:
        headline: News headline to analyze
        current_vix: Current VIX value
        impact_analyzer: NewsImpact instance
    
    Returns:
        dict with impact analysis results
    """
    # Find similar historical headlines
    results = impact_analyzer.query(headline, top_k=10)
    
    # Get impact statistics
    stats = impact_analyzer.get_impact_stats()
    
    # Adjust confidence based on VIX
    base_confidence = results.average_similarity
    adjusted_confidence = adjust_confidence(base_confidence, current_vix)
    
    return {
        'headline': headline,
        'similar_count': len(results),
        'avg_similarity': results.average_similarity,
        'avg_historical_return': results.average_return,
        'return_volatility': results.return_std,
        'vix_regime': get_regime(current_vix).value,
        'base_confidence': base_confidence,
        'vol_adjusted_confidence': adjusted_confidence,
        'market_context': stats,
    }

# Usage
# analyzer = NewsImpact(historical_df, text_column='headline')
# analysis = analyze_news_impact('New headline', current_vix=18.5, impact_analyzer=analyzer)
```

---

## API Reference

### Classes

#### `NewsImpact`

Main class for historical news impact analysis.

**Constructor:**
```python
NewsImpact(
    historical_df: pd.DataFrame,
    text_column: str = "headline",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
)
```

**Parameters:**
- `historical_df`: DataFrame with historical news data
- `text_column`: Column containing headline text
- `model_name`: Sentence-transformers model for embeddings

**Methods:**

| Method | Description |
|--------|-------------|
| `query(headline, top_k=5)` | Find similar historical headlines |
| `get_impact_stats()` | Get aggregate impact statistics |
| `build_index()` | Rebuild FAISS index |
| `add_headlines(df, rebuild_index=True)` | Add new headlines |
| `get_embedding(text)` | Get embedding vector for text |

---

#### `ImpactQueryResult`

Dataclass containing query results.

**Attributes:**
- `headlines`: List of similar historical headlines
- `dates`: List of dates when headlines occurred
- `similarity_scores`: Cosine similarity scores (0.0 to 1.0)
- `returns_1d`: List of 1-day returns following each headline
- `tickers`: List of associated ticker symbols (if available)
- `metadata`: Additional metadata (if available)

**Properties:**
- `average_return`: Mean 1-day return across results
- `return_std`: Standard deviation of returns
- `average_similarity`: Mean similarity score

**Methods:**
- `to_dataframe()`: Convert to pandas DataFrame
- `__len__()`: Number of results

---

## Data Format

### Required Columns

| Column | Type | Description |
|--------|------|-------------|
| `headline` | str | News headline text |

### Optional Columns

| Column | Type | Description |
|--------|------|-------------|
| `date` | str | Date of headline (YYYY-MM-DD) |
| `returns_1d` | float | 1-day price return after headline |
| `ticker` | str | Associated ticker symbol |

### Additional Columns

Any additional columns will be included in query result metadata.

---

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=aion_newsimpact
```

---

## Data Contribution

We welcome contributions of historical news impact data to improve the ecosystem. Please submit data in the following JSON format:

```json
{
  "headline_hash": "sha256 of headline",
  "headline": "Company reports strong quarterly earnings",
  "sentiment_label": "positive",
  "sentiment_confidence": 0.95,
  "ticker": "RELIANCE",
  "date": "2025-01-15",
  "week": "2025-03",
  "vix_regime": "NORMAL",
  "returns_1d": 0.025,
  "returns_5d": 0.042,
  "sector": "Technology"
}
```

### Contribution Guidelines

1. **Format**: JSON Lines (.jsonl) format preferred for large datasets
2. **Required Fields**: `headline_hash`, `headline`, `date`
3. **Recommended Fields**: `returns_1d`, `ticker`, `sentiment_label`
4. **Privacy**: Ensure no personally identifiable information is included
5. **Quality**: Data should be from reliable sources with proper attribution
6. **License**: Contributions must be compatible with Apache 2.0

### Submitting Data

1. **GitHub**: Create a PR with data files in `data/contributions/`
2. **Email**: Send to data-contributions@aion-analytics.org
3. **Form**: Use the contribution form at aion-analytics.org/contribute

---

## Performance Considerations

### Index Size vs. Speed

| Headlines | Index Build Time | Query Time (top_k=5) | Memory |
|-----------|------------------|----------------------|--------|
| 1,000 | ~2 seconds | ~1 ms | ~2 MB |
| 10,000 | ~15 seconds | ~2 ms | ~15 MB |
| 100,000 | ~2 minutes | ~5 ms | ~150 MB |
| 1,000,000 | ~20 minutes | ~15 ms | ~1.5 GB |

### Model Selection

| Model | Dimensions | Speed | Accuracy | Use Case |
|-------|------------|-------|----------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | Default, general purpose |
| all-mpnet-base-v2 | 768 | Medium | Better | Higher accuracy needs |
| all-MiniLM-L12-v2 | 384 | Medium | Better | Balance of speed/accuracy |

---

## Troubleshooting

### Common Issues

**Issue**: `ImportError: FAISS is required`
**Solution**: `pip install faiss-cpu`

**Issue**: `ImportError: sentence-transformers is required`
**Solution**: `pip install sentence-transformers`

**Issue**: Query returns poor results
**Solution**: 
- Ensure historical data has sufficient examples
- Try a different model (e.g., `all-mpnet-base-v2`)
- Check that headlines are in the same language as the model

**Issue**: Out of memory with large datasets
**Solution**:
- Use a smaller model
- Consider FAISS IVF index for very large datasets
- Process data in batches

---

## License

Copyright 2026 AION Analytics

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

## AION Open Source Ecosystem

This package is part of the AION open-source ecosystem for financial analytics. Explore other AION packages:

- **aion-sentiment**: Core sentiment analysis engine
- **aion-volweight**: VIX-based confidence adjustment
- **aion-newsimpact**: Historical news impact analysis (this package)
- **aion-sectormap**: Sector and industry mapping

Visit [https://github.com/aion-analytics](https://github.com/aion-analytics) for more.

---

## Support

- **Documentation**: https://aion-analytics.org/docs
- **Issues**: https://github.com/aion-analytics/aion-newsimpact/issues
- **Discussions**: https://github.com/aion-analytics/aion-newsimpact/discussions

---

*Built with ❤️ by AION Analytics for the open-source community*
