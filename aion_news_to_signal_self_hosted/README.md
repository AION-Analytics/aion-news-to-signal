# AION News-to-Signal Self-Hosted Runtime

Local/self-hosted source package for the active `aion-news-to-signal` runtime.

Production callers should continue to use:

```python
from aion import analyze, get_pipeline
```

This source tree exists so runtime fixes are made in package code and installed
into the trading environment, instead of editing `.venv` files directly.

## 1.0.0.post2

- Adds package-level deterministic macro overlays for:
  - geopolitical conflict headlines,
  - geopolitical oil-supply shock headlines,
  - commercial LPG / industrial fuel price policy changes.
- Adds a narrow non-financial guard so low-confidence model fallback does not
  emit market events for nonsense or out-of-domain headlines.
- Keeps the correction inside the `aion-news-to-signal` package so crawlers
  consume clean `analyze()` output and do not need model-specific heuristics.
- Does not change DistilBERT classifier weights.
