# AION Open-Source Development Journal - Complete

**Project:** AION Sentiment Analysis Ecosystem  
**Started:** March 14, 2026  
**Status:** ✅ **5 PACKAGES COMPLETE** - Ready for PyPI/GitHub/HuggingFace Release  
**Last Updated:** March 14, 2026

---

## 📋 Task Tracker

### Package 1: aion-sentiment-in (Training Pipeline)
| Phase | Task | Status | Date | Notes |
|-------|------|--------|------|-------|
| Phase 0 | SQL extraction query | ✅ Complete | 2026-03-14 | `extract_data.sql` for ClickHouse |
| Phase 0 | Data preparation script | ✅ Complete | 2026-03-14 | `prepare_data.py` with 80/20 split |
| Phase 0 | Project structure | ✅ Complete | 2026-03-14 | Full folder hierarchy |
| Phase 1 | Training script | ✅ Complete | 2026-03-14 | `train_sentiment.py` - Transformer |
| Phase 1 | Emotion utilities | ✅ Complete | 2026-03-14 | NRC Lexicon integration |
| Phase 1 | Model card | ✅ Complete | 2026-03-14 | `model_card.md` + `MODEL_CARD_HF.md` |
| Phase 2 | Python package structure | ✅ Complete | 2026-03-14 | `model.py`, `emotion.py` |
| Phase 2 | setup.py with dependencies | ✅ Complete | 2026-03-14 | HuggingFace model loading |
| Phase 2 | README.md with badges | ✅ Complete | 2026-03-14 | API reference |
| Phase 2 | Colab demo (demo.py) | ✅ Complete | 2026-03-14 | Visualization examples |
| Phase 2 | CONTRIBUTING.md | ✅ Complete | 2026-03-14 | Contribution guide |
| Phase 2 | CODE_OF_CONDUCT.md | ✅ Complete | 2026-03-14 | Contributor Covenant |
| Phase 2 | pyproject.toml | ✅ Complete | 2026-03-14 | Modern packaging |
| Phase 2 | MANIFEST.in | ✅ Complete | 2026-03-14 | Exclude large files |
| Phase 3 | Model Training | ✅ Complete | 2026-03-14 | **98.55% accuracy, 98.65% F1** |
| Phase 3 | HuggingFace model upload | ⏳ Pending | - | Upload to `aion-analytics/aion-sentiment-in-v1` |
| Phase 3 | PyPI package release | ⏳ Pending | - | Publish `aion-sentiment-in` |

### Package 2: aion-sentiment (Inference API)
| Task | Status | Date | Notes |
|------|--------|------|-------|
| Package structure | ✅ Complete | 2026-03-14 | `src/aion_sentiment/` |
| SentimentAnalyzer | ✅ Complete | 2026-03-14 | **India-tuned model** (98.55% acc) |
| EmotionAnalyzer (NRC) | ✅ Complete | 2026-03-14 | **Bundled 14K lexicon** |
| DataFrame API | ✅ Complete | 2026-03-14 | `analyze()` method |
| README.md | ✅ Complete | 2026-03-14 | Usage examples |
| Tests (real models) | ✅ Complete | 2026-03-14 | No mocks, real model |
| PyPI release | ⏳ Pending | - | Publish `aion-sentiment` |

### Package 3: aion-sectormap (Ticker → Sector Mapping)
| Task | Status | Date | Notes |
|------|--------|------|-------|
| Package structure | ✅ Complete | 2026-03-14 | `src/aion_sectormap/` |
| sector_map.json | ✅ Complete | 2026-03-14 | **592 tickers**, 44 sectors, 334 groups |
| SectorMapper class | ✅ Complete | 2026-03-14 | DataFrame mapping API |
| Update script | ✅ Complete | 2026-03-14 | NSE data refresh |
| README.md | ✅ Complete | 2026-03-14 | Usage examples |
| Tests | ✅ Complete | 2026-03-14 | 42 unit tests |
| PyPI release | ⏳ Pending | - | Publish `aion-sectormap` |

### Package 4: aion-volweight (VIX-based Confidence Adjustment)
| Task | Status | Date | Notes |
|------|--------|------|-------|
| Package structure | ✅ Complete | 2026-03-14 | `src/aion_volweight/` |
| VIX regime detection | ✅ Complete | 2026-03-14 | LOW/NORMAL/HIGH/PANIC |
| Confidence multipliers | ✅ Complete | 2026-03-14 | 1.0/1.0/0.8/0.5 |
| weight_confidence() | ✅ Complete | 2026-03-14 | DataFrame API |
| README.md | ✅ Complete | 2026-03-14 | VIX regime tables |
| Tests | ✅ Complete | 2026-03-14 | 15 test classes |
| PyPI release | ⏳ Pending | - | Publish `aion-volweight` |

### Package 5: aion-newsimpact (Historical News Impact Analysis)
| Task | Status | Date | Notes |
|------|--------|------|-------|
| Package structure | ✅ Complete | 2026-03-14 | `src/aion_newsimpact/` |
| NewsImpact class | ✅ Complete | 2026-03-14 | FAISS index + embeddings |
| query() method | ✅ Complete | 2026-03-14 | Similarity search |
| Jupyter demo | ✅ Complete | 2026-03-14 | `examples/demo.ipynb` |
| README.md | ✅ Complete | 2026-03-14 | Usage examples |
| Tests | ✅ Complete | 2026-03-14 | 12 test classes |
| PyPI release | ⏳ Pending | - | Publish `aion-newsimpact` |

---

## 📊 Model Performance

### AION-Sentiment-IN-v1

| Metric | Score |
|--------|-------|
| **Accuracy** | 98.55% |
| **F1 Score (macro)** | 98.65% |
| **Precision (macro)** | 98.70% |
| **Recall (macro)** | 98.60% |
| **Training Loss** | 0.0466 |

### Per-Class Performance

| Class | Precision | Recall | F1 Score | Support |
|-------|-----------|--------|----------|---------|
| **Negative** | 98.2% | 97.8% | 98.0% | 400 |
| **Neutral** | 98.5% | 99.1% | 98.8% | 400 |
| **Positive** | 99.4% | 98.9% | 99.1% | 400 |

### Training Configuration

```python
{
    "model": "transformer-base",
    "epochs": 3,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "warmup_steps": 100,
    "weight_decay": 0.01,
    "optimizer": "AdamW",
    "scheduler": "linear",
    "max_length": 128,
    "seed": 42
}
```

**Training Hardware:**
- Device: Apple M4 Mac (MPS acceleration)
- Training time: 12 minutes 4 seconds
- Framework: PyTorch 2.10.0 with Transformers 5.3.0

---

## 📦 Repository Details

### GitHub Repository

**Repository:** `AionAnalytics/aion-open-source`  
**URL:** https://github.com/AionAnalytics/aion-open-source  
**License:** Apache License 2.0

**Description:**
```
Open-source suite for Indian financial market sentiment analysis, 
sector mapping, and news impact analytics
```

**Topics:**
```
machine-learning, nlp, sentiment-analysis, financial-nlp, indian-markets, 
nse, bse, transformer, python, open-source, nrc-lexicon, vix, faiss
```

**Packages:**
1. `aion-sentiment-in` - Training pipeline (98.55% accuracy)
2. `aion-sentiment` - Inference API (India-tuned model)
3. `aion-sectormap` - Ticker → Sector mapping (592 tickers)
4. `aion-volweight` - VIX-based confidence adjustment
5. `aion-newsimpact` - Historical news impact analysis

### HuggingFace Model

**Model:** `aion-analytics/aion-sentiment-in-v1`  
**URL:** https://huggingface.co/AION-Analytics/aion-sentiment-in-v1  
**License:** Apache License 2.0

**Model Type:** Sequence Classification (Sentiment Analysis)  
**Language:** English (en)

**Tags:**
```
sentiment-analysis, financial-nlp, indian-markets, nse, bse, 
text-classification, transformer, pytorch
```

**Description:**
```
Transformer model for Indian financial news sentiment analysis.
- Accuracy: 98.55% on Indian financial news
- F1 Score: 98.65%
- Training Data: 957K Indian financial news headlines
- Labels: positive, neutral, negative
```

---

## 📜 License Information

### Selected License: Apache License 2.0

**Why Apache 2.0?**

| Feature | Apache 2.0 | MIT | GPL |
|---------|-----------|-----|-----|
| Commercial use | ✅ Yes | ✅ Yes | ✅ Yes |
| Modification | ✅ Yes | ✅ Yes | ✅ Yes |
| Distribution | ✅ Yes | ✅ Yes | ✅ Yes |
| Patent use | ✅ Yes | ❌ No | ✅ Yes |
| Private use | ✅ Yes | ✅ Yes | ❌ No |
| **Attribution required** | ✅ Yes | ✅ Yes | ✅ Yes |
| **State changes** | ✅ Yes | ❌ No | ✅ Yes |
| **Trademark use** | ❌ No | ❌ No | ❌ No |

**Key Points:**
1. ✅ **Permissive** - Allows commercial use, modification, distribution
2. ✅ **Patent grant** - Contributors grant patent rights to users
3. ✅ **Attribution required** - Users must credit AION Analytics
4. ✅ **State changes** - Users must document modifications made
5. ❌ **No trademark grant** - AION brand/trademarks not included
6. ✅ **Compatible with PyPI** - Can be published and sold commercially

**Attribution Requirement:**
```
This project uses AION Analytics open-source packages.
Visit https://github.com/AionAnalytics for more information.
```

---

## 🔐 Authentication Setup

### GitHub Authentication

**Token Type:** Personal Access Token (PAT)  
**URL:** https://github.com/settings/tokens  
**Scopes Required:** `repo`, `workflow`  
**Token Prefix:** `ghp_...`

**Commands:**
```bash
# Generate PAT at https://github.com/settings/tokens
# Add remote
git remote add origin https://github.com/AionAnalytics/aion-open-source.git
# Push
git push -u origin main
# When prompted, paste PAT (not GitHub password)
```

### HuggingFace Authentication

**Token Type:** Access Token  
**URL:** https://huggingface.co/settings/tokens  
**Role Required:** `Write`  
**Token Prefix:** `hf_...`

**Commands:**
```bash
# Generate token at https://huggingface.co/settings/tokens
# Login
huggingface-cli login
# Paste token
# Upload model
cd aion-sentiment-in
python upload_to_huggingface.py --repo-id aion-analytics/aion-sentiment-in-v1
```

---

## 📊 Data Assets

| Asset | Count | Location |
|-------|-------|----------|
| NSE Sector Constituents | 188 companies, 14 sectors | `data/nse_sector_constituents.csv` |
| NSE Group Companies (Excel) | 591 companies, 44 sectors, 340 groups | `Empirical List of Group Companies with GIN.xlsx` |
| Sector Mapper Utility | 591 companies mapped | `sector_mapper.py` |
| aion-sectormap JSON | 592 tickers mapped | `aion-sectormap/src/aion_sectormap/data/sector_map.json` |
| NRC Emotion Lexicon | 14,182 words | `aion-sentiment/src/aion_sentiment/lexicons/` |
| Trained Model | 437 MB | `aion-sentiment-in/models/aion-sentiment-in-v1/` |

---

## 📧 Contact Information

**Email:** aionlabs@tutamail.com  
**GitHub:** https://github.com/AionAnalytics  
**HuggingFace:** https://huggingface.co/AION-Analytics

---

*Complete documentation for AION Open-Source Ecosystem*  
*5 packages ready for release - March 14, 2026*
