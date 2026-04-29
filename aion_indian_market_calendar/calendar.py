from __future__ import annotations

import json
import logging
import os
import pkgutil
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Iterable
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from .models import MarketEvent, SessionSegment

logger = logging.getLogger(__name__)

DEFAULT_SESSIONS: dict[str, list[SessionSegment]] = {
    "NSE": [SessionSegment(market="NSE", open=time(9, 0), close=time(15, 30))],
    "NSE_EQUITY": [SessionSegment(market="NSE_EQUITY", open=time(9, 0), close=time(15, 30))],
    "NSE_EQUITY_DERIVATIVES": [SessionSegment(market="NSE_EQUITY_DERIVATIVES", open=time(9, 15), close=time(15, 30))],
    "BSE": [SessionSegment(market="BSE", open=time(9, 15), close=time(15, 30))],
    "NSE_COMMODITY_DERIVATIVES": [SessionSegment(market="NSE_COMMODITY_DERIVATIVES", open=time(9, 0), close=time(23, 30))],
    "MCX": [
        SessionSegment(market="MCX", open=time(8, 45), close=time(8, 59)),
        SessionSegment(market="MCX", open=time(9, 0), close=time(23, 30)),
    ],
    "NSE_INTEREST_RATE_DERIVATIVES": [SessionSegment(market="NSE_INTEREST_RATE_DERIVATIVES", open=time(9, 0), close=time(17, 0))],
    "NSE_CORPORATE_BONDS": [SessionSegment(market="NSE_CORPORATE_BONDS", open=time(9, 0), close=time(17, 15))],
}

MARKET_ALIASES: dict[str, set[str]] = {
    "NSE": {"NSE", "NSE_EQUITY", "EQUITIES", "NSE_CASH", "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "NIFTYNXT50"},
    "NSE_EQUITY": {"NSE", "NSE_EQUITY", "EQUITIES", "NSE_CASH", "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "NIFTYNXT50"},
    "NFO": {"NFO", "FNO", "NSE_FNO", "EQUITY_DERIVATIVES", "NSE_EQUITY_DERIVATIVES", "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"},
    "NSE_EQUITY_DERIVATIVES": {"NFO", "FNO", "NSE_FNO", "EQUITY_DERIVATIVES", "NSE_EQUITY_DERIVATIVES", "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"},
    "NSE_CURRENCY_DERIVATIVES": {"NSE_CURRENCY_DERIVATIVES", "CURRENCY_DERIVATIVES", "CDS", "USDINR", "EURINR", "GBPINR", "JPYINR"},
    "NSE_COMMODITY_DERIVATIVES": {"NSE_COMMODITY_DERIVATIVES", "COMMODITY_DERIVATIVES", "NSE_COMMODITIES"},
    "NSE_INTEREST_RATE_DERIVATIVES": {"NSE_INTEREST_RATE_DERIVATIVES", "INTEREST_RATE_DERIVATIVES", "IRD"},
    "NSE_CORPORATE_BONDS": {"NSE_CORPORATE_BONDS", "CORPORATE_BONDS", "CBRICS"},
    "BSE": {"BSE", "SENSEX", "BANKEX"},
    "MCX": {"MCX", "MCX-COMMODITIES", "CRUDEOIL", "NATURALGAS", "GOLD", "SILVER", "COPPER", "ALUMINIUM", "ZINC", "LEAD", "NICKEL"},
}


def _coerce_datetime(value: date | datetime | str, tz: ZoneInfo) -> datetime:
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime.combine(value, time.min)
    else:
        text = str(value).strip()
        if len(text) == 10:
            dt = datetime.fromisoformat(f"{text}T00:00:00")
        else:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))

    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


class IndiaMarketCalendar:
    def __init__(
        self,
        events_json_path: str | None = None,
        *,
        refresh_url: str | None = None,
        refresh_interval_hours: float = 6,
        _raw: dict | list | None = None,
    ):
        if _raw is None:
            if events_json_path is None:
                data = pkgutil.get_data(__package__, "data/events_2026.json")
                if data is None:
                    raise FileNotFoundError("Bundled calendar data/events_2026.json not found")
                raw = json.loads(data.decode("utf-8"))
            else:
                raw = json.loads(Path(events_json_path).read_text(encoding="utf-8"))
        else:
            raw = _raw

        payload = self._normalize_payload(raw)
        self.timezone = payload["timezone"]
        self.tz = ZoneInfo(self.timezone)
        self.default_sessions = self._load_default_sessions(payload.get("market_sessions"))
        self.sources = dict(payload.get("sources") or {})
        self.market_timings = dict(payload.get("market_timings") or {})
        self.events = tuple(
            sorted(
                (self._normalize_event(event) for event in payload["events"]),
                key=lambda event: (event.start, event.id),
            )
        )
        self.refresh_url = refresh_url
        self.refresh_interval = timedelta(hours=refresh_interval_hours)
        self._last_refreshed: datetime | None = None
        self._live_events: dict[str, MarketEvent] = {}
        self._live_deleted_ids: set[str] = set()
        self._live_version: str | None = None
        self._live_generated_at: datetime | None = None

        if self.refresh_url:
            self._load_cache()
            self.refresh()

    @classmethod
    def from_records(
        cls,
        records: Iterable[dict],
        *,
        timezone: str = "Asia/Kolkata",
        refresh_url: str | None = None,
        refresh_interval_hours: float = 6,
    ) -> "IndiaMarketCalendar":
        return cls(
            refresh_url=refresh_url,
            refresh_interval_hours=refresh_interval_hours,
            _raw={"timezone": timezone, "events": list(records)},
        )

    @classmethod
    def from_json(
        cls,
        path: str | Path,
        *,
        refresh_url: str | None = None,
        refresh_interval_hours: float = 6,
    ) -> "IndiaMarketCalendar":
        return cls(str(path), refresh_url=refresh_url, refresh_interval_hours=refresh_interval_hours)

    @classmethod
    def bundled(
        cls,
        year: int = 2026,
        *,
        refresh_url: str | None = None,
        refresh_interval_hours: float = 6,
    ) -> "IndiaMarketCalendar":
        data = pkgutil.get_data(__package__, f"data/events_{year}.json")
        if data is None:
            raise FileNotFoundError(f"Bundled calendar data/events_{year}.json not found")
        return cls(
            refresh_url=refresh_url,
            refresh_interval_hours=refresh_interval_hours,
            _raw=json.loads(data.decode("utf-8")),
        )

    @staticmethod
    def _normalize_payload(raw: dict | list) -> dict[str, object]:
        if isinstance(raw, list):
            return {
                "timezone": "Asia/Kolkata",
                "events": raw,
                "market_sessions": {},
                "market_timings": {},
                "sources": {},
            }
        if isinstance(raw, dict) and isinstance(raw.get("events"), list):
            return {
                "timezone": str(raw.get("timezone") or "Asia/Kolkata"),
                "events": raw["events"],
                "market_sessions": dict(raw.get("market_sessions") or {}),
                "market_timings": dict(raw.get("market_timings") or {}),
                "sources": dict(raw.get("sources") or {}),
            }
        raise ValueError("Calendar JSON must be a list of events or an object with an events list")

    @staticmethod
    def _load_default_sessions(payload: Any) -> dict[str, list[SessionSegment]]:
        sessions: dict[str, list[SessionSegment]] = {
            market: list(segments) for market, segments in DEFAULT_SESSIONS.items()
        }
        if not isinstance(payload, dict):
            return sessions

        for market, segments in payload.items():
            if not isinstance(segments, list):
                continue
            parsed = [SessionSegment.from_dict(segment) for segment in segments]
            if parsed:
                sessions[str(market).strip().upper()] = parsed
        return sessions

    def _normalize_event(self, payload: dict) -> MarketEvent:
        event = MarketEvent.from_dict(payload)
        start = _coerce_datetime(event.start, self.tz)
        end = _coerce_datetime(event.end, self.tz) if event.end else None
        return MarketEvent(
            id=event.id,
            name=event.name,
            category=event.category,
            impact=event.impact,
            applies_to=list(event.applies_to),
            start=start,
            end=end,
            windows=dict(event.windows) if event.windows else None,
            session_override=list(event.session_override) if event.session_override else None,
            policy=event.policy,
            tags=list(event.tags),
            description=event.description,
            metadata=dict(event.metadata),
        )

    def _now(self) -> datetime:
        return datetime.now(self.tz)

    def _cache_path(self) -> Path:
        base = Path(os.path.expanduser("~")) / ".aion_indian_market"
        base.mkdir(parents=True, exist_ok=True)
        return base / "live_cache.json"

    def _load_cache(self) -> None:
        try:
            payload = json.loads(self._cache_path().read_text(encoding="utf-8"))
            last_refreshed = payload.get("last_refreshed")
            self._last_refreshed = _coerce_datetime(last_refreshed, self.tz) if last_refreshed else None
            generated_at = payload.get("generated_at")
            self._live_generated_at = _coerce_datetime(generated_at, self.tz) if generated_at else None
            self._live_version = payload.get("version")
            self._live_deleted_ids = {str(item).strip() for item in payload.get("deleted_ids", []) if str(item).strip()}
            self._live_events = {
                event.id: self._normalize_event(event.to_dict())
                for event in (MarketEvent.from_dict(record) for record in payload.get("events", []))
                if event.id not in self._live_deleted_ids
            }
        except Exception:
            self._last_refreshed = None
            self._live_generated_at = None
            self._live_version = None
            self._live_deleted_ids = set()
            self._live_events = {}

    def _save_cache(self) -> None:
        payload = {
            "version": self._live_version,
            "generated_at": self._live_generated_at.isoformat() if self._live_generated_at else None,
            "last_refreshed": self._last_refreshed.isoformat() if self._last_refreshed else None,
            "deleted_ids": sorted(self._live_deleted_ids),
            "events": [event.to_dict() for event in self._live_events.values()],
        }
        self._cache_path().write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    def refresh(self, force: bool = False) -> bool:
        if not self.refresh_url:
            return False
        if (
            not force
            and self._last_refreshed is not None
            and (self._now() - self._last_refreshed) < self.refresh_interval
        ):
            logger.debug("Skipping market-calendar refresh; interval has not elapsed")
            return False

        try:
            request = Request(self.refresh_url, headers={"User-Agent": "aion-market-calendar/1.0"})
            with urlopen(request, timeout=10) as response:
                payload = json.load(response)
        except Exception as exc:
            logger.warning("Failed to refresh market-calendar live events: %s", exc)
            return False

        deleted_ids = {str(item).strip() for item in payload.get("deleted_ids", []) if str(item).strip()}
        live_events: dict[str, MarketEvent] = {}
        for record in payload.get("events", []):
            event = self._normalize_event(record)
            if event.id not in deleted_ids:
                live_events[event.id] = event

        generated_at = payload.get("generated_at")
        self._live_generated_at = _coerce_datetime(generated_at, self.tz) if generated_at else None
        self._live_version = payload.get("version")
        self._live_deleted_ids = deleted_ids
        self._live_events = live_events
        self._last_refreshed = self._now()
        self._save_cache()
        logger.info("Loaded %d live market-calendar events from %s", len(live_events), self.refresh_url)
        return True

    def _all_events(self) -> tuple[MarketEvent, ...]:
        merged = {event.id: event for event in self.events}
        for deleted_id in self._live_deleted_ids:
            merged.pop(deleted_id, None)
        merged.update(self._live_events)
        return tuple(sorted(merged.values(), key=lambda event: (event.start, event.id)))

    def __iter__(self):
        return iter(self._all_events())

    def __len__(self) -> int:
        return len(self._all_events())

    def all_events(self) -> tuple[MarketEvent, ...]:
        return self._all_events()

    def _market_tokens(self, market: str) -> set[str]:
        market_upper = market.strip().upper()
        return MARKET_ALIASES.get(market_upper, {market_upper})

    def _resolve_market_key(self, market: str) -> str:
        market_upper = market.strip().upper()
        if market_upper in MARKET_ALIASES:
            return market_upper
        for key, aliases in MARKET_ALIASES.items():
            if market_upper in aliases:
                return key
        return market_upper

    def _market_match(self, left: str, right: str) -> bool:
        return bool(self._market_tokens(left) & self._market_tokens(right))

    def _event_applies_to_market(self, event: MarketEvent, market: str) -> bool:
        if not event.applies_to:
            return True
        event_tokens = {item.upper() for item in event.applies_to}
        return bool(event_tokens & self._market_tokens(market))

    def _event_active_on_day(self, event: MarketEvent, day: date) -> bool:
        end = event.end or event.start
        return event.start.date() <= day <= end.date()

    def _event_active_at(self, event: MarketEvent, dt: datetime) -> bool:
        end = event.end or event.start
        return event.start <= dt <= end

    def holidays(
        self,
        market: str = "NSE",
        year: int | None = None,
        *,
        exchange: str | None = None,
    ) -> list[date]:
        target_market = exchange or market
        results = {
            event.start.date()
            for event in self._all_events()
            if event.is_holiday
            and not event.session_override
            and self._event_applies_to_market(event, target_market)
            and (year is None or event.start.year == year)
        }
        return sorted(results)

    def is_trading_day(self, dt: datetime, market: str = "NSE") -> bool:
        local_dt = _coerce_datetime(dt, self.tz)
        if self._session_overrides_for_day(local_dt.date(), market):
            return True
        if local_dt.weekday() >= 5:
            return False
        return local_dt.date() not in set(self.holidays(market=market, year=local_dt.year))

    def _session_overrides_for_day(self, day: date, market: str) -> list[SessionSegment]:
        overrides: list[SessionSegment] = []
        for event in self._all_events():
            if not self._event_active_on_day(event, day):
                continue
            if not event.session_override:
                continue
            overrides.extend(
                segment
                for segment in event.session_override
                if self._market_match(segment.market, market)
            )
        return sorted(overrides, key=lambda segment: (segment.open, segment.close))

    def get_session(self, dt: datetime, market: str = "NSE") -> list[SessionSegment] | None:
        local_dt = _coerce_datetime(dt, self.tz)
        overrides = self._session_overrides_for_day(local_dt.date(), market)
        if overrides:
            return overrides

        if not self.is_trading_day(local_dt, market=market):
            return None

        market_key = self._resolve_market_key(market)
        return list(self.default_sessions.get(market_key, [])) or None

    def active_sessions(self, dt: datetime, market: str = "NSE") -> list[SessionSegment]:
        local_dt = _coerce_datetime(dt, self.tz)
        sessions = self.get_session(local_dt, market=market) or []
        active: list[SessionSegment] = []
        current = local_dt.timetz().replace(tzinfo=None)
        for segment in sessions:
            if segment.open <= current <= segment.close:
                active.append(segment)
        return active

    def is_market_open(self, dt: datetime | None = None, market: str = "NSE") -> bool:
        local_dt = _coerce_datetime(dt or self._now(), self.tz)
        return bool(self.active_sessions(local_dt, market=market))

    def next_trading_day(
        self,
        after: date | datetime | str | None = None,
        market: str = "NSE",
    ) -> date:
        local_dt = _coerce_datetime(after or self._now(), self.tz)
        cursor = local_dt.date()
        while True:
            probe = datetime.combine(cursor, time(12, 0), tzinfo=self.tz)
            if self.is_trading_day(probe, market=market):
                return cursor
            cursor += timedelta(days=1)

    def get_relevant_events(self, dt: datetime, indices: list[str]) -> list[MarketEvent]:
        local_dt = _coerce_datetime(dt, self.tz)
        index_tokens = {item.strip().upper() for item in indices if item and item.strip()}
        relevant: list[MarketEvent] = []
        for event in self._all_events():
            if not self._event_active_at(event, local_dt):
                continue
            if not event.applies_to:
                relevant.append(event)
                continue
            event_tokens = {item.upper() for item in event.applies_to}
            if event_tokens & index_tokens:
                relevant.append(event)
        return relevant

    def events_on(self, day: date | datetime | str, *, exchange: str | None = None) -> list[MarketEvent]:
        target = _coerce_datetime(day, self.tz).date()
        return [
            event
            for event in self._all_events()
            if event.day == target and (exchange is None or self._event_applies_to_market(event, exchange))
        ]

    def between(
        self,
        start: date | datetime | str,
        end: date | datetime | str,
        *,
        exchange: str | None = None,
    ) -> list[MarketEvent]:
        start_dt = _coerce_datetime(start, self.tz)
        end_dt = _coerce_datetime(end, self.tz)
        if isinstance(end, date) and not isinstance(end, datetime):
            end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        return [
            event
            for event in self._all_events()
            if start_dt <= event.start <= end_dt and (exchange is None or self._event_applies_to_market(event, exchange))
        ]

    def upcoming(
        self,
        *,
        as_of: date | datetime | str | None = None,
        limit: int | None = None,
        exchange: str | None = None,
    ) -> list[MarketEvent]:
        cutoff = _coerce_datetime(as_of or datetime.now(self.tz), self.tz)
        events = [
            event
            for event in self._all_events()
            if event.start >= cutoff and (exchange is None or self._event_applies_to_market(event, exchange))
        ]
        return events[:limit] if limit is not None else events

    def by_category(self, category: str) -> list[MarketEvent]:
        needle = category.strip().lower()
        return [event for event in self._all_events() if event.category.lower() == needle]

    def search(self, text: str) -> list[MarketEvent]:
        needle = text.strip().lower()
        if not needle:
            return list(self._all_events())
        return [
            event
            for event in self._all_events()
            if needle in event.name.lower()
            or needle in (event.description or "").lower()
            or any(needle in tag.lower() for tag in event.tags)
            or needle in event.policy.reason.lower()
        ]


EventCalendar = IndiaMarketCalendar
