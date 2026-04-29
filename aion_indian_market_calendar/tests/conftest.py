from __future__ import annotations

import json

import pytest

from aion_indian_market_calendar import EventCalendar


@pytest.fixture
def sample_records() -> list[dict]:
    return [
        {
            "event_id": "holiday-2026-01-26",
            "title": "Republic Day Market Holiday",
            "category": "holiday",
            "starts_at": "2026-01-26T00:00:00",
            "exchanges": ["NSE", "BSE"],
            "is_holiday": True,
            "tags": ["holiday", "republic-day"],
        },
        {
            "event_id": "policy-2026-02-06",
            "title": "RBI Monetary Policy Statement",
            "category": "macro",
            "starts_at": "2026-02-06T10:00:00",
            "exchanges": ["NSE"],
            "tags": ["rbi", "policy"],
            "policy": {
                "action": "ALLOW_REDUCED_SIZE",
                "size_multiplier": 0.5,
                "reason": "Expected volatility around policy release",
            },
            "session_override": [
                {
                    "market": "NSE",
                    "open": "09:15:00",
                    "close": "13:00:00",
                }
            ],
        },
        {
            "event_id": "earnings-2026-02-10",
            "title": "Large Cap Earnings Cluster",
            "category": "earnings",
            "starts_at": "2026-02-10",
            "exchanges": ["NSE"],
            "tags": ["earnings"],
        },
    ]


@pytest.fixture
def sample_calendar(sample_records: list[dict]) -> EventCalendar:
    return EventCalendar.from_records(sample_records)


@pytest.fixture
def sample_json_path(tmp_path, sample_records: list[dict]):
    path = tmp_path / "events.json"
    path.write_text(json.dumps(sample_records), encoding="utf-8")
    return path
