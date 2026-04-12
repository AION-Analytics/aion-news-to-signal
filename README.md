AION Market Sentiment - Indian Financial News Sentiment Analysis

AI-powered sentiment intelligence for Indian financial markets

86.67% accuracy (ties with FinBERT) | <100ms latency | Open Source | Apache 2.0 License

--------------------------------------------------------------------

AION-Sentiment-IN-v3 is an open-source Indian financial news sentiment model with taxonomy-driven market logic and sector-aware signal integration.

--------------------------------------------------------------------

NEW IN VERSION 3.0: MARKET INTELLIGENCE LAYER

A complete 4-factor market intelligence engine has been added to AION-Sentiment.
This system provides real-time event impact analysis by modeling sector sensitivities to:

- Interest Rates (10-year G-Sec yield)
- Crude Oil (WTI futures)
- Rupee/USD (exchange rate)
- Risk Sentiment (India VIX)

WHAT YOU CAN NOW BUILD:

- Event Impact Engine: Calculate how any event affects any instrument
- Instrument Classifier: Classify equity, derivatives, commodities, bonds into sectors
- Sector Sensitivity Dashboard: 90-day rolling correlations for 14 NIFTY sectors
- Portfolio Risk Analysis: Rank instruments by sensitivity to macro factors
- Automated Data Pipeline: Weekly refresh of sector sensitivities from live markets

from aion_taxonomy.event_impact_engine import rank_instruments_by_impact

# Define your portfolio
instruments = [
    {"tradingsymbol": "RELIANCE", "segment": "EQ", "exchange": "NSE"},
    {"tradingsymbol": "HDFCBANK", "segment": "EQ", "exchange": "NSE"},
]

# Get ranked impact for an event
ranked = rank_instruments_by_impact("RBI_RATE_HIKE", instruments)
print(ranked)

See aion_taxonomy/README.md for full documentation.

--------------------------------------------------------------------

WHAT YOU CAN BUILD WITH IT

- Financial news sentiment dashboards
- Sector impact analysis tools
- Market monitoring systems
- Research pipelines
- AI agents for financial news analysis
- Event-driven market intelligence platforms

--------------------------------------------------------------------

INSTALLATION

pip install aion-sentiment

--------------------------------------------------------------------

QUICK START

from aion_sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer()

result = analyzer.predict("RBI hikes repo rate by 25 bps")
print(result)

Output:
{'label': 'negative', 'confidence': 0.92}

Time to first result: under 2 minutes.

--------------------------------------------------------------------

BENCHMARK COMPARISON

Test set: 45 manually labeled Indian financial news headlines (15 per class)

Model                    Accuracy    F1 Score
AION-Sentiment-IN-v3     86.67%      0.865
FinBERT (ProsusAI)       86.67%      0.865
RoBERTa (cardiffnlp)     73.33%      0.725

AION ties with FinBERT on pure sentiment accuracy.

Both significantly outperform RoBERTa, proving the value of financial domain specialization.

AION's real advantage is the India-specific taxonomy, sector-aware signal flips, and production pipeline.

--------------------------------------------------------------------

WHY AION INSTEAD OF FINBERT

Feature                  AION        FinBERT
Indian market tuned      YES         NO
Taxonomy events          YES         NO
Sector-aware signals     YES         NO
Production pipeline      YES         LIMITED
Open source platform     YES         LIMITED
Extensible by community  YES         NO

--------------------------------------------------------------------

THE KEY DIFFERENTIATOR: SECTOR-AWARE SIGNAL FLIPS

The same event can have opposite impacts on different sectors.

Example: Rupee falls to all-time low against dollar

Overall sentiment: NEGATIVE

Sector-specific signals:
- IT Services: POSITIVE (export revenue increases in INR terms)
- Pharma: POSITIVE (global competitiveness improves)
- Aviation: NEGATIVE (fuel becomes expensive in USD)
- Oil & Gas: NEGATIVE (import bill rises)
- Banks: NEGATIVE (FII outflow pressure)

Most models stop at "negative". AION continues to sector-level impact.

--------------------------------------------------------------------

LIGHTWEIGHT ARCHITECTURE

- No heavy NLP frameworks required (no spaCy, no NLTK)
- Minimal inference stack: transformers + torch only
- Production-friendly deployment
- Fast inference (CPU / MPS / CUDA)
- Model size: 268 MB

--------------------------------------------------------------------

MODEL DETAILS

Developer: AION Analytics
Architecture: 6-layer transformer encoder, 768 hidden, 12 attention heads
Classification Head: pre_classifier (768x768) + classifier (3x768)
Parameters: ~67M
Model Size: 268 MB (safetensors)
Input: Text (financial news headlines)
Output: Sentiment label (negative/neutral/positive) + confidence
License: Apache License 2.0

--------------------------------------------------------------------

TRAINING DATA

Source: Proprietary Indian financial news corpus
Size: 1,029,611 headlines (823,688 train / 205,923 validation)
Period: 2024-01-01 to 2026-03-31

Label distribution:
- Negative: 139,385 (13.5%)
- Neutral: 305,131 (29.7%)
- Positive: 379,172 (36.8%)

--------------------------------------------------------------------

HOW THE TRAINING DATA WAS GENERATED

Primary - Taxonomy-corrected labels:

Headlines matching any of the 136 taxonomy events (e.g., macro_rbi_repo_hike) were assigned the event's default_sentiment. This ensures labels align with deterministic market logic.

Fallback - VADER:

Headlines that did not match any taxonomy event were labeled using VADER's compound score thresholds (positive >= 0.05, negative <= -0.05, else neutral). This maintains dataset size while preserving quality for event-driven headlines.

Result: ~13,000+ high-quality, taxonomy-corrected headlines + broader coverage from VADER.

--------------------------------------------------------------------

WHAT THE 98.55% ACCURACY MEANS

- Taxonomy-labeled headlines achieve near-perfect accuracy
- VADER-labeled headlines have lower but still strong accuracy
- The model learns patterns consistent with Indian financial news, especially for critical market events
- It does NOT measure universal sentiment understanding
- It does NOT measure performance on non-Indian markets
- It does NOT measure market movement prediction

--------------------------------------------------------------------

OPEN TAXONOMY PLATFORM

The taxonomy is community-extensible. Contribute new:

- Market events (e.g., new sector policies, global macro)
- Sectors and industry mappings
- Regional market adaptations
- Contextual modifiers

This turns AION into a platform, not just a model.

--------------------------------------------------------------------

AION PLATFORM COMPONENTS

Component              Purpose
Sentiment Model        Headline sentiment classification (this model)
Taxonomy Engine        Event detection (136 India-specific events)
Sector Map             NSE ticker to sector mapping
VIX Weighting          Confidence adjustment based on India VIX
Event Impact Engine    Event impact calculation for any instrument (NEW)
Instrument Classifier  Classify instruments into asset class and sector (NEW)
Meta-Factor Analysis   90-day rolling sector-factor correlations (NEW)

Use each component independently or combine them for a complete solution.

--------------------------------------------------------------------

WHO SHOULD USE THIS

- AI developers building financial applications
- Quant researchers exploring Indian market sentiment
- Financial engineers creating monitoring tools
- Market intelligence builders
- Data scientists in financial institutions
- Open-source contributors expanding the taxonomy

--------------------------------------------------------------------

LIMITATIONS

1. Label quality: Taxonomy labels are high-quality; VADER-fallback labels introduce noise
2. Overconfidence: Softmax outputs often saturate; use confidence as relative indicator
3. Domain specificity: Works best on Indian financial English news
4. No market prediction: Sentiment is not a direct predictor of price movements
5. Not for high-frequency trading: Intended for research, monitoring, and analysis

--------------------------------------------------------------------

PRODUCTION USAGE

For real-time enrichment with taxonomy:

from aion_sentiment import SentimentAnalyzer
from aion_taxonomy import TaxonomyPipeline

sentiment = SentimentAnalyzer()
taxonomy = TaxonomyPipeline()

headline = "Rupee falls to all-time low against dollar"
sentiment_result = sentiment.predict(headline)
taxonomy_result = taxonomy.process(headline)

print(sentiment_result)
print(taxonomy_result)

For event impact analysis:

from aion_taxonomy.event_impact_engine import rank_instruments_by_impact, classify_instrument, get_meta_factors

# Classify an instrument and get its meta-factor sensitivities
info = classify_instrument("RELIANCE", "EQ", "NSE")
factors = get_meta_factors(info)
# {'interest_rate': -0.0571, 'crude_oil': 0.0308, 'rupee': -0.2281, 'risk_sentiment': -0.4107}

# Rank multiple instruments by event impact
instruments = [
    {"tradingsymbol": "RELIANCE", "segment": "EQ", "exchange": "NSE"},
    {"tradingsymbol": "HDFCBANK", "segment": "EQ", "exchange": "NSE"},
    {"tradingsymbol": "TCS", "segment": "EQ", "exchange": "NSE"},
]
ranked = rank_instruments_by_impact("RBI_RATE_HIKE", instruments)

--------------------------------------------------------------------

CONTRIBUTING

We welcome contributions to the taxonomy, sectors, and new events.

How to help:
- Add missing keywords for uncovered events (list in no_match_events.txt)
- Propose new sectors or event types
- Improve calibration with new backfill data

See CONTRIBUTING.md for details.

--------------------------------------------------------------------

COMMUNITY CONTRIBUTION NEEDS

1) MISSING MARKET EVENTS

Currently at 136 events. What's missing for Indian markets?

Examples:
- Monsoon impact (agriculture, FMCG, two-wheelers)
- Budget policy changes (sector subsidies, tax changes)
- Commodity prices (steel, cement, aluminum)
- Regulatory changes (SEBI policies)
- Geopolitical events (oil supply, trade routes)
- IPL season (consumer discretionary, advertising)
- Festival season (FMCG, auto, retail)

GOAL: Expand to 200+ events with community contributions.

2) KEYWORD REFINEMENTS

Found false positives? Missing keywords for existing events?

Help reduce noise and improve match rates.

3) SECTOR MAPPINGS

Do these relationships make sense?
- Rupee depreciation to IT positive
- Crude surge to aviation negative
- Repo hike to banks mixed

What other sector sensitivities should be captured?

4) USE CASES

What would you build on top of this?

Ideas:
- Sector rotation engine
- Macro risk dashboard
- Trading signal generator
- Market intelligence API
- Portfolio hedging triggers
- Event-driven backtesting

--------------------------------------------------------------------

VERSION HISTORY

Version   Date        Changes
1.0.0     Mar 2026    Initial release (deprecated due to labeling issues)
2.0.0     Mar 2026    Retrained with VADER labels (deprecated)
3.0.0     Mar 2026    PRODUCTION READY - retrained with taxonomy-corrected labels;
                      fixed sector biases; added new sectors and keywords;
                      benchmarked against FinBERT; use case examples added
4.0.0     Apr 2026    MARKET INTELLIGENCE LAYER - Event Impact Engine with 4-factor model;
                      Instrument Classifier (equity, derivatives, commodities, bonds);
                      90-day rolling sector-factor correlations (14 NIFTY sectors);
                      Automated data pipeline (Yahoo Finance, Investing.com, ClickHouse);
                      538 days of FPI net flow data; 504 days of G-Sec yield

--------------------------------------------------------------------

CITATION

@software{aion_sentiment_2026,
  author = {AION Analytics},
  title = {AION-Sentiment-IN: Indian Financial News Sentiment Analysis},
  version = {4.0.0},
  year = {2026},
  url = {https://github.com/AION-Analytics/market-sentiments}
}

--------------------------------------------------------------------

ACKNOWLEDGEMENTS

- Taxonomy events: manual curation (136 India-specific events)
- VADER Sentiment: Hutto & Gilbert (2014) - used as fallback
- NRC Emotion Lexicon: Mohammad & Turney (2013) - emotion analysis
- HuggingFace Transformers: Wolf et al. (2020)
- AION Analytics: News corpus and infrastructure

--------------------------------------------------------------------

LICENSE

Apache License 2.0

--------------------------------------------------------------------

LINKS

HuggingFace: https://huggingface.co/aion-analytics/aion-sentiment-in-v3
GitHub: https://github.com/AION-Analytics/market-sentiments
PyPI: https://pypi.org/project/aion-sentiment/

--------------------------------------------------------------------

Last Updated: April 12, 2026
Copyright: 2026 AION Analytics
Built for the Indian developer community
