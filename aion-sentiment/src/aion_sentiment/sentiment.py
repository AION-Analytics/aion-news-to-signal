# =============================================================================
# AION Sentiment Analysis - Unified Multi-Task Analyzer
# =============================================================================
# Copyright (c) 2026 AION Open Source Contributors
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# AION Open Source Project - Financial News Sentiment Analysis
# =============================================================================
"""
Unified Multi-Task Sentiment Analyzer for AION.

DistilBERT encoder with 4 task heads:
    1. Sentiment (3-class: negative/neutral/positive)
    2. Event classification (95 Indian market events)
    3. Macro signal (regression: -1 to +1)
    4. Sector impacts (32 NSE sectors)

Trained on 42,014 Indian financial news headlines with taxonomy-corrected labels.
Temperature-scaled confidence (T=1.5) for calibrated probabilities.

===========================================================================
TROUBLESHOOTING: News Sentiment Issues
===========================================================================

If a headline is getting wrong sentiment (e.g., POSITIVE for negative news):

1. THIS FILE: src/aion_sentiment/sentiment.py
   - SentimentAnalyzer.predict() applies inference-time override for 11 negative events
   - Override: if macro < -0.2 and event in NEGATIVE_EVENTS → force negative
   - Version: check __version__ in __init__.py (should be >= 0.2.1)

2. MODEL FILES:
   https://huggingface.co/AION-Analytics/aion-sentiment-unified-v1/
   - pytorch_model.bin, config.json, event_mapping.json, sector_order.json

3. CRAWLER (where live news sentiment is computed):
   /Users/lokeshgupta/projects/aion_algo_trading/src/zerodha/crawlers/gift_nifty_gap.py
   - _unified_analysis() line ~430: same override logic

4. DOWNSTREAM (reads sentiment from Redis):
   /Users/lokeshgupta/projects/aion_algo_trading/src/aion_ML/models/predictors/nifty_open_predictor.py
   - _collect_news_sentiment_from_redis() line ~151

5. KNOWN ISSUE TRACKING:
   - GitHub: https://github.com/AION-Analytics/aion-news-to-signal/issues/1
   - HF: https://huggingface.co/AION-Analytics/aion-sentiment-unified-v1/discussions/1
"""

import torch
import os
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from typing import Optional, List, Dict, Union
import logging
import json

from .utils import get_device

logger = logging.getLogger(__name__)


class MultiTaskModel(nn.Module):
    """Shared DistilBERT encoder + 4 task heads."""

    def __init__(
        self,
        base_model_name: str = "distilbert-base-uncased",
        num_events: int = 95,
        num_sectors: int = 32,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model_name)
        hidden_size = self.encoder.config.hidden_size
        self.dropout = nn.Dropout(dropout)

        self.sentiment_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 3),
        )
        self.event_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_events),
        )
        self.macro_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 4, 1),
        )
        self.sector_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_sectors),
        )

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> dict:
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = self.dropout(outputs.last_hidden_state[:, 0, :])
        return {
            "sentiment_logits": self.sentiment_head(cls),
            "event_logits": self.event_head(cls),
            "macro_pred": self.macro_head(cls).squeeze(-1),
            "sector_pred": self.sector_head(cls),
        }


class SentimentAnalyzer:
    """
    Unified multi-task sentiment analyzer for Indian financial news.

    Analyzes headlines with 4 outputs:
        - Sentiment (negative/neutral/positive with temperature-calibrated confidence)
        - Event classification (95 taxonomy events)
        - Macro signal (market impact: -1 to +1)
        - Sector impacts (32 NSE sectors)

    Model: DistilBERT base uncased, trained on 42,014 headlines.
    Temperature: 1.5 (calibrated confidence scores)

    Example:
        >>> analyzer = SentimentAnalyzer()
        >>> result = analyzer.predict("Rupee strengthens to 84 per USD")
        >>> print(result['sentiment'])  # negative
        >>> print(result['sector_impacts']['IT'])  # -0.34 (hurts exporters)
    """

    # Inference-time override for high-impact negative events (v1.0.1)
    # Bypasses broken sentiment head for known negative events
    NEGATIVE_EVENTS = {
        "global_crude_surge", "global_war_escalation", "macro_cpi_spike",
        "global_recession_fear", "sector_oil_inventory_build", "global_sanctions",
        "macro_inr_depreciation", "macro_rbi_repo_hike", "global_shipping_disruption",
        "global_vix_spike", "macro_gdp_downside"
    }

    LABEL_MAP = {0: 'negative', 1: 'neutral', 2: 'positive'}
    TEMPERATURE = 1.5  # Temperature scaling for calibrated confidence

    def __init__(
        self,
        model_name: str = "aion-analytics/aion-sentiment-unified-v1",
        device: Optional[str] = None
    ) -> None:
        self.model_name = model_name
        self.device = get_device() if device is None else device

        logger.info(f"Loading unified model '{model_name}' on {self.device}")
        try:
            # Check if model_name is a local directory path
            if os.path.isdir(model_name):
                # Load from local path directly — no torch.hub, no download, no cache
                logger.info(f"Loading from local path: {model_name}")
                self.model = MultiTaskModel(num_events=95, num_sectors=32)
                state_dict = torch.load(
                    os.path.join(model_name, "model.pt"),
                    map_location=self.device,
                    weights_only=True
                )
                self.model.load_state_dict(state_dict)

                # Load metadata from local files
                with open(os.path.join(model_name, "config.json")) as f:
                    cfg = json.load(f)
                self.event_mapping = {int(k): v for k, v in cfg.get('id2label', {}).items()}
                self.sector_cols = cfg.get('sector_cols', [])

                # Load tokenizer from local path
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            else:
                # Load from HuggingFace Hub (original behaviour)
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = MultiTaskModel(num_events=95, num_sectors=32)
                state_dict = torch.hub.load_state_dict_from_url(
                    f"https://huggingface.co/{model_name}/resolve/main/pytorch_model.bin",
                    map_location=self.device
                )
                self.model.load_state_dict(state_dict)

                # Load metadata
                try:
                    import requests
                    cfg = requests.get(
                        f"https://huggingface.co/{model_name}/resolve/main/config.json"
                    ).json()
                    self.event_mapping = cfg.get('id2label', {})
                    self.sector_cols = cfg.get('sector_cols', [])
                except Exception:
                    self.event_mapping = {}
                    self.sector_cols = []

            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Model loaded: 95 events, 32 sectors on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def predict(self, texts: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
        """
        Predict sentiment, event, macro, and sector impacts for text(s).

        Returns dict (single) or list of dicts with keys:
            - sentiment: 'negative' | 'neutral' | 'positive'
            - sentiment_score: calibrated confidence (temperature-scaled)
            - event_id: predicted event string
            - event_confidence: float
            - macro_signal: float (-1 to +1)
            - sector_impacts: dict of sector -> impact score
        """
        if isinstance(texts, str):
            texts = [texts]
            single = True
        else:
            single = False

        if not texts:
            raise ValueError("Input texts cannot be empty")

        results = []
        for text in texts:
            if not text or not str(text).strip():
                results.append({
                    'sentiment': 'neutral', 'sentiment_score': 0.5,
                    'event_id': '', 'event_confidence': 0.0,
                    'macro_signal': 0.0, 'sector_impacts': {}
                })
                continue

            inputs = self.tokenizer(
                text, return_tensors='pt', truncation=True, max_length=128
            )
            inputs = {k: v for k, v in inputs.items() if k != 'token_type_ids'}

            with torch.no_grad():
                out = self.model(**inputs)

            # Sentiment with temperature scaling
            sent_logits = out['sentiment_logits'] / self.TEMPERATURE
            sent_probs = torch.softmax(sent_logits, dim=1)
            sent_label = torch.argmax(out['sentiment_logits'], dim=1).item()
            confidence = sent_probs.max().item()

            # Event
            event_logits = out['event_logits'] / self.TEMPERATURE
            event_probs = torch.softmax(event_logits, dim=1)
            event_id = torch.argmax(out['event_logits'], dim=1).item()
            event_conf = event_probs.max().item()
            event_name = self.event_mapping.get(str(event_id), f"event_{event_id}")

            # Macro
            macro = out['macro_pred'].item()

            # Sector impacts
            sector_vals = out['sector_pred'].squeeze(0).cpu().tolist()
            if self.sector_cols:
                sector_impacts = dict(zip(self.sector_cols, sector_vals))
            else:
                sector_impacts = {f"sector_{i}": v for i, v in enumerate(sector_vals)}

            sentiment = self.LABEL_MAP.get(sent_label, 'neutral')

            # Override: force negative for high-impact negative events
            if (macro < -0.2) and (event_name in self.NEGATIVE_EVENTS):
                sentiment = 'negative'
                confidence = max(0.7, confidence)

            results.append({
                'sentiment': sentiment,
                'sentiment_score': confidence,
                'event_id': event_name,
                'event_confidence': event_conf,
                'macro_signal': macro,
                'sector_impacts': sector_impacts,
            })

        return results[0] if single else results

    def predict_batch(self, texts: List[str], batch_size: int = 8) -> List[Dict]:
        """Batch prediction for memory efficiency."""
        return self.predict(texts)

    def get_sentiment_score(self, text: str) -> float:
        """Get continuous sentiment score (-1 to +1)."""
        result = self.predict(text)
        label = result['sentiment']
        conf = result['sentiment_score']
        if label == 'positive':
            return conf
        elif label == 'negative':
            return -conf
        return 0.0

    def __repr__(self) -> str:
        return f"SentimentAnalyzer(model='{self.model_name}', device='{self.device}')"
