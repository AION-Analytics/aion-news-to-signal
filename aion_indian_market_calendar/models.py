from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any


def _parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)

    text = str(value).strip()
    if not text:
        return None
    if len(text) == 10:
        return datetime.fromisoformat(f"{text}T00:00:00")
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _parse_time(value: Any) -> time | None:
    if value in (None, ""):
        return None
    if isinstance(value, time):
        return value
    text = str(value).strip()
    if not text:
        return None
    if len(text) == 5:
        return time.fromisoformat(text)
    return time.fromisoformat(text[:8])


def _normalize_str_list(values: Any) -> list[str]:
    if values in (None, ""):
        return []
    if isinstance(values, str):
        return [values.strip()] if values.strip() else []
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text:
            result.append(text)
    return result


@dataclass(frozen=True)
class SessionSegment:
    market: str
    open: time
    close: time

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SessionSegment":
        market = str(payload.get("market") or payload.get("exchange") or "").strip()
        if not market:
            raise ValueError("SessionSegment is missing market")

        open_time = _parse_time(payload.get("open"))
        close_time = _parse_time(payload.get("close"))
        if open_time is None or close_time is None:
            raise ValueError("SessionSegment requires open and close times")

        return cls(market=market, open=open_time, close=close_time)

    def to_dict(self) -> dict[str, str]:
        return {
            "market": self.market,
            "open": self.open.isoformat(),
            "close": self.close.isoformat(),
        }


@dataclass(frozen=True)
class EventPolicy:
    action: str
    size_multiplier: float | None = None
    blocked_strategy_tags: list[str] = field(default_factory=list)
    allowed_strategy_tags: list[str] = field(default_factory=list)
    reason: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "EventPolicy":
        payload = dict(payload or {})
        action = str(payload.get("action") or "ALLOW").strip()
        size_multiplier = payload.get("size_multiplier")
        return cls(
            action=action,
            size_multiplier=(float(size_multiplier) if size_multiplier not in (None, "") else None),
            blocked_strategy_tags=_normalize_str_list(payload.get("blocked_strategy_tags")),
            allowed_strategy_tags=_normalize_str_list(payload.get("allowed_strategy_tags")),
            reason=str(payload.get("reason") or "").strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "size_multiplier": self.size_multiplier,
            "blocked_strategy_tags": list(self.blocked_strategy_tags),
            "allowed_strategy_tags": list(self.allowed_strategy_tags),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class MarketEvent:
    id: str
    name: str
    category: str
    impact: str
    applies_to: list[str]
    start: datetime
    end: datetime | None = None
    windows: dict[str, Any] | None = None
    session_override: list[SessionSegment] | None = None
    policy: EventPolicy = field(default_factory=lambda: EventPolicy(action="ALLOW"))
    tags: list[str] = field(default_factory=list)
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def event_id(self) -> str:
        return self.id

    @property
    def title(self) -> str:
        return self.name

    @property
    def starts_at(self) -> datetime:
        return self.start

    @property
    def ends_at(self) -> datetime | None:
        return self.end

    @property
    def exchanges(self) -> list[str]:
        return self.applies_to

    @property
    def is_holiday(self) -> bool:
        return "holiday" in self.category.lower()

    @property
    def day(self) -> date:
        return self.start.date()

    def matches_exchange(self, exchange: str | None) -> bool:
        if not exchange:
            return True
        if not self.applies_to:
            return True
        needle = exchange.strip().upper()
        return needle in {item.upper() for item in self.applies_to}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MarketEvent":
        start = _parse_datetime(payload.get("start") or payload.get("starts_at") or payload.get("date"))
        if start is None:
            raise ValueError("MarketEvent is missing start/starts_at/date")

        event_id = str(payload.get("id") or payload.get("event_id") or "").strip()
        if not event_id:
            raise ValueError("MarketEvent is missing id/event_id")

        name = str(payload.get("name") or payload.get("title") or "").strip()
        if not name:
            raise ValueError("MarketEvent is missing name/title")

        category = str(payload.get("category") or payload.get("type") or "GENERAL").strip()
        impact = str(payload.get("impact") or "UNKNOWN").strip()
        end = _parse_datetime(payload.get("end") or payload.get("ends_at"))
        windows = dict(payload.get("windows") or {}) or None

        session_override_payload = payload.get("session_override") or []
        session_override = (
            [SessionSegment.from_dict(item) for item in session_override_payload]
            if session_override_payload
            else None
        )

        return cls(
            id=event_id,
            name=name,
            category=category,
            impact=impact,
            applies_to=_normalize_str_list(payload.get("applies_to") or payload.get("exchanges")),
            start=start,
            end=end,
            windows=windows,
            session_override=session_override,
            policy=EventPolicy.from_dict(payload.get("policy")),
            tags=_normalize_str_list(payload.get("tags")),
            description=(str(payload["description"]).strip() if payload.get("description") else None),
            metadata=dict(payload.get("metadata") or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "impact": self.impact,
            "applies_to": list(self.applies_to),
            "start": self.start.isoformat(),
            "end": self.end.isoformat() if self.end else None,
            "windows": dict(self.windows) if self.windows else None,
            "session_override": [segment.to_dict() for segment in self.session_override or []],
            "policy": self.policy.to_dict(),
            "tags": list(self.tags),
            "description": self.description,
            "metadata": dict(self.metadata),
        }


Event = MarketEvent
