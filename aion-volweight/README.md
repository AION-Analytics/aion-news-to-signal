# AION VolWeight

**VIX-based Sentiment Confidence Adjustment for the AION Open Source Ecosystem**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Overview

**AION VolWeight** is a Python package that adjusts sentiment confidence scores based on market volatility regimes using the VIX (CBOE Volatility Index). During periods of high market volatility, sentiment analysis becomes less reliable, and this package provides a systematic way to discount confidence scores accordingly.

### Key Features

- **VIX Regime Detection**: Automatically classify market conditions into LOW, NORMAL, HIGH, or PANIC regimes
- **Confidence Multipliers**: Apply appropriate discounts to sentiment confidence based on volatility
- **DataFrame Integration**: Batch process sentiment analysis results with pandas
- **Type-Safe**: Full type hints for IDE support and static analysis
- **Configurable**: Customize regime thresholds and multipliers for your use case

### VIX Regime Classification

| Regime | VIX Range | Multiplier | Discount | Market Condition |
|--------|-----------|------------|----------|------------------|
| **LOW** | VIX < 12 | 1.0 | 0% | Market complacency |
| **NORMAL** | 12 ≤ VIX < 15 | 1.0 | 0% | Typical conditions |
| **HIGH** | 15 ≤ VIX < 25 | 0.8 | 20% | Elevated volatility |
| **PANIC** | VIX ≥ 25 | 0.5 | 50% | Market stress |

---

## Installation

### From PyPI (Recommended)

```bash
pip install aion-volweight
```

### From Source

```bash
git clone https://github.com/aion-analytics/aion-volweight.git
cd aion-volweight
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

---

## Quick Start

```python
from aion_volweight import adjust_confidence, get_regime, get_multiplier

# Get current VIX regime
regime = get_regime(18.5)
print(f"Market regime: {regime}")  # HIGH

# Adjust a single confidence score
original_confidence = 0.95
adjusted = adjust_confidence(original_confidence, vix_value=18.5)
print(f"Adjusted confidence: {adjusted:.2f}")  # 0.76

# Get the multiplier directly
multiplier = get_multiplier(regime)
print(f"Multiplier: {multiplier}")  # 0.8
```

---

## Usage Examples

### Basic Usage

```python
from aion_volweight import adjust_confidence, get_regime_summary

# Example 1: Normal market conditions (no adjustment)
confidence = 0.90
vix = 13.0
adjusted = adjust_confidence(confidence, vix)
print(f"Normal: {confidence} -> {adjusted}")  # 0.90 -> 0.90

# Example 2: High volatility (20% discount)
vix = 20.0
adjusted = adjust_confidence(confidence, vix)
print(f"High: {confidence} -> {adjusted}")  # 0.90 -> 0.72

# Example 3: Panic conditions (50% discount)
vix = 35.0
adjusted = adjust_confidence(confidence, vix)
print(f"Panic: {confidence} -> {adjusted}")  # 0.90 -> 0.45

# Get regime summary
print(get_regime_summary(20.0))
```

### DataFrame Processing

```python
import pandas as pd
from aion_volweight import weight_confidence

# Create sample sentiment analysis results
df = pd.DataFrame({
    'headline': [
        'Company A reports strong quarterly earnings',
        'Market uncertainty grows amid trade tensions',
        'Tech sector shows resilience despite challenges',
    ],
    'sentiment_confidence': [0.95, 0.80, 0.70],
    'sentiment_label': ['positive', 'negative', 'positive'],
})

# Current VIX level
current_vix = 18.5  # HIGH regime

# Adjust all confidence scores
df_adjusted = weight_confidence(df, vix_value=current_vix)

print(df_adjusted)
```

Output:
```
                                            headline  sentiment_confidence  sentiment_label  sentiment_confidence_adjusted
0  Company A reports strong quarterly earnings                    0.95         positive                           0.76
1   Market uncertainty grows amid trade tensions                    0.80         negative                           0.64
2    Tech sector shows resilience despite challenges                    0.70         positive                           0.56
```

### Custom Configuration

```python
from aion_volweight import VIXRegimeConfig, adjust_confidence, get_regime

# Create custom regime configuration
custom_config = VIXRegimeConfig(
    low_threshold=10.0,      # Lower threshold for LOW regime
    normal_threshold=18.0,   # Extended NORMAL regime
    high_threshold=30.0,     # Higher threshold for HIGH regime
    high_multiplier=0.7,     # 30% discount in HIGH regime
    panic_multiplier=0.4,    # 60% discount in PANIC regime
)

# Use custom config
regime = get_regime(20.0, config=custom_config)  # Still NORMAL with custom thresholds
confidence = adjust_confidence(0.90, vix_value=25.0, config=custom_config)
```

### Integration with Sentiment Analysis Pipeline

```python
from aion_volweight import weight_confidence
import pandas as pd

def process_sentiment_with_volatility(sentiment_df, current_vix):
    """
    Process sentiment analysis results with volatility adjustment.
    
    Args:
        sentiment_df: DataFrame with sentiment analysis results
        current_vix: Current VIX index value
    
    Returns:
        DataFrame with volatility-adjusted confidence scores
    """
    # Adjust confidence based on VIX
    adjusted_df = weight_confidence(
        sentiment_df,
        vix_value=current_vix,
        confidence_col='sentiment_confidence',
        output_col='vol_adjusted_confidence'
    )
    
    # Add regime information
    from aion_volweight import get_regime
    adjusted_df['vix_regime'] = get_regime(current_vix).value
    
    return adjusted_df

# Usage
# sentiment_results = run_sentiment_analysis(news_headlines)
# adjusted_results = process_sentiment_with_volatility(sentiment_results, current_vix=18.5)
```

---

## API Reference

### Functions

#### `get_regime(vix_value: float, config: VIXRegimeConfig | None = None) -> VIXRegime`

Determine the VIX regime for a given VIX value.

**Parameters:**
- `vix_value`: The VIX index value (must be non-negative)
- `config`: Optional custom configuration

**Returns:** VIXRegime enum (LOW, NORMAL, HIGH, or PANIC)

**Raises:**
- `ValueError`: If vix_value is negative
- `TypeError`: If vix_value is not a number

---

#### `get_multiplier(regime: VIXRegime | str, config: VIXRegimeConfig | None = None) -> float`

Get the confidence multiplier for a VIX regime.

**Parameters:**
- `regime`: The VIX regime (VIXRegime enum or string)
- `config`: Optional custom configuration

**Returns:** Confidence multiplier (0.0 to 1.0)

**Raises:**
- `ValueError`: If regime is invalid
- `TypeError`: If regime is not VIXRegime or string

---

#### `adjust_confidence(confidence: float, vix_value: float, config: VIXRegimeConfig | None = None) -> float`

Adjust a sentiment confidence score based on VIX volatility.

**Parameters:**
- `confidence`: Original confidence score (0.0 to 1.0)
- `vix_value`: Current VIX index value
- `config`: Optional custom configuration

**Returns:** Adjusted confidence score (0.0 to 1.0)

**Raises:**
- `ValueError`: If confidence is outside [0.0, 1.0] or vix_value is negative
- `TypeError`: If inputs are not numbers

---

#### `weight_confidence(df: pd.DataFrame, vix_value: float, confidence_col: str = 'sentiment_confidence', output_col: str | None = None, config: VIXRegimeConfig | None = None) -> pd.DataFrame`

Adjust sentiment confidence scores in a DataFrame based on VIX volatility.

**Parameters:**
- `df`: DataFrame containing sentiment confidence scores
- `vix_value`: Current VIX index value
- `confidence_col`: Name of column with original confidence scores
- `output_col`: Name for adjusted column (default: '{confidence_col}_adjusted')
- `config`: Optional custom configuration

**Returns:** DataFrame with additional adjusted confidence column

**Raises:**
- `ValueError`: If confidence_col not found or contains invalid values
- `TypeError`: If inputs are of incorrect types

---

#### `get_regime_summary(vix_value: float) -> str`

Get a human-readable summary of the current VIX regime.

**Parameters:**
- `vix_value`: Current VIX index value

**Returns:** Formatted string describing the regime

---

### Classes

#### `VIXRegime` (Enum)

VIX volatility regime classification.

**Values:**
- `LOW`: VIX < 12
- `NORMAL`: 12 ≤ VIX < 15
- `HIGH`: 15 ≤ VIX < 25
- `PANIC`: VIX ≥ 25

---

#### `VIXRegimeConfig` (dataclass)

Configuration for VIX regime thresholds and confidence multipliers.

**Attributes:**
- `low_threshold`: Upper bound for LOW regime (default: 12.0)
- `normal_threshold`: Upper bound for NORMAL regime (default: 15.0)
- `high_threshold`: Upper bound for HIGH regime (default: 25.0)
- `low_multiplier`: Confidence multiplier for LOW (default: 1.0)
- `normal_multiplier`: Confidence multiplier for NORMAL (default: 1.0)
- `high_multiplier`: Confidence multiplier for HIGH (default: 0.8)
- `panic_multiplier`: Confidence multiplier for PANIC (default: 0.5)

---

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=aion_volweight
```

---

## Data Contribution

We welcome contributions of historical VIX and sentiment data to improve regime calibration. Please submit data in the following JSON format:

```json
{
  "headline_hash": "sha256 of headline",
  "sentiment_label": "positive",
  "sentiment_confidence": 0.95,
  "ticker": "RELIANCE",
  "week": "2025-12",
  "vix_regime": "NORMAL",
  "actual_price_impact": 0.023
}
```

### Contribution Guidelines

1. **Format**: JSON Lines (.jsonl) format preferred for large datasets
2. **Fields**: All fields above are required except `actual_price_impact`
3. **Privacy**: Ensure no personally identifiable information is included
4. **Quality**: Data should be from reliable sources with proper attribution

Submit contributions via GitHub Issues or email: data-contributions@aion-analytics.org

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
- **aion-volweight**: VIX-based confidence adjustment (this package)
- **aion-newsimpact**: Historical news impact analysis
- **aion-sectormap**: Sector and industry mapping

Visit [https://github.com/aion-analytics](https://github.com/aion-analytics) for more.

---

## Support

- **Documentation**: https://aion-analytics.org/docs
- **Issues**: https://github.com/aion-analytics/aion-volweight/issues
- **Discussions**: https://github.com/aion-analytics/aion-volweight/discussions

---

*Built with ❤️ by AION Analytics for the open-source community*
