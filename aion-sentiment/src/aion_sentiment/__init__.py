AION Sentiment Analysis - Unified Multi-Task Model v1

Multi-task transformer for Indian financial news:
- Sentiment: negative/neutral/positive (3-class, temperature T=1.5)
- Event classification: 95 Indian market events
- Macro signal: market impact score (-1 to +1)
- Sector impacts: 32 NSE sectors

Trained on 42,214 Indian financial headlines.

Usage:
    from aion_sentiment import AIONUnifiedModel
    model = AIONUnifiedModel.from_pretrained("AION-Analytics/aion-sentiment-unified-v1")
    result = model.predict("RBI cuts repo rate by 25 bps")
    print(result['sentiment'])
    print(result['sector_impacts'])

from .unified_model import AIONUnifiedModel
from .sentiment import SentimentAnalyzer
from .utils import get_device

__all__ = [
    'AIONUnifiedModel',
    'SentimentAnalyzer',
    'get_device',
]

__version__ = '0.2.0'
__author__ = 'AION Open Source Contributors'
__license__ = 'Apache-2.0'
