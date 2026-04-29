from datetime import date, datetime
from functools import lru_cache

from .calendar import EventCalendar, IndiaMarketCalendar
from .models import Event, EventPolicy, MarketEvent, SessionSegment

__all__ = [
    "Event",
    "EventCalendar",
    "EventPolicy",
    "IndiaMarketCalendar",
    "MarketEvent",
    "SessionSegment",
    "is_market_open",
    "next_trading_day",
]


@lru_cache(maxsize=4)
def _bundled_calendar(year: int = 2026) -> IndiaMarketCalendar:
    return IndiaMarketCalendar.bundled(year)


def is_market_open(
    market: str = "NSE",
    at: date | datetime | str | None = None,
    *,
    year: int = 2026,
) -> bool:
    calendar = _bundled_calendar(year)
    when = at if at is not None else datetime.now(calendar.tz)
    return calendar.is_market_open(when, market=market)


def next_trading_day(
    market: str = "NSE",
    after: date | datetime | str | None = None,
    *,
    year: int = 2026,
) -> date:
    calendar = _bundled_calendar(year)
    when = after if after is not None else datetime.now(calendar.tz)
    return calendar.next_trading_day(when, market=market)
