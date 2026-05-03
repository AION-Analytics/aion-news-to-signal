# Data Flow

## 1. `aion-news-to-signal`

## 1.1 Input

Public local function:

```python
analyze(headline: str, published_at: str | None = None) -> dict[str, Any]
```

MCP tool:

```python
analyze_news(headline: str, published_at: str | None = None) -> dict[str, Any]
```

Raw input shape:

```json
{
  "headline": "RBI hikes repo rate by 25 bps",
  "published_at": null
}
```

## 1.2 Taxonomy Pipeline Output

`SectorPropagationEngine.propagate(...)` first calls:

```python
TaxonomyPipeline.process(headline=headline, date=published_at)
```

This returns a dictionary with keys documented by the code:

```json
{
  "event": {},
  "impact_level": "string",
  "macro_signal": 0.0,
  "sector_signals": {},
  "active_sector_id": null,
  "active_sector_signal": null,
  "confidence": 0.0,
  "confidence_components": {
    "taxonomy_match": 0.0,
    "data_quality": 0.9,
    "model_probability": null,
    "agreement_score": null
  },
  "metadata": {
    "headline": "string",
    "ticker": null,
    "date": null,
    "taxonomy_version": "string"
  }
}
```

`SectorPropagationEngine.taxonomy_sector_vector(...)` converts `sector_signals` into:

```json
{
  "Financial Services": 0.56925,
  "Banks": 0.56925,
  "NBFC": 0.56925,
  "IT": -0.3465
}
```

## 1.3 Primitive Decomposition

`CauseEffectRuleEngine.extract_conditions(...)` decomposes the headline into:

```json
{
  "weather_type": [],
  "crop_type": [],
  "commodity": [],
  "region": [],
  "month": [],
  "severity": [],
  "policy_action": [],
  "duration": []
}
```

Example actual output from the current code:

```json
{
  "weather_type": ["unseasonal rainfall", "unseasonal rain"],
  "crop_type": ["apple", "horticulture"],
  "commodity": ["apple", "horticulture"],
  "region": ["Himachal Pradesh"],
  "month": [],
  "severity": [],
  "policy_action": [],
  "duration": []
}
```

## 1.4 Disambiguation Output

If `model_confidence < 0.7`, `disambiguate_event(...)` produces:

```json
{
  "candidate_event_a": 0.62,
  "candidate_event_b": 0.14
}
```

This is returned in `markov_scores`.

## 1.5 Propagation Engine Output

Actual top-level output keys from `SectorPropagationEngine.propagate(...)`:

```json
{
  "headline": "string",
  "published_at": null,
  "taxonomy_event_id": "string|null",
  "taxonomy_confidence": 0.0,
  "model_event_id": "string|null",
  "model_confidence": 0.0,
  "resolved_event_id": "string|null",
  "markov_scores": {},
  "weather_triggered": false,
  "cause_effect_rule_id": null,
  "cause_effect_rule_score": 0.0,
  "matched_rule_fields": {},
  "cause_effect_rule_metadata": {},
  "taxonomy_macro_signal": 0.0,
  "direct_impact_vector": {},
  "propagated_impact_vector": {},
  "combined_impact_vector": {},
  "propagation_timeline": []
}
```

The final `combined_impact_vector` is passed into the VIX overlay.

## 1.6 VIX Overlay Transformation

`aion.py` computes:

1. `vix_snapshot = _vix().snapshot(published_at)`
2. `post_vix_vector = _vix().apply(result["combined_impact_vector"], vix_snapshot)`

VIX snapshot shape:

```json
{
  "date": "2026-04-30",
  "vix_close": 16.42,
  "regime": "normal",
  "toggle": "balanced",
  "positive_multiplier": 1.0,
  "negative_multiplier": 1.0
}
```

## 1.7 Stakeholder View Transformation

`stakeholder_impact_mapper.map_views(...)` consumes:

```json
{
  "combined_impact_vector": {},
  "propagation_timeline": [],
  "cause_effect_rule_metadata": {}
}
```

and returns:

```json
{
  "producer_view": {
    "winners": [],
    "losers": []
  },
  "trader_intermediary_view": {
    "winners": [],
    "losers": [],
    "second_order_effects": {}
  },
  "investor_view": {
    "top_risers": [],
    "top_fallers": [],
    "cascade_timeline": []
  },
  "government_fiscal_view": {
    "opportunities": [],
    "risks": [],
    "rebuild_signals": []
  },
  "international_trade_view": {
    "opportunities": [],
    "risks": [],
    "competitor_gains": []
  }
}
```

## 1.8 Final Output JSON

Actual output keys from `aion.analyze(...)`:

```json
{
  "headline": "RBI hikes repo rate by 25 bps",
  "event": "macro_rbi_repo_hike",
  "confidence": 0.4623,
  "vix_regime": "normal",
  "sector_vector": {},
  "top_positive_sectors": {},
  "top_negative_sectors": {},
  "sector_directional_bias": {
    "positive_bias": [],
    "negative_bias": []
  },
  "stakeholder_views": {},
  "raw_assignment": {
    "resolved_event_id": "macro_rbi_repo_hike",
    "cause_effect_rule_id": null,
    "weather_triggered": false
  }
}
```

## 2. `aion-indian-market-calendar`

## 2.1 Bundled File Shape

Actual top-level keys in `data/events_2026.json`:

```json
{
  "events": [],
  "market_sessions": {},
  "market_timings": {},
  "range": {},
  "sources": {},
  "timezone": "Asia/Kolkata",
  "version": "..."
}
```

Example event record from the bundled file:

```json
{
  "id": "MCX_HOLIDAY_20260101",
  "name": "Mcx Holiday: New Year Day",
  "category": "EXCHANGE_HOLIDAY",
  "impact": "EXTREME",
  "applies_to": ["MCX"],
  "start": "2026-01-01T00:00:00+05:30",
  "end": "2026-01-01T23:59:59+05:30",
  "policy": {
    "action": "NO_NEW_TRADES",
    "reason": "New Year Day holiday - market closed"
  },
  "metadata": {
    "exchange": "MCX",
    "segment": "MCX",
    "source": "https://www.mcxindia.com/market-operations/trading-survelliance/trading-holidays",
    "holiday_name": "New Year Day"
  }
}
```

## 2.2 Internal Object Flow

Load path:

1. raw JSON
2. `_normalize_payload(...)`
3. `_load_default_sessions(...)`
4. `MarketEvent.from_dict(...)`
5. `_normalize_event(...)`
6. `self.events`

## 2.3 Event Object Shape

`MarketEvent.to_dict()` returns:

```json
{
  "id": "NSE_EQUITY_HOLIDAY_20260115",
  "name": "Nse Equity Holiday: Municipal Corporation Election - Maharashtra",
  "category": "EXCHANGE_HOLIDAY",
  "impact": "EXTREME",
  "applies_to": ["NSE_EQUITY"],
  "start": "2026-01-15T00:00:00+05:30",
  "end": "2026-01-15T23:59:59+05:30",
  "windows": null,
  "session_override": [],
  "policy": {
    "action": "NO_NEW_TRADES",
    "size_multiplier": null,
    "blocked_strategy_tags": [],
    "allowed_strategy_tags": [],
    "reason": "Municipal Corporation Election - Maharashtra holiday - market closed"
  },
  "tags": [],
  "description": null,
  "metadata": {
    "exchange": "NSE",
    "segment": "NSE_EQUITY",
    "source": "https://www.nseindia.com/resources/exchange-communication-holidays",
    "holiday_name": "Municipal Corporation Election - Maharashtra"
  }
}
```

## 2.4 Session Output Shape

`get_session(...)` returns either:

- `None`
- or `list[SessionSegment]`

Example:

```text
[SessionSegment(market='NSE_EQUITY', open=09:00:00, close=15:30:00)]
```

## 2.5 Live Refresh Delta Shape

Remote payload expected by `refresh(...)`:

```json
{
  "version": "20260430-001",
  "generated_at": "2026-04-30T10:00:00+05:30",
  "events": [],
  "deleted_ids": []
}
```

Cached local payload written to `~/.aion_indian_market/live_cache.json`:

```json
{
  "version": "string|null",
  "generated_at": "string|null",
  "last_refreshed": "string|null",
  "deleted_ids": [],
  "events": []
}
```
