"""
AION Sentiment Analysis - Unified Multi-Task Model v2

Multi-task transformer for Indian financial news:
- Sentiment: negative/neutral/positive (3-class, temperature T=1.5)
- Event classification: 95 Indian market events
- Macro signal: market impact score (-1 to +1)
- Sector impacts: 32 NSE sectors
- Instrument classification + meta-factor sensitivities (Layer 1-4)
- Event impact engine with 5-factor model

Trained on 42,214 Indian financial headlines.

Usage:
    from aion_sentiment import AIONUnifiedModel
    model = AIONUnifiedModel.from_pretrained("AION-Analytics/aion-sentiment-unified-v1")
    result = model.predict("RBI cuts repo rate by 25 bps")
    print(result['sentiment'])
    print(result['sector_impacts'])

    # Instrument classification + impact analysis
    from aion_sentiment import classify_instrument, get_meta_factors, calculate_impact
    info = classify_instrument("RELIANCE", "EQ", "NSE")
    factors = get_meta_factors(info)
    impact = calculate_impact("RBI_RATE_HIKE", info)
"""

from .unified_model import AIONUnifiedModel
from .sentiment import SentimentAnalyzer
from .utils import get_device

# Instrument classification and meta-factor sensitivities
try:
    from aion_taxonomy.instrument_classifier import (
        classify_instrument,
        get_meta_factors,
    )
except ImportError:
    # aion_taxonomy not installed; provide stubs
    def classify_instrument(*args, **kwargs):
        raise ImportError("aion_taxonomy package required for instrument classification")

    def get_meta_factors(*args, **kwargs):
        raise ImportError("aion_taxonomy package required for meta-factor sensitivities")

# Event impact engine
try:
    from aion_taxonomy.event_impact_engine import (
        calculate_impact,
        rank_instruments_by_impact,
        EVENT_IMPACTS,
    )
except ImportError:
    def calculate_impact(*args, **kwargs):
        raise ImportError("aion_taxonomy package required for event impact calculation")

    def rank_instruments_by_impact(*args, **kwargs):
        raise ImportError("aion_taxonomy package required for instrument ranking")

    EVENT_IMPACTS = {}

__all__ = [
    'AIONUnifiedModel',
    'SentimentAnalyzer',
    'get_device',
    'classify_instrument',
    'get_meta_factors',
    'calculate_impact',
    'rank_instruments_by_impact',
    'EVENT_IMPACTS',
]

__version__ = '0.3.0'
__author__ = 'AION Open Source Contributors'
__license__ = 'Apache-2.0'
