# Changelog
*Auto-maintained by Qwen Code + aion_algo_trading rules*
*Revert any change by finding timestamp and restoring from .bkup_{date} backup*

## [2026-04-12 18:50:00 IST]
- [release]: Pushed market intelligence layer to GitHub (commit f8f73d9) — 14 files, 1793 insertions; updated Hugging Face model card (commit 66fa66e) with 4-factor engine documentation (files: README.md, aion_taxonomy/README.md, aion-sentiment/src/aion_sentiment/__init__.py, aion_taxonomy/scripts/, scripts/, dataset/) | Task: task-018
  type = release
  task_id = task-018

## [2026-04-12 18:45:00 IST]
- [release]: Published aion-sentiment v0.3.0 to PyPI — added Market Intelligence Layer exports (classify_instrument, get_meta_factors, calculate_impact, rank_instruments_by_impact) with optional aion_taxonomy integration (files: aion-sentiment/src/aion_sentiment/__init__.py, dist/aion_sentiment-0.3.0-py3-none-any.whl, dist/aion_sentiment-0.3.0.tar.gz) | Task: task-017
  type = feat
  task_id = task-017

## [2026-04-12 18:30:00 IST]
- [docs]: Updated root README.md with Market Intelligence Layer section (4-factor model, Event Impact Engine examples, new platform components, v4.0.0 version history) and created aion_taxonomy/README.md; updated aion_sentiment/__init__.py to export classify_instrument, get_meta_factors, calculate_impact (files: README.md, aion_taxonomy/README.md, aion-sentiment/src/aion_sentiment/__init__.py, scripts/) | Task: task-016
  type = docs
  task_id = task-016

## [2026-04-12 18:00:00 IST]
- [feat]: 4-factor rolling correlations computed — aggregated 5-min VIX to daily (413 rows), merged with ClickHouse VIX (503 rows total), aligned all factors + 14 sectors (415 days), computed 90-day rolling correlations (interest_rate, crude_oil, rupee, risk_sentiment) (files: dataset/vix_daily_full.csv, dataset/aligned_4factor_daily.csv, aion_taxonomy/src/aion_taxonomy/data/sector_sensitivities.json) | Task: task-012,task-013,task-014,task-015
  type = feat
  task_id = task-012

## [2026-04-12 17:03:00 IST]
- [feat]: Scraped 538 trading days of FPI daily equity net flows from NSDL archive (Apr 2024 – Mar 2026) via batched month-end XHR requests with fresh viewstate tokens (files: dataset/fpi_daily_nsdl.csv) | Task: task-011
  type = feat
  task_id = task-011

## [2026-04-12 16:16:00 IST]
- [feat]: Backfilled G-Sec 10Y yield to 2 years (504 rows, Apr 2024 → Apr 2026) via 5 additional XHR batches to Investing.com (curr_id=24014) (files: dataset/India 10-Year Bond Yield Historical Data.csv) | Task: task-008
  type = feat
  task_id = task-008

## [2026-04-12 15:00:00 IST]
- [feat]: Layer 4 complete — dynamic sensitivity calibration via 90-day rolling correlations (files: aion_taxonomy/scripts/fetch_meta_data.py, aion_taxonomy/scripts/update_sensitivities.py, aion_taxonomy/scripts/scrape_gsec_yield.py, aion_taxonomy/scripts/refresh_sensitivities.py, aion_taxonomy/src/aion_taxonomy/instrument_classifier.py, aion_taxonomy/src/aion_taxonomy/data/sector_sensitivities.json, dataset/India 10-Year Bond Yield Historical Data.csv) | Task: task-008,task-009,task-010,task-011
  type = feat
  task_id = task-008

## [2026-04-10 12:45:00 IST]
- [feat]: Extended instrument_classifier.py to handle currency derivatives (CDS) and bond/G-Sec fixed income instruments (files: aion_taxonomy/src/aion_taxonomy/instrument_classifier.py) | Task: task-002
  type = feat
  task_id = task-002

## [2026-04-10 12:40:00 IST]
- [feat]: Extended instrument_classifier.py to handle commodity instruments (MCX/NCO) with precious metal, energy, base metal sub-classification (files: aion_taxonomy/src/aion_taxonomy/instrument_classifier.py) | Task: task-002
  type = feat
  task_id = task-002

## [2026-04-10 12:35:00 IST]
- [feat]: Added instrument_classifier.py to aion_taxonomy for equity spot and index derivative classification (files: aion_taxonomy/src/aion_taxonomy/instrument_classifier.py) | Task: task-002
  type = feat
  task_id = task-002

## [2026-04-10 12:25:00 IST]
- [feat]: Published 3 packages to PyPI — aion-sectormap (v0.1.0), aion-volweight (v0.1.0), aion-taxonomy (v1.0.0) (files: aion-sectormap/dist/, aion-volweight/dist/, aion_taxonomy/dist/) | Task: pypi-publish-all-packages-001
  type = feat
  task_id = pypi-publish-all-packages-001

## [2026-04-06 14:00:00 IST]
- [fix]: Added inference-time override for high-impact negative events to fix false positive sentiment (files: models/aion_sentiment_unified_v1/README.md, src/zerodha/crawlers/gift_nifty_gap.py) | Task: fix-sentiment-false-positive-001
  type = fix
  task_id = fix-sentiment-false-positive-001
- [feat]: Generated 4,000 synthetic training examples for 8 underrepresented negative events (files: generate_synthetic_events.py, synthetic_events.csv) | Task: fix-sentiment-false-positive-001
  type = feat
  task_id = fix-sentiment-false-positive-001
- [feat]: Merged synthetic data with training_data_unified.csv → training_data_augmented.csv (104,470 rows) (files: merge_synthetic_data.py, training_data_augmented.csv) | Task: fix-sentiment-false-positive-001
  type = feat
  task_id = fix-sentiment-false-positive-001
- [fix]: Fixed sentiment labels in training data based on macro_signal sign (files: fix_sentiment_labels.py, training_data_fixed.csv) | Task: fix-sentiment-false-positive-001
  type = fix
  task_id = fix-sentiment-false-positive-001
- [chore]: Added --data and --sentiment-weight args to train_multitask.py (files: train_multitask.py) | Task: fix-sentiment-false-positive-001
  type = chore
  task_id = fix-sentiment-false-positive-001
- [docs]: Created GitHub issue #1 and HuggingFace discussion #1 documenting known issue and workaround (files: github_issue_false_positive.md, hf_discussion_override.md) | Task: fix-sentiment-false-positive-001
  type = docs
  task_id = fix-sentiment-false-positive-001
- [feat]: Trained 6 batch models (multi_task_v2_batch1-6) on 100K+ rows for v2.0 retraining (files: models/multi_task_v2_batch1-6/) | Task: fix-sentiment-false-positive-001
  type = feat
  task_id = fix-sentiment-false-positive-001
- [feat]: Created balanced sentiment dataset pipeline and batch splitting (files: training_data_fixed_batch_1-6.csv, balanced_sentiment.csv) | Task: fix-sentiment-false-positive-001
  type = feat
  task_id = fix-sentiment-false-positive-001

## [1.0.0] - 2026-04-05

AION Unified Sentiment Model v1 — multi-task transformer for Indian financial news.

### Multi-Task Model Architecture

- Built MultiTaskModel: DistilBERT encoder with 4 task heads
  - Sentiment head: 3-class classification (negative/neutral/positive), cross-entropy loss
  - Event head: 95-class classification (taxonomy events), cross-entropy loss
  - Macro head: regression (-1 to +1 market impact), MSE loss
  - Sector head: 32-dim regression (NSE sector impacts), MSE loss
- Base model: distilbert-base-uncased, 67M parameters, 270MB
- Max sequence length: 128 tokens

### Training Pipeline

- Extracted 100,470 raw headlines from ClickHouse aion_master
- Labeled sentiment via AION-Sentiment-IN-v3 model
- Merged with Nifty 100 labeled (6,910 headlines) and baptle labeled (248 headlines)
- Generated 200 synthetic rupee appreciation headlines with correct negative sentiment to fix "strengthens = positive" polarity flip
- Final training set: 42,214 rows (2,979 event-matched, 39,235 sentiment-only)
- Separated training strategy: event rows train all 4 heads at 10x weight, sentiment-only rows train sentiment head only
- Loss weights: event=10.0, macro=10.0, sector=10.0, sentiment=1.0
- Trained 5 epochs, batch_size=64, lr=2e-5
- 5 epochs, batch_size=64, lr=2e-5 on Apple M4 (MPS acceleration)

### Taxonomy Integration

- Added context_rules to taxonomy_india_v2_calibrated.yaml for currency_appreciation, currency_depreciation, bank_npa, layoffs
- Context rules override polarity: e.g. rupee strengthens → negative sentiment (hurts exporters)
- Sector bias rules: inverse (IT, Healthcare) vs aligned (Oil, Aviation, Metals, Capital Goods)

### Ticker and Sector Mapping

- Created ticker_to_sector.json: 90 NSE tickers across 32 sectors
- _detect_ticker(headline): extracts NSE symbols from headlines (longest-match first + name variants)
- _unified_analysis(headline, ticker): returns sentiment, event_id, macro_signal, sector_impacts, active_sector_signal, active_sector_id

### Crawler Integration (gift_nifty_gap.py)

- Replaced legacy AION Sentiment v3 with unified MultiTaskModel in Zerodha Pulse crawler
- Added ticker detection and active sector resolution
- News published to Redis news:sorted_set with enriched fields: sentiment, event_id, macro_signal, 32-sector impacts, active_sector_id, relevant_indices
- ~30ms inference time per headline on MPS

### Temperature Scaling

- Added temperature scaling T=1.5 to softmax during inference
- Reduces overconfidence: 1.00 → 0.96 for strong signals, 0.64 → 0.57 for uncertain ones
- Applied to both sentiment and event logits
- Argmax predictions unchanged, only confidence values are calibrated

### Premarket Predictor Integration

- Updated nifty_open_predictor.py to read from indices_master_v3 (was v1)
- Migrated US500, GIFT NIFTY, NIFTY 50, INDIA VIX, NIFTY BANK from ticks_buffer_v1 to indices_master_v3 (34,677 rows)
- Migrated sectoral banks: NSENIFTYPVTBANK, NSENIFTYPSUBANK, NSENIFTYFINSERVICE (23,426 rows)
- Updated all 12 ClickHouse queries to v3 table
- Updated news sentiment reader to accept event_confidence field (was only confidence_adjusted/confidence_base)

### Model Evaluation

- 8/8 validation checks passed on live Zerodha Pulse headlines:
  - "Rupee strengthens..." → negative (0.94), IT=-0.34, Healthcare=-0.32, Aviation=+0.32
  - "RBI repo cut..." → positive (0.97), Banks=+0.06, Auto=+0.07
  - "Sensex crashes..." → negative (0.98), macro=-0.23
  - "Reliance profit..." → positive (1.00), macro=+0.26
- Sentiment accuracy: 97.2%
- Event classification accuracy: 99.5%
- Macro signal correlation: 0.990
- Sector impacts average MAE: 0.0043

### HuggingFace Deployment

- Model: https://huggingface.co/AION-Analytics/aion-sentiment-unified-v1
  - 9 files: pytorch_model.bin, config.json, event_mapping.json, sector_order.json, tokenizer.json, README.md
- Dataset: https://huggingface.co/datasets/AION-Analytics/indian_financial_news_42k
  - 42,214 rows with 32 sector columns, Apache 2.0 license

### PyPI Package

- Package: aion-sentiment v0.2.0
- URL: https://pypi.org/project/aion-sentiment/0.2.0/
- Updated description to reflect unified model capabilities
- Author email: aionlabs@tutamail.com

### GitHub Repository

- Repo: https://github.com/AION-Analytics/aion-news-to-signal
- Removed legacy aion-sentiment-in/ (24 files, 147,374 lines of old v1/v2/v3 code)
- Removed emotions.py, NRC lexicons (141,893 lines), old tests, example.py
- Updated README with unified model quick start and HuggingFace links
- Updated pyproject.toml and setup.py descriptions

### Code Cleanup

- Deleted et_headlines.txt, et_scrape_progress.txt (scrape artifacts)
- Rewrote CHANGELOG.md with unified model documentation only
- Removed outdated CONTRIBUTING.md (v3 release instructions)

## [0.1.0] - 2026-03-14

- Initial release: aion-sentiment with transformer-based sentiment analysis
- Trained on 957K Indian financial news headlines
