# API Specification

## `aion-news-to-signal`

## Python API

### `analyze`

Signature:

```python
analyze(headline: str, published_at: str | None = None) -> dict[str, Any]
```

Request fields:

- `headline`
- `published_at`

Response shape:

```json
{
  "headline": "string",
  "event": "string|null",
  "confidence": "float",
  "vix_regime": "string",
  "sector_vector": {},
  "top_positive_sectors": {},
  "top_negative_sectors": {},
  "sector_directional_bias": {
    "positive_bias": [],
    "negative_bias": []
  },
  "stakeholder_views": {},
  "raw_assignment": {
    "resolved_event_id": "string|null",
    "cause_effect_rule_id": "string|null",
    "weather_triggered": "bool"
  }
}
```

Actual observed keys:

- `confidence`
- `event`
- `headline`
- `raw_assignment`
- `sector_vector`
- `sector_directional_bias`
- `stakeholder_views`
- `top_negative_sectors`
- `top_positive_sectors`
- `vix_regime`

Canonical output note:

- `sector_vector` is the detailed sector impact map
- there is no `sector_impacts` key in the public `aion-news-to-signal` output contract

Edge cases:

- empty headline:
  - current code does not reject it
  - observed behavior: returns `event=None` and `confidence=0.405`
- whitespace-only headline:
  - same observed behavior as empty headline
- missing `published_at`:
  - current VIX snapshot uses the latest row in `india_vix_daily_spot.csv`

## MCP API

### `analyze_news`

Signature:

```python
analyze_news(headline: str, published_at: str | None = None) -> dict[str, Any]
```

Behavior:

- returns `aion.analyze(...)` directly
- no extra request transformation is applied

Transport CLI:

```bash
python -m aion_news_to_signal.mcp_server --transport stdio
python -m aion_news_to_signal.mcp_server --transport sse
python -m aion_news_to_signal.mcp_server --transport streamable-http
```

Edge cases:

- if `mcp.server.fastmcp` is unavailable, import fails before server start

## Internal Signal-Engine API

### `SectorPropagationEngine.propagate`

Signature:

```python
propagate(
    headline: str,
    published_at: str | None = None,
    previous_events: list[str] | None = None,
    event_prediction: dict[str, Any] | None = None,
) -> dict[str, Any]
```

Response keys:

```json
{
  "headline": "string",
  "published_at": "string|null",
  "taxonomy_event_id": "string|null",
  "taxonomy_confidence": "float",
  "model_event_id": "string|null",
  "model_confidence": "float",
  "resolved_event_id": "string|null",
  "markov_scores": {},
  "weather_triggered": "bool",
  "cause_effect_rule_id": "string|null",
  "cause_effect_rule_score": "float",
  "matched_rule_fields": {},
  "cause_effect_rule_metadata": {},
  "taxonomy_macro_signal": "float",
  "direct_impact_vector": {},
  "propagated_impact_vector": {},
  "combined_impact_vector": {},
  "propagation_timeline": []
}
```

## `aion-indian-market-calendar`

## Constructors

### `IndiaMarketCalendar(...)`

Signature:

```python
IndiaMarketCalendar(
    events_json_path: str | None = None,
    *,
    refresh_url: str | None = None,
    refresh_interval_hours: float = 6,
    _raw: dict | list | None = None,
)
```

Edge cases:

- missing bundled file:
  - raises `FileNotFoundError`
- invalid raw payload shape:
  - raises `ValueError`

### `IndiaMarketCalendar.from_records(...)`

Signature:

```python
from_records(
    records: Iterable[dict],
    *,
    timezone: str = "Asia/Kolkata",
    refresh_url: str | None = None,
    refresh_interval_hours: float = 6,
) -> IndiaMarketCalendar
```

### `IndiaMarketCalendar.from_json(...)`

Signature:

```python
from_json(
    path: str | Path,
    *,
    refresh_url: str | None = None,
    refresh_interval_hours: float = 6,
) -> IndiaMarketCalendar
```

### `IndiaMarketCalendar.bundled(...)`

Signature:

```python
bundled(
    year: int = 2026,
    *,
    refresh_url: str | None = None,
    refresh_interval_hours: float = 6,
) -> IndiaMarketCalendar
```

## Query API

### `holidays`

```python
holidays(
    market: str = "NSE",
    year: int | None = None,
    *,
    exchange: str | None = None,
) -> list[date]
```

Behavior:

- returns full-day holidays only
- events with `session_override` are excluded from the holiday list

### `is_trading_day`

```python
is_trading_day(dt: datetime, market: str = "NSE") -> bool
```

Behavior:

- weekends return `False`
- unless a session override exists for that date

### `get_session`

```python
get_session(dt: datetime, market: str = "NSE") -> list[SessionSegment] | None
```

Behavior:

- returns override session list if one exists
- otherwise returns default session list
- returns `None` if the market is closed for that datetime’s date
- raises `ValueError` if `market` cannot be resolved to a canonical segment

### `active_sessions`

```python
active_sessions(dt: datetime, market: str = "NSE") -> list[SessionSegment]
```

Behavior:

- filters the full-day session list to only the currently active segments
- raises `ValueError` if `market` cannot be resolved to a canonical segment

### `is_market_open`

```python
is_market_open(dt: datetime | None = None, market: str = "NSE") -> bool
```

Behavior:

- thin boolean wrapper around `active_sessions(...)`
- raises `ValueError` if `market` cannot be resolved to a canonical segment

### `next_trading_day`

```python
next_trading_day(
    after: date | datetime | str | None = None,
    market: str = "NSE",
) -> date
```

Behavior:

- iterates forward by date until `is_trading_day(...)` returns `True`
- raises `ValueError` if `market` cannot be resolved to a canonical segment

### Market Resolution Semantics

Current resolver order:

1. instrument input → canonical segment
2. alias input → canonical segment
3. canonical segment → pass-through
4. otherwise → `ValueError`

Examples:

- `NFO` → `NSE_EQUITY_DERIVATIVES`
- `FNO` → `NSE_EQUITY_DERIVATIVES`
- `NIFTY` → `NSE_EQUITY_DERIVATIVES`
- `BANKNIFTY` → `NSE_EQUITY_DERIVATIVES`

### `refresh`

```python
refresh(force: bool = False) -> bool
```

Behavior:

- returns `False` if no `refresh_url` is configured
- returns `False` if refresh interval has not elapsed
- returns `False` if fetch fails
- returns `True` if live events were loaded successfully

Observed failure behavior:

- invalid refresh URL:
  - logs warning
  - returns `False`

## Package-Level Helpers

### `is_market_open`

```python
is_market_open(
    market: str = "NSE",
    at: date | datetime | str | None = None,
    *,
    year: int = 2026,
) -> bool
```

### `next_trading_day`

```python
next_trading_day(
    market: str = "NSE",
    after: date | datetime | str | None = None,
    *,
    year: int = 2026,
) -> date
```
