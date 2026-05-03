# Architecture

## News-To-Signal

```text
[ HEADLINE INPUT ]
        ↓
[ EVENT CLASSIFIER ]
        ↓
[ DISAMBIGUATION (PMI + MARKOV) ]
        ↓
[ PRIMITIVE DECOMPOSITION ]
        ↓
[ SECTOR MATRIX ]
        ↓
[ CAUSAL PROPAGATION ]
        ↓
[ VIX OVERLAY ]
        ↓
[ STAKEHOLDER VIEWS ]
        ↓
[ OUTPUT JSON ]
```

### Actual File Mapping

- `aion_news_to_signal/__init__.py`
  - exports `analyze`
- `aion.py`
  - public local entrypoint
- `sector_propagation_engine.py`
  - taxonomy + rule + disambiguation + propagation
- `stakeholder_impact_mapper.py`
  - stakeholder reshaping of the post-VIX sector vector

### Stage Mapping

#### `[ HEADLINE INPUT ]`

Input enters via:

- `aion.analyze(headline, published_at=None)`
- or MCP tool `analyze_news(...)`

#### `[ EVENT CLASSIFIER ]`

Implemented by:

- `TaxonomyPipeline.process(...)`

Used from:

- `SectorPropagationEngine.propagate(...)`

This stage returns:

- taxonomy event
- sector signals
- macro signal
- taxonomy confidence

#### `[ DISAMBIGUATION (PMI + MARKOV) ]`

Implemented by:

- `EventHistoryModel.transition_score(...)`
- `EventHistoryModel.token_pmi_score(...)`
- `SectorPropagationEngine.disambiguate_event(...)`

This stage only activates when:

- `model_confidence < 0.7`
- and there are candidate events to compare

#### `[ PRIMITIVE DECOMPOSITION ]`

Implemented by:

- `CauseEffectRuleEngine.extract_conditions(...)`

Current primitive buckets:

- `weather_type`
- `crop_type`
- `commodity`
- `region`
- `month`
- `severity`
- `policy_action`
- `duration`

#### `[ SECTOR MATRIX ]`

Implemented by:

- taxonomy sector output from `TaxonomyPipeline`
- cause-to-sector mapping in `CAUSE_SECTOR_TO_MODEL_WEIGHTS`

#### `[ CAUSAL PROPAGATION ]`

Implemented by:

- `CauseEffectRuleEngine.propagation_timeline(...)`
- `CauseEffectRuleEngine.to_sector_vector(...)`

This stage activates only when:

- a cause-effect rule matched
- and `rule_match.score >= 0.5`

#### `[ VIX OVERLAY ]`

Implemented by:

- `VIXOverlay.snapshot(...)`
- `VIXOverlay.apply(...)`

Data source:

- `dataset/india_vix_daily_spot.csv`

#### `[ STAKEHOLDER VIEWS ]`

Implemented by:

- `stakeholder_impact_mapper.map_views(...)`

#### `[ OUTPUT JSON ]`

Final shape is assembled in:

- `aion.analyze(...)`

## Market Calendar

```text
[ SYSTEM CLOCK ]
        ↓
[ MARKET CALENDAR ]
        ↓
[ SESSION STATE ]
        ↓
[ VALIDATION LAYER ]
```

### Actual File Mapping

- `aion_indian_market_calendar/_calendar.py`
- `aion_indian_market_calendar/models.py`
- `aion_indian_market_calendar/__init__.py`

### Stage Mapping

#### `[ SYSTEM CLOCK ]`

Time enters through:

- caller-provided `date`, `datetime`, or ISO string
- or internal `datetime.now(self.tz)`

Normalization is done by:

- `_coerce_datetime(...)`

#### `[ MARKET CALENDAR ]`

Implemented by:

- `IndiaMarketCalendar`

Data sources:

- bundled `data/events_2026.json`
- optional live delta JSON from `refresh_url`

#### `[ SESSION STATE ]`

Derived by:

- `holidays(...)`
- `_session_overrides_for_day(...)`
- `get_session(...)`
- `active_sessions(...)`

#### `[ VALIDATION LAYER ]`

Exposed as:

- `is_trading_day(...)`
- `is_market_open(...)`
- `next_trading_day(...)`

These functions do not place trades or enforce broker rules. They only return deterministic calendar state.
