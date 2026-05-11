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
[ DYNAMIC MACRO FALLBACK ]
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
- `aion_news_to_signal_self_hosted/src/aion/pipeline.py`
  - versioned self-hosted package runtime consumed by installed environments
    that import `from aion import analyze, get_pipeline`
- `sector_propagation_engine.py`
  - taxonomy + rule + disambiguation + propagation + dynamic fallback gating
- `dynamic_macro_propagator.py`
  - template-level fallback for broad macro events not covered by specific rules
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

#### `[ DYNAMIC MACRO FALLBACK ]`

Implemented by:

- `DynamicMacroFallbackPropagator`
- `cause_effect_rule_classifier_v3/macro_event_templates.yaml`
- `DependencyWeightedPropagator`
- `VocabularyExpander`

This stage activates only when:

- no specific cause-effect YAML rule fired
- and the resolved event is missing or the combined sector vector is all zero

It selects a broad macro template by weighted expanded-keyword scoring, unique
keyword-family coverage, and a minimum meaningful-token density gate. Specific
terms such as `war`, `attack`, `crude oil`, or `repo rate` outrank generic terms
such as `rules` or `deadline`. The selected template then applies dependency
weights where relevant, marks the output in `raw_assignment.dynamic_fallback_*`,
and leaves the existing VIX overlay to the public `aion.analyze(...)` layer.
Dynamic fallback hits are telemetry, not final taxonomy authority; repeated
template hits are fed back into the review queue for specific-rule creation.

Installed self-hosted runtimes also include a package-level deterministic macro
overlay for high-priority events that previously polluted downstream crawlers
when the frozen classifier fallback was trusted directly. This package overlay
currently covers geopolitical conflict, oil-supply shock, and commercial
LPG/fuel price policy changes, and includes a narrow non-financial guard that
returns `event: null` with an all-zero `sector_vector` for low-confidence,
out-of-domain headlines.

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
