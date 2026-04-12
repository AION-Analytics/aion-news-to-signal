AION Market Intelligence Layer

A complete 4-factor market intelligence engine for Indian markets, built on top of AION-Sentiment. This system provides real-time event impact analysis by modeling sector sensitivities to:

- Interest Rates (10-year G-Sec yield)
- Crude Oil (WTI futures)
- Rupee/USD (exchange rate)
- Risk Sentiment (India VIX)

--------------------------------------------------------------------

ARCHITECTURE

Layer 1: Instrument Classifier
- Classifies any instrument (equity, derivative, commodity, bond) into asset class and sector
- Uses sector_map.json (591+ tickers) for equity spot classification
- Handles NFO/BFO index derivatives, MCX/NCO commodities, CDS currency, G-SEC bonds

Layer 2: Meta-Factor Sensitivities
- Dynamic 90-day rolling correlations between 14 NIFTY sectors and 4 macro factors
- Static fallback sensitivities for unknown instruments
- Covers equity, derivative, commodity, currency, and fixed income asset classes

Layer 3: Event Impact Engine
- Calculates net impact of any event on any instrument
- Uses 5-factor model: interest_rate, crude_oil, rupee, risk_sentiment, liquidity
- Ranks instruments by impact magnitude for portfolio analysis

Layer 4: Data Pipeline
- Automated data fetching from Yahoo Finance, Investing.com, and ClickHouse
- Weekly sensitivity refresh via refresh_sensitivities.py
- Covers 504 trading days of G-Sec yield, 503 days of VIX, 415 days of sector indices

--------------------------------------------------------------------

QUICK START

from aion_taxonomy.event_impact_engine import rank_instruments_by_impact

# Define your portfolio (tradingsymbol, segment, exchange, underlying)
instruments = [
    {"tradingsymbol": "RELIANCE", "segment": "EQ", "exchange": "NSE"},
    {"tradingsymbol": "HDFCBANK", "segment": "EQ", "exchange": "NSE"},
]

# Get ranked impact for an event
ranked = rank_instruments_by_impact("RBI_RATE_HIKE", instruments)
print(ranked)

--------------------------------------------------------------------

DATA PIPELINE

# Refresh weekly sensitivities
python aion_taxonomy/scripts/refresh_sensitivities.py

# Update sector sensitivities with latest data
python aion_taxonomy/scripts/update_sensitivities.py

# Fetch macroeconomic factor data
python aion_taxonomy/scripts/fetch_meta_data.py

--------------------------------------------------------------------

REQUIREMENTS

Python 3.9+
pandas, numpy, yfinance, clickhouse-connect, curl-cffi

--------------------------------------------------------------------

LICENSE

Apache License 2.0
