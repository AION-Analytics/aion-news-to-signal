# Runtime Behavior

## `aion-news-to-signal`

## Activation Path

The main local execution path activates when:

- Python imports `aion_news_to_signal.analyze`
- or MCP calls `analyze_news(...)`

Runtime chain:

1. taxonomy processing
2. optional disambiguation
3. optional cause-effect propagation
4. VIX overlay
5. stakeholder reshaping

## Deterministic vs Probabilistic

### Deterministic Components

- `CauseEffectRuleEngine.extract_conditions(...)`
- `CauseEffectRuleEngine.match(...)`
- `CauseEffectRuleEngine.to_sector_vector(...)`
- `VIXOverlay.snapshot(...)`
- `VIXOverlay.apply(...)`
- `stakeholder_impact_mapper.map_views(...)`

### Probabilistic / Data-Derived Components

- `TaxonomyPipeline.process(...)`
  - confidence and classification are data-driven
- `EventHistoryModel.transition_score(...)`
  - based on fitted historical transition counts
- `EventHistoryModel.token_pmi_score(...)`
  - based on fitted token/event statistics

## Conditional Activation

### Disambiguation

`SectorPropagationEngine.disambiguate_event(...)` is only used when:

- `model_confidence < 0.7`
- and at least one candidate event exists

### Cause-Effect Propagation

The propagation branch activates only when:

- a rule matched
- and `rule_match.score >= 0.5`

If not, `propagation_timeline` is empty and `propagated_impact_vector` stays zeroed.

### VIX Overlay

Always activates in `aion.analyze(...)`.

There is no bypass flag in the current code.

## Latency Expectations

Observed local validation in this session:

- single-call local analysis completed successfully in an interactive Python process

The current codebase does not define explicit latency SLOs or timers.

Practical expectation from structure:

- cold process cost is dominated by:
  - taxonomy loading
  - CSV loading
  - YAML loading
- warm process cost is reduced by:
  - `@lru_cache(maxsize=1)` on engine and VIX overlay

## `aion-indian-market-calendar`

## Activation Path

The calendar activates on:

- constructor load
- query methods
- optional live refresh

## Deterministic vs Probabilistic

All documented calendar behavior is deterministic.

There is no model inference.

## Conditional Activation

### Live Refresh

Refresh activates only when:

- `refresh_url` is configured
- and refresh interval allows a fetch
- or `force=True`

### Session Override Branch

Override sessions win over weekends and holidays if a matching override exists for the day/market.

## Latency Expectations

The package is local-data driven.

Expected cost centers:

- JSON load on initialization
- event normalization
- network fetch only when `refresh(...)` is used

No internal async work or background scheduler exists in the package.
