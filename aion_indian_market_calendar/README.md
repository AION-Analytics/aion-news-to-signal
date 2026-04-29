# aion-indian-market-calendar

**Indian stock market calendar for Python — NSE trading calendar, MCX trading hours, and Indian market holidays API.**

Use this if you need to answer:
- is NSE market open today?
- what are NSE/MCX trading hours right now?
- which days are trading holidays in India?
- build intraday or algo trading systems with correct market timings

Works as a **Python API** for NSE trading calendar, Indian stock market holidays, MCX trading hours, "is market open today India" queries, and financial market calendar needs in quantitative finance and algorithmic trading.

Includes macro-event awareness (RBI, Budget, FOMC) for trading system restrictions.

If you tried using `pandas_market_calendars` for India and ran into incorrect holidays or missing MCX sessions, this package fixes those gaps.

## Structure

```text
aion_indian_market_calendar/
├── __init__.py
├── calendar.py
├── models.py
├── data/
│   └── events_2026.json
├── tests/
│   ├── conftest.py
│   └── test_calendar.py
├── pyproject.toml
└── README.md
```

## Quick Start

Simple Python API, no external services required.

### Is the market open right now?

```python
from aion_indian_market_calendar import is_market_open

is_market_open("NSE")  # True / False
is_market_open("MCX")  # Handles evening sessions correctly
```

Used in intraday trading and algo trading systems to prevent execution during closed sessions. Works for real-time checks like: "is NSE market open today?"

### Next trading day

```python
from aion_indian_market_calendar import next_trading_day

next_trading_day("NSE")
```

### Full calendar API

```python
import pytz

from datetime import datetime

from aion_indian_market_calendar import IndiaMarketCalendar

cal = IndiaMarketCalendar.bundled(2026)
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)

# Check if NSE equity is trading right now
print("NSE open?", cal.is_market_open(now, "NSE_EQUITY"))

# Get today's exact trading session (accounts for partial MCX days)
session = cal.get_session(now, "MCX")
for seg in session or []:
    print(f"MCX: {seg.open} - {seg.close}")

# List all NSE equity holidays for 2026
for d in cal.holidays("NSE_EQUITY", 2026):
    print(d)
```

Designed for trading systems, bots, and execution engines that require accurate Indian market timings.

## Use with AION News-to-Signal

Used alongside AION News-to-Signal for:
- validating whether a signal falls within trading hours
- blocking trades on holidays or macro-event windows
- aligning intraday execution with real Indian market sessions

## Why Developers Choose aion-indian-market-calendar

- Save weeks of engineering: no need to scrape NSE circulars, parse Hindu calendars, or model MCX partial sessions
- Production-ready: verified against official exchange calendars and tested for known edge cases
- Live delta updates: refresh from a remote URL, no `pip install --upgrade` needed for every holiday change
- LLM-friendly: static JSON and live endpoint are machine-readable, so coding assistants can query or embed the package

## Live Refresh

```python
calendar = IndiaMarketCalendar.bundled(
    2026,
    refresh_url="https://<username>.github.io/<repo>/live_events.json",
    refresh_interval_hours=4,
)

calendar.refresh()
```

- live deltas are cached at `~/.aion_indian_market/live_cache.json`
- bundled static events remain the fallback
- live events override bundled events by `id`
- `deleted_ids` can remove bundled events without repackaging the wheel

### Delta Format

```json
{
  "version": "20260430-001",
  "generated_at": "2026-04-30T10:00:00+05:30",
  "events": [],
  "deleted_ids": []
}
```

## Notes

- `data/events_2026.json` can be either:
  - a plain list of event objects, or
  - an object with top-level metadata plus an `events` list
- main typed models:
  - `MarketEvent`
  - `EventPolicy`
  - `SessionSegment`
- bundled metadata also exposes:
  - `calendar.sources`
  - `calendar.market_timings`
  - `calendar.default_sessions`
- convenience helpers:
  - `is_market_open(market="NSE", at=None, year=2026)`
  - `next_trading_day(market="NSE", after=None, year=2026)`
- live refresh metadata exposes:
  - `calendar.refresh_url`
  - `calendar.refresh_interval`
- bundled 2026 segment calendars now include:
  - `NSE_EQUITY`
  - `NSE_EQUITY_DERIVATIVES`
  - `NSE_CURRENCY_DERIVATIVES`
  - `NSE_COMMODITY_DERIVATIVES`
  - `NSE_INTEREST_RATE_DERIVATIVES`
  - `NSE_CORPORATE_BONDS`
  - `MCX`
- `EventCalendar` remains available as a compatibility alias for `IndiaMarketCalendar`
- the current bundled data is copied from:
  - `src/shared_core/risk/special_events_and_holidays.json`
  and extended with:
  - `https://nsearchives.nseindia.com/content/RSS/Circulars.xml`
  - `https://www.nseindia.com/resources/exchange-communication-holidays`
  - `https://www.mcxindia.com/market-operations/trading-survelliance/trading-holidays`
- repo-side helpers for live updates:
  - `scripts/poll_nse_rss.py`
  - `.github/workflows/update_live_events.yml`
  - `.github/workflows/publish_live_events.yml`
