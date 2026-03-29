# AION Market Sentiment & Taxonomy System

**AI-powered sentiment intelligence for Indian financial markets**

**99.63% accuracy** | **<100ms latency** | **592 NSE tickers** | **136 Taxonomy Events**

---

## 🎯 What You're Actually Getting

**For Enterprise Licensing:**

| Component | What It Is | What's Yours | Time to Replicate |
|-----------|------------|--------------|-------------------|
| **Sentiment Model** | 6-layer transformer classifier | 100% AION trained weights | 3-4 months |
| **aion-sentiment Package** | Python inference library | 100% AION code | 3-4 months |
| **1M+ Classified Headlines** | Training corpus | 100% AION proprietary | 6-9 months |
| **136 Taxonomy Events** | Market event definitions | 100% AION proprietary | 3-4 months |
| **Sector-Aware Signal Flips** | Same event → opposite sector impacts | 100% AION proprietary | 2-3 months |
| **592 NSE Sector Mappings** | Ticker → sector → signal | 100% AION proprietary | 2-3 months |
| **Production Pipeline** | gift_nifty_gap → Redis → ClickHouse | 100% AION code | 4-6 months |
| **VIX-Adjusted Confidence** | Scoring methodology | 100% AION proprietary | 2-3 months |

**Total:** 18-24 months of work → Available via licensing

**Everything is AION. Everything is proprietary.**

---

## 🔥 Key Differentiator: Sector-Aware Signal Flips

**The SAME event can have OPPOSITE impacts on different sectors:**

### Example: Rupee Depreciation

```
Event: "Rupee falls to all-time low against dollar"

Overall sentiment: NEGATIVE (macro_signal: -0.382)

Sector-specific signals:
├─ IT Services:        +0.382 (POSITIVE) ← Dollar revenues worth more
├─ Healthcare Exports: +0.382 (POSITIVE) ← Export competitiveness
├─ Aviation:           -0.382 (NEGATIVE) ← Fuel costs rise (USD-denominated)
├─ Oil & Gas:          -0.382 (NEGATIVE) ← Import bill increases
└─ Banks:              -0.382 (NEGATIVE) ← FII outflows
```

### Example: Crude Oil Surge

```
Event: "Brent crude jumps 10% on supply concerns"

Overall sentiment: NEGATIVE (macro_signal: -0.45)

Sector-specific signals:
├─ Energy:             +0.40 (POSITIVE) ← Upstream companies benefit
├─ Aviation:           -0.45 (NEGATIVE) ← Fuel costs rise
├─ Transportation:     -0.36 (NEGATIVE) ← Operating costs increase
└─ Paints:             -0.45 (NEGATIVE) ← Input costs rise
```

**This is NOT just sentiment analysis. This is market structure modeling.**

## 📅 Last Updated

**Date:** 2026-03-29
**Time:** 00:00 IST
**Version:** v3.0.0 (Taxonomy-trained)

---

## 📅 March 29, 2026 - HuggingFace Update Complete

### ✅ Model Card Uploaded to HuggingFace

**Model:** https://huggingface.co/aion-analytics/aion-sentiment-in-v3

**Changes Uploaded:**
- ✅ **15 Optimized Tags** (increased from 5 to 15 for better discovery)
- ✅ **Parameter Count Corrected:** ~67M (was incorrectly showing 132M)
- ✅ **Attribution Updated:** AION Analytics (not "AION Open-Source Contributors")
- ✅ **Professional Formatting:** Clean, enterprise-ready presentation

**New Tags Added:**
```
text-classification       financial-news        sector-analysis
sentiment-analysis        indian-markets        taxonomy-driven
financial-nlp             indian-finance        financial-ai
financial-sentiment       stock-market          open-source
transformer               market-intelligence   production-ready
```

**Sync Status:**
| Platform | Status | Last Updated |
|----------|--------|--------------|
| **GitHub** | ✅ MODEL_CARD_HF.md | 2026-03-29 |
| **HuggingFace** | ✅ README.md | 2026-03-29 |
| **Sync** | ✅ Fully Synchronized | 2026-03-29 00:00 IST |

**Commit Message:** "Update model card with optimized 15 tags and AION Analytics attribution"

---

## 📅 Weekly Update Reminder

---

## ✅ System Status: Production Ready

| Component | Status | Coverage | Last Run |
|-----------|--------|----------|----------|
| **aion-sentiment** | ✅ Production | 592 tickers | v3.0.0 |
| **aion-taxonomy** | ✅ Production | 136 events | 2026-03-28 |
| **aion-sectormap** | ✅ Production | 592 tickers | v1.0.0 |
| **aion-volweight** | ✅ Production | VIX regimes | v1.0.0 |
| **gift_nifty_gap** | ✅ Production | Real-time | Every 15 min |
| **nifty_open_predictor** | ✅ Production | NIFTY/BANKNIFTY | Daily 08:46 AM |
| **ClickHouse Backfill** | ✅ Complete | 93.3% | 2026-03-28 |

---

## 🏗️ Complete Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AION SENTIMENT ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────────────┤

  REAL-TIME FLOW (Intraday)
  ═════════════════════════
  
  Zerodha Pulse RSS
        ↓
  gift_nifty_gap.py (Every 15 min)
    - Fetches latest news
    - Loads: taxonomy_india_v2_calibrated.yaml
    - Enriches with taxonomy events
    - Computes: macro_signal, confidence_base, confidence_adjusted
        ↓
  Redis DB1: news:sorted_set
    - Real-time news stream
    - Fields: title, sentiment, macro_signal, 
              confidence_base, confidence_adjusted, 
              taxonomy_event_id, sector_signals, vix_regime
        ↓
  nifty_open_predictor.py (Daily 08:46 AM IST)
    - Reads from Redis (NOT ClickHouse, NOT YAML)
    - Extracts: confidence_adjusted, macro_signal
    - Computes: weighted_sentiment = macro × confidence
    - Features: taxonomy_confidence, taxonomy_weighted_macro
        ↓
  XGBoost ML Model
    - NIFTY/BANKNIFTY/SENSEX pre-open prediction
    - Output: Low/Mid/High price estimates with confidence
        ↓
  Redis DB2: premarket:predictions
    - Consumed by trading bots


  HISTORICAL FLOW (Backfill/Training)
  ═══════════════════════════════════
  
  ClickHouse: news_master_v1 (1,066,658 headlines)
        ↓
  backfill_taxonomy_overnight.py
    - Loads: taxonomy_india_v2_calibrated.yaml
    - Processes historical headlines
    - LEFT ANTI JOIN to avoid duplicates
        ↓
  ClickHouse: news_taxonomy_v1
    - 994,760 unique classified headlines (93.3% coverage)
    - 64,770 matched taxonomy events (6.5% match rate)
    - Fields: event_id, event_name, macro_signal, 
              confidence, sector_impacts, classified_at
        ↓
  Uses:
    - Taxonomy calibration (calibrate_taxonomy.py)
    - ML model training
    - Historical analysis
    - Keyword refinement


  TAXONOMY DEFINITION
  ═══════════════════
  
  taxonomy_india_v2_calibrated.yaml
    - 136 market events
    - 7 categories (macro, sector, global, etc.)
    - 32 sectors with beta weights
    - Base impacts, sector multipliers, VIX regimes
        ↓
  Used by:
    - gift_nifty_gap.py (real-time)
    - backfill_taxonomy_overnight.py (historical)
    - calibrate_taxonomy.py (calibration)
```

---

## 📊 ClickHouse Taxonomy Universe

**⚠️ UPDATE THIS SECTION EVERY WEEK ⚠️**

### Current Status (2026-03-28 20:00 IST)

```sql
-- Run this query weekly to get updated stats:
SELECT 
    count(DISTINCT row_hash) as unique_classified,
    countIf(event_id != '') as matched_events,
    countIf(event_id = '') as no_match,
    avg(macro_signal) as avg_macro,
    avg(confidence) as avg_confidence
FROM aion_master.news_taxonomy_v1;
```

| Metric | Value | Week-over-Week Change |
|--------|-------|----------------------|
| **Total news_master_v1** | 1,066,658 | — |
| **Unique classified (news_taxonomy_v1)** | 994,760 | +XXX,XXX |
| **Coverage** | 93.3% | +X.X% |
| **Matched events (event_id != '')** | 64,770 | +X,XXX |
| **Match rate** | 6.5% | +X.X% |
| **Avg macro signal** | +0.0012 | — |
| **Avg confidence** | 0.428 | — |

### Top 15 Taxonomy Events (by count)

| Rank | Event ID | Count | Avg Signal | Category |
|------|----------|-------|------------|----------|
| 1 | market_fii_selling | 6,576 | -0.276 | Market |
| 2 | corp_earnings_beat | 5,549 | +0.176 | Corporate |
| 3 | market_ipo_open | 5,199 | +0.075 | Market |
| 4 | corp_demerger_value_unlock | 4,114 | +0.199 | Corporate |
| 5 | macro_inr_depreciation | 3,773 | -0.382 | Macro |
| 6 | macro_inr_appreciation | 3,529 | +0.382 | Macro |
| 7 | corp_penalty_imposed | 3,496 | -0.204 | Corporate |
| 8 | corp_merger_positive | 3,059 | +0.175 | Corporate |
| 9 | global_war_escalation | 2,623 | -0.522 | Global |
| 10 | corp_buyback | 2,522 | +0.107 | Corporate |
| 11 | sector_bank_credit_growth | 2,248 | +0.150 | Sector |
| 12 | sector_fmcg_price_hike | 1,987 | +0.125 | Sector |
| 13 | global_sanctions | 1,870 | -0.450 | Global |
| 14 | sector_it_currency_tailwind | 1,786 | +0.138 | Sector |
| 15 | macro_budget_capex_boost | 1,654 | +0.425 | Macro |

### Newly Added Events (This Week)

| Event ID | Keywords Added | Impact | Date |
|----------|---------------|--------|------|
| global_war_escalation | iran war, iran military, strait of hormuz, war live updates | -0.522 | 2026-03-28 |
| global_crude_surge | oil supply disruption, oil tanker attack, strait disruption | -0.450 | 2026-03-28 |

### Keyword Refinements (This Week)

| Event | Old Keywords | New Keywords | Reason |
|-------|-------------|--------------|--------|
| gov_digital_india | upi, digital initiative | upi transaction surge, digital india mission | Reduce false positives |
| micro_ipl_season | ipl | ipl season, ipl tournament, ipl cricket | Add context |
| sector_it_currency_tailwind | rupee falls | rupee tailwind for it, weak rupee helps it | IT-specific |

### Coverage Trend (Last 4 Weeks)

```
Week Ending    | Classified | Matched | Coverage | Match Rate
---------------|------------|---------|----------|-----------
2026-03-28     | 994,760    | 64,770  | 93.3%    | 6.5%
2026-03-21     | XXX,XXX    | XX,XXX  | XX.X%    | X.X%
2026-03-14     | XXX,XXX    | XX,XXX  | XX.X%    | X.X%
2026-03-07     | XXX,XXX    | XX,XXX  | XX.X%    | X.X%
```

<!-- 
  WEEKLY UPDATE INSTRUCTIONS:
  1. Run the ClickHouse query above to get current stats
  2. Update the "Current Status" table with new values
  3. Update "Top 15 Taxonomy Events" with latest counts
  4. Add any new events/keywords to "Newly Added Events"
  5. Document keyword refinements in "Keyword Refinements"
  6. Add a row to "Coverage Trend" table
-->

---

## 🔧 Script Integration Details

### 1. gift_nifty_gap.py (Real-Time Crawler)

**Location:** `/Users/lokeshgupta/Projects/aion_algo_trading/src/zerodha/crawlers/gift_nifty_gap.py`

**Schedule:** Every 15 minutes during market hours

**Integration:**
```python
# Line 364: Initialize taxonomy enricher
self.taxonomy_enricher = SentimentTaxonomyEnricher(
    taxonomy_path="/Users/lokeshgupta/aion_open_source/aion_taxonomy/taxonomy_india_v2_calibrated.yaml"
)

# Line 439: Enrich news with taxonomy
enriched = self.taxonomy_enricher.enrich_news(
    headline=title,
    sentiment_result=sentiment_result,
    current_vix=current_vix,
    ticker=None,
    date=datetime.now(IST_TZ).strftime('%Y-%m-%d')
)

# Line 462-470: Store taxonomy fields in Redis
news_item = {
    "taxonomy_event_id": enriched.get('event_id'),
    "taxonomy_event_name": enriched.get('event_name'),
    "macro_signal": enriched.get('macro_signal', 0.0),
    "sector_signals": enriched.get('sector_signals', {}),
    "confidence_base": enriched.get('confidence_base'),
    "confidence_adjusted": enriched.get('confidence_adjusted'),
    "vix_regime": enriched.get('vix_regime'),
}

# Line 780: Store to Redis sorted_set
self.redis_client.zadd("news:sorted_set", {json.dumps(news_item): now_ts})
```

**Output to Redis DB1:**
- Key: `news:sorted_set`
- Fields: title, sentiment, sentiment_score, macro_signal, confidence_base, confidence_adjusted, taxonomy_event_id, sector_signals, vix_regime

---

### 2. nifty_open_predictor.py (Pre-Market Prediction)

**Location:** `/Users/lokeshgupta/Projects/aion_algo_trading/src/aion_ML/models/predictors/nifty_open_predictor.py`

**Schedule:** Daily at 08:46 AM IST (via launchd plist)

**Plist:** `/Users/lokeshgupta/Projects/aion_algo_trading/src/plists/com.aion.premarket.predictor.plist`

**Integration:**
```python
# Line 119-145: Extract sentiment with taxonomy confidence
def _safe_sentiment_value(news_obj):
    # Try taxonomy-enriched fields first
    macro_signal = news_obj.get('macro_signal')
    confidence = news_obj.get('confidence_adjusted') or news_obj.get('confidence_base')
    
    if macro_signal is not None and confidence is not None:
        return float(macro_signal) * float(confidence)  # Weighted sentiment
    
    # Fallback to legacy sentiment_score
    ...

# Line 148-279: Collect taxonomy confidence from Redis
def _collect_news_sentiment_from_redis(r1, now_ist):
    confidence_values = []
    macro_signals = []
    
    for item in news_items:
        conf = item.get('confidence_adjusted') or item.get('confidence_base')
        macro = item.get('macro_signal', 0.0)
        
        if conf is not None:
            confidence_values.append(float(conf))
        if macro is not None and macro != 0.0:
            macro_signals.append(float(macro))
    
    avg_confidence = sum(confidence_values) / len(confidence_values)
    weighted_macro = sum(macros) / len(macros)
    
    return avg_sent, news_vol, sent_ma3, avg_confidence, weighted_macro

# Line 60-61: BASE_FEATURES includes taxonomy
BASE_FEATURES = [
    ...
    "taxonomy_confidence", "taxonomy_weighted_macro",
]

# Line 609-611: Features dict passes to ML model
"features": {
    ...
    "taxonomy_confidence": avg_confidence,
    "taxonomy_weighted_macro": weighted_macro,
    ...
}
```

**Input from Redis:**
- Reads: `news:sorted_set` (confidence_adjusted, macro_signal)

**Output to ML Model:**
- Features: taxonomy_confidence, taxonomy_weighted_macro
- Prediction: NIFTY/BANKNIFTY/SENSEX open price (Low/Mid/High)

---

### 3. backfill_taxonomy_overnight.py (Historical Backfill)

**Location:** `/Users/lokeshgupta/aion_open_source/aion-sentiment/backfill_taxonomy_overnight.py`

**Status:** ✅ Complete (93.3% coverage)

**Integration:**
```python
# Fetch headlines NOT yet classified
query = """
SELECT DISTINCT n.row_hash, n.title, n.body, n.published_at
FROM aion_master.news_master_v1 n
LEFT ANTI JOIN aion_master.news_taxonomy_v1 t ON n.row_hash = t.row_hash
WHERE n.title != ''
ORDER BY n.published_at DESC
LIMIT {limit} OFFSET {offset}
"""

# Classify with taxonomy
result = self.pipeline.process(
    headline=headline,
    date=published_at.isoformat()
)

# Store to ClickHouse
client.insert("aion_master.news_taxonomy_v1", [
    (row_hash, published_at, event_id, event_name, 
     macro_signal, confidence, sector_impacts, ...)
])
```

**Input from ClickHouse:**
- Table: `news_master_v1` (1,066,658 headlines)

**Output to ClickHouse:**
- Table: `news_taxonomy_v1` (994,760 unique classified)

---

### 4. calibrate_taxonomy.py (Taxonomy Calibration)

**Location:** `/Users/lokeshgupta/aion_open_source/aion_taxonomy/calibrate_taxonomy.py`

**Schedule:** Weekly (after backfill complete)

**Purpose:** Update `event_volatility` and `base_impact` based on actual data

**Integration:**
```python
# Query ClickHouse for event statistics
query = """
SELECT 
    event_id,
    count() as event_count,
    avg(macro_signal) as avg_signal,
    std(macro_signal) as signal_volatility
FROM aion_master.news_taxonomy_v1
WHERE event_id != ''
GROUP BY event_id
"""

# Update taxonomy YAML
for event in taxonomy['events']:
    event['event_volatility'] = computed_volatility
    event['base_impact'] = calibrated_impact
```

**Input from ClickHouse:**
- Table: `news_taxonomy_v1` (classified events)

**Output:**
- File: `taxonomy_india_v2_calibrated.yaml` (updated parameters)

---

## 📦 Packages & Dependencies

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| **aion-sentiment** | v3.0.0 | Sentiment analysis (99.63% accuracy) | ✅ Production |
| **aion-taxonomy** | v2.0.0 | Event classification (136 events) | ✅ Production |
| **aion-sectormap** | v1.0.0 | NSE ticker → sector (592 tickers) | ✅ Production |
| **aion-volweight** | v1.0.0 | VIX-adjusted confidence | ✅ Production |

---

## 🚀 Quickstart

### Real-Time Sentiment

```python
from aion_sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.predict("RBI hikes repo rate by 25 bps")
print(result)
# {'label': 'negative', 'confidence': 0.89}
```

### Taxonomy Event Classification

```python
from aion_taxonomy import TaxonomyPipeline

pipeline = TaxonomyPipeline("taxonomy_india_v2_calibrated.yaml")
result = pipeline.process(
    headline="RBI hikes repo rate",
    ticker="HDFCBANK",
    date="2026-03-28"
)

print(f"Event: {result['event']['event_id']}")
print(f"Macro Signal: {result['macro_signal']:+.3f}")
print(f"Sector Signal (Banks): {result['active_sector_signal']:+.3f}")
print(f"Confidence: {result['confidence']:.1%}")
```

**Output:**
```
Event: macro_rbi_repo_hike
Macro Signal: -0.495
Sector Signal (Banks): +0.569
Confidence: 54.7%
```

---

## 📈 Model Performance

### Sentiment Analysis (v3.0.0)

| Metric | Score |
|--------|-------|
| **Accuracy** | 99.63% |
| **F1 Score** | 99.65% |
| **Precision** | 99.68% |
| **Recall** | 99.62% |
| **Training Data** | 400K taxonomy-labeled headlines |

### Taxonomy Coverage

| Metric | Value |
|--------|-------|
| **Total Events** | 136 |
| **Categories** | 7 |
| **Sectors** | 32 |
| **Keywords** | 500+ |
| **Match Rate** | 6.5% |

---

## 🔍 Monitoring & Alerts

### Daily Checks

```bash
# 1. Check predictor run status (09:00 AM IST)
tail -f /Users/lokeshgupta/Projects/aion_algo_trading/logs/premarket_predictor.log

# Expected output:
--- DEBUG SENTIMENT ---
Avg Taxonomy Confidence: 0.XXX
Weighted Macro Signal: +X.XXXX
-----------------------

# 2. Check gift_nifty_gap crawler (every 15 min)
tail -f /Users/lokeshgupta/Projects/aion_algo_trading/logs/gift_nifty_gap.log

# Expected: "Collected X news items with taxonomy enrichment"

# 3. Check Redis data freshness
redis-cli -n 1 ZCARD news:sorted_set
# Should increase every 15 min during market hours
```

### Weekly Checks

```bash
# 1. Update taxonomy universe stats (Monday 10:00 AM IST)
cd /Users/lokeshgupta/aion_open_source
source venv/bin/activate
python3 -c "
import clickhouse_connect
client = clickhouse_connect.get_client(host='localhost', database='aion_master')
# Run queries and update README.md
"

# 2. Review no-match events
cat aion_taxonomy/no_match_events.txt
# Add keywords for high-frequency unmatched events

# 3. Calibrate taxonomy parameters
cd aion_taxonomy
python3 calibrate_taxonomy.py --taxonomy-path taxonomy_india_v2_calibrated.yaml
```

---

## 📝 Changelog

### 2026-03-28

**Taxonomy Integration Complete**

- ✅ gift_nifty_gap.py integrated with taxonomy confidence
- ✅ nifty_open_predictor.py reads taxonomy fields from Redis
- ✅ BASE_FEATURES updated with taxonomy_confidence, taxonomy_weighted_macro
- ✅ Backfill complete: 994,760 headlines classified (93.3% coverage)
- ✅ Keyword refinements: gov_digital_india, micro_ipl_season, sector_it_currency_tailwind
- ✅ New keywords added: iran war, strait of hormuz, oil supply disruption

**ClickHouse Universe**

- Total classified: 994,760 (93.3% coverage)
- Matched events: 64,770 (6.5% match rate)
- Unique events: 47

### 2026-03-27

**Backfill Execution**

- ✅ backfill_taxonomy_overnight.py executed
- ✅ 420,000 headlines processed
- ✅ Checkpoint system fixed (bytes serialization bug resolved)

### 2026-03-29

**HuggingFace Model Card Update**

- ✅ Uploaded optimized model card with **15 tags** (was 5)
- ✅ Corrected parameter count: **~67M** (was 132M)
- ✅ Updated attribution: **AION Analytics**
- ✅ GitHub ↔ HuggingFace fully synchronized

**New Tags:**
- text-classification, financial-sentiment, financial-news, indian-finance, stock-market
- market-intelligence, sector-analysis, taxonomy-driven, financial-ai, open-source, production-ready

**Commit:** "Update model card with optimized 15 tags and AION Analytics attribution"

### 2026-03-28

**Taxonomy Integration Complete**

- ✅ gift_nifty_gap.py integrated with taxonomy confidence
- ✅ nifty_open_predictor.py reads taxonomy fields from Redis
- ✅ BASE_FEATURES updated with taxonomy_confidence, taxonomy_weighted_macro
- ✅ Backfill complete: 994,760 headlines classified (93.3% coverage)
- ✅ Keyword refinements: gov_digital_india, micro_ipl_season, sector_it_currency_tailwind
- ✅ New keywords added: iran war, strait of hormuz, oil supply disruption

**ClickHouse Universe**

- Total classified: 994,760 (93.3% coverage)
- Matched events: 64,770 (6.5% match rate)
- Unique events: 47

### 2026-03-27

**Backfill Execution**

- ✅ backfill_taxonomy_overnight.py executed
- ✅ 420,000 headlines processed
- ✅ Checkpoint system fixed (bytes serialization bug resolved)

### 2026-03-26

**Taxonomy Enhancement**

- ✅ Added 14 oil/commodity keyword variants
- ✅ global_crude_surge, global_crude_collapse events expanded

---

## 📧 Support

- **Email:** aionlabs@tutamail.com
- **GitHub:** https://github.com/AION-Analytics
- **HuggingFace:** https://huggingface.co/aion-analytics/aion-sentiment-in-v3

---

*Built for the Indian financial community*

**Last Updated:** 2026-03-29 00:00 IST

**GitHub ↔ HuggingFace Sync:** ✅ Fully Synchronized
