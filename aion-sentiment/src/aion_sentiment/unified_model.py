#!/usr/bin/env python3
"""
AION Unified Model for Indian Financial News Analysis.

Multi-task transformer with DistilBERT encoder and 4 task heads:
    1. Sentiment (3-class: negative/neutral/positive)
    2. Event classification (95 Indian market events)
    3. Macro signal (regression: -1 to +1)
    4. Sector impacts (32 NSE sectors)

Usage:
    from aion_sentiment import AIONUnifiedModel
    model = AIONUnifiedModel.from_pretrained("AION-Analytics/aion-sentiment-unified-v1")
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer, AutoConfig
from typing import Optional


class AIONUnifiedModel(nn.Module):
    """DistilBERT encoder + 4 task heads for Indian financial news analysis."""

    def __init__(
        self,
        base_model_name: str = "distilbert-base-uncased",
        num_events: int = 95,
        num_sectors: int = 32,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model_name)
        hidden = self.encoder.config.hidden_size  # 768

        self.dropout = nn.Dropout(dropout)

        self.sentiment_head = nn.Sequential(
            nn.Linear(hidden, hidden // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden // 2, 3),
        )
        self.event_head = nn.Sequential(
            nn.Linear(hidden, hidden // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden // 2, num_events),
        )
        self.macro_head = nn.Sequential(
            nn.Linear(hidden, hidden // 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden // 4, 1),
        )
        self.sector_head = nn.Sequential(
            nn.Linear(hidden, hidden // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden // 2, num_sectors),
        )

    @classmethod
    def from_pretrained(cls, model_name_or_path: str):
        """Load model from HuggingFace Hub or local path."""
        config = AutoConfig.from_pretrained(model_name_or_path)
        num_events = getattr(config, "num_events", 95)
        num_sectors = getattr(config, "num_sectors", 32)
        base = getattr(config, "base_model", "distilbert-base-uncased")

        model = cls(base_model_name=base, num_events=num_events, num_sectors=num_sectors)

        # Load weights
        from huggingface_hub import hf_hub_download
        try:
            state_path = hf_hub_download(model_name_or_path, "pytorch_model.bin")
        except Exception:
            state_path = hf_hub_download(model_name_or_path, "model.pt")

        state_dict = torch.load(state_path, map_location="cpu", weights_only=True)
        model.load_state_dict(state_dict)
        return model

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> dict:
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = self.dropout(outputs.last_hidden_state[:, 0, :])
        return {
            "sentiment_logits": self.sentiment_head(cls),
            "event_logits": self.event_head(cls),
            "macro_pred": self.macro_head(cls).squeeze(-1),
            "sector_pred": self.sector_head(cls),
        }

    def predict(self, text: str, temperature: float = 1.5) -> dict:
        """Run inference on a single headline with temperature-scaled confidence."""
        tokenizer = AutoTokenizer.from_pretrained("AION-Analytics/aion-sentiment-unified-v1")
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v for k, v in inputs.items() if k != "token_type_ids"}

        with torch.no_grad():
            out = self(**inputs)

        # Sentiment with temperature scaling
        sent_logits = out["sentiment_logits"] / temperature
        sent_probs = torch.softmax(sent_logits, dim=1)
        sent_label = torch.argmax(out["sentiment_logits"], dim=1).item()
        labels = ["negative", "neutral", "positive"]

        # Event
        event_logits = out["event_logits"] / temperature
        event_probs = torch.softmax(event_logits, dim=1)
        event_id = torch.argmax(out["event_logits"], dim=1).item()

        # Macro
        macro = out["macro_pred"].item()

        # Sector
        sector_vals = out["sector_pred"].squeeze(0).cpu().tolist()

        return {
            "sentiment": labels[sent_label],
            "sentiment_confidence": sent_probs.max().item(),
            "event_id": event_id,
            "event_confidence": event_probs.max().item(),
            "macro_signal": macro,
            "sector_impacts": sector_vals,
        }


if __name__ == "__main__":
    model = AIONUnifiedModel.from_pretrained("AION-Analytics/aion-sentiment-unified-v1")
    print("Model loaded from HuggingFace")

    tests = [
        "RBI cuts repo rate by 25 bps to boost growth",
        "Rupee strengthens to 84 per USD on FII inflows",
        "Sensex crashes 800 points on global selloff",
        "Reliance reports record quarterly profit",
    ]

    print(f"\n{'Headline':60s} | {'Sentiment':10s} | {'Conf':5s} | {'Macro':6s} | Top Sectors")
    print("-" * 120)

    for h in tests:
        r = model.predict(h)
        sectors = sorted(enumerate(r["sector_impacts"]), key=lambda x: -abs(x[1]))[:3]
        sec_str = ", ".join(f"s{i}={v:+.2f}" for i, v in sectors)
        print(f"{h:60s} | {r['sentiment']:10s} | {r['sentiment_confidence']:.2f} | {r['macro_signal']:+6.3f} | {sec_str}")
