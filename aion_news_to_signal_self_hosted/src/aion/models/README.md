This package does not bundle model weights because the combined artifacts exceed typical PyPI file limits.

On first use, `from aion import analyze` downloads the public weights from:
- `AION-Analytics/aion-news-to-signal`
- `distilbert-base-uncased`

The artifacts are cached locally under `~/.cache/aion-news-to-signal` unless `AION_CACHE_DIR` is set.
