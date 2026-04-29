from __future__ import annotations

import json
from datetime import date, datetime
from io import BytesIO

from aion_indian_market_calendar import EventCalendar, is_market_open, next_trading_day
from aion_indian_market_calendar import calendar as calendar_module


def test_from_json_loads_events(sample_json_path):
    calendar = EventCalendar.from_json(sample_json_path)
    assert len(calendar) == 3


def test_events_on_filters_by_day_and_exchange(sample_calendar: EventCalendar):
    events = sample_calendar.events_on("2026-01-26", exchange="NSE")
    assert len(events) == 1
    assert events[0].title == "Republic Day Market Holiday"


def test_holidays_returns_only_holiday_events(sample_calendar: EventCalendar):
    holidays = sample_calendar.holidays(exchange="BSE", year=2026)
    assert holidays == [date(2026, 1, 26)]


def test_upcoming_honors_limit(sample_calendar: EventCalendar):
    events = sample_calendar.upcoming(as_of="2026-02-01T00:00:00", limit=1)
    assert len(events) == 1
    assert events[0].event_id == "policy-2026-02-06"


def test_bundled_calendar_loads_placeholder_file():
    calendar = EventCalendar.bundled(2026)
    assert isinstance(calendar, EventCalendar)
    assert len(calendar) > 0
    assert calendar.sources["nse_circulars_rss"] == "https://nsearchives.nseindia.com/content/RSS/Circulars.xml"


def test_policy_and_session_override_are_typed(sample_calendar: EventCalendar):
    event = sample_calendar.by_category("macro")[0]
    assert event.policy.action == "ALLOW_REDUCED_SIZE"
    assert event.policy.size_multiplier == 0.5

    session = sample_calendar.get_session(datetime(2026, 2, 6, 9, 30), market="NSE")
    assert session is not None
    assert len(session) == 1
    assert session[0].close.isoformat() == "13:00:00"


def test_bundled_segment_holidays_and_sessions():
    calendar = EventCalendar.bundled(2026)

    equity_holidays = calendar.holidays(market="NSE_EQUITY", year=2026)
    assert date(2026, 1, 15) in equity_holidays
    assert date(2026, 12, 25) in equity_holidays
    assert len(equity_holidays) == 16
    assert calendar.is_trading_day(datetime(2026, 1, 27, 9, 5), market="NSE_EQUITY")
    equity_session = calendar.get_session(datetime(2026, 1, 27, 9, 5), market="NSE_EQUITY")
    assert equity_session is not None
    assert [(segment.market, segment.open.isoformat(), segment.close.isoformat()) for segment in equity_session] == [("NSE_EQUITY", "09:00:00", "15:30:00")]

    assert calendar.is_trading_day(datetime(2026, 1, 15, 10, 0), market="NSE_COMMODITY_DERIVATIVES")
    commodity_session = calendar.get_session(datetime(2026, 1, 15, 18, 0), market="NSE_COMMODITY_DERIVATIVES")
    assert commodity_session is not None
    assert [(segment.open.isoformat(), segment.close.isoformat()) for segment in commodity_session] == [("17:00:00", "23:30:00")]

    mcx_session = calendar.get_session(datetime(2026, 7, 1, 18, 0), market="MCX")
    assert mcx_session is not None
    assert [(segment.market, segment.open.isoformat(), segment.close.isoformat()) for segment in mcx_session] == [
        ("MCX", "08:45:00", "08:59:00"),
        ("MCX", "09:00:00", "23:30:00"),
    ]
    assert date(2026, 3, 3) not in calendar.holidays(market="MCX", year=2026)
    assert date(2026, 4, 3) in calendar.holidays(market="MCX", year=2026)
    mcx_normal_session = calendar.get_session(datetime(2026, 1, 15, 18, 0), market="MCX")
    assert mcx_normal_session is not None
    assert [(segment.market, segment.open.isoformat(), segment.close.isoformat()) for segment in mcx_normal_session] == [
        ("MCX", "08:45:00", "08:59:00"),
        ("MCX", "09:00:00", "23:30:00"),
    ]
    mcx_partial_session = calendar.get_session(datetime(2026, 3, 3, 18, 0), market="MCX")
    assert mcx_partial_session is not None
    assert [(segment.market, segment.open.isoformat(), segment.close.isoformat()) for segment in mcx_partial_session] == [
        ("MCX", "17:00:00", "23:30:00")
    ]
    assert calendar.is_trading_day(datetime(2026, 3, 3, 18, 0), market="MCX")
    assert not calendar.is_trading_day(datetime(2026, 4, 3, 18, 0), market="MCX")


def test_is_market_open_is_session_aware():
    calendar = EventCalendar.bundled(2026)

    assert calendar.is_market_open(datetime(2026, 1, 27, 9, 5), market="NSE_EQUITY")
    assert not calendar.is_market_open(datetime(2026, 1, 27, 8, 55), market="NSE_EQUITY")
    assert calendar.is_market_open(datetime(2026, 3, 3, 18, 0), market="MCX")
    assert not calendar.is_market_open(datetime(2026, 4, 3, 18, 0), market="MCX")


def test_module_level_is_market_open_helper():
    assert is_market_open("NSE", at="2026-01-27T09:05:00+05:30")
    assert not is_market_open("NSE", at="2026-01-27T08:55:00+05:30")


def test_next_trading_day_helper():
    calendar = EventCalendar.bundled(2026)
    assert calendar.next_trading_day("2026-01-26T10:00:00+05:30", market="NSE_EQUITY") == date(2026, 1, 27)
    assert next_trading_day("NSE_EQUITY", after="2026-01-26T10:00:00+05:30") == date(2026, 1, 27)


def test_refresh_from_url_merges_and_deletes(monkeypatch, sample_records, tmp_path):
    live_payload = {
        "version": "20260430-001",
        "generated_at": "2026-04-30T10:00:00+05:30",
        "events": [
            {
                "id": "policy-2026-02-06",
                "name": "RBI Monetary Policy Statement (Updated)",
                "category": "macro",
                "impact": "HIGH",
                "applies_to": ["NSE"],
                "start": "2026-02-06T11:00:00+05:30",
                "end": "2026-02-06T12:00:00+05:30",
                "policy": {"action": "NO_NEW_TRADES", "reason": "Updated from live feed"},
            },
            {
                "id": "live-2026-05-12",
                "name": "Exchange Holiday: State Election",
                "category": "EXCHANGE_HOLIDAY",
                "impact": "EXTREME",
                "applies_to": ["NSE"],
                "start": "2026-05-12T00:00:00+05:30",
                "end": "2026-05-12T23:59:59+05:30",
                "policy": {"action": "NO_NEW_TRADES", "reason": "State election day"},
            },
        ],
        "deleted_ids": ["earnings-2026-02-10"],
    }

    class FakeResponse(BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            self.close()
            return False

    monkeypatch.setattr(
        calendar_module,
        "urlopen",
        lambda request, timeout=10: FakeResponse(json.dumps(live_payload).encode("utf-8")),
    )
    monkeypatch.setattr(calendar_module.IndiaMarketCalendar, "_cache_path", lambda self: tmp_path / "live_cache.json")

    calendar = EventCalendar.from_records(
        sample_records,
        refresh_url="https://example.com/live_events.json",
        refresh_interval_hours=4,
    )

    all_ids = {event.id for event in calendar.all_events()}
    assert "live-2026-05-12" in all_ids
    assert "earnings-2026-02-10" not in all_ids

    updated = next(event for event in calendar.all_events() if event.id == "policy-2026-02-06")
    assert updated.name == "RBI Monetary Policy Statement (Updated)"
    assert updated.policy.reason == "Updated from live feed"
    assert calendar._live_deleted_ids == {"earnings-2026-02-10"}
    assert calendar._live_version == "20260430-001"
