#!/usr/bin/env python3
"""
Multi-Task Model for AION News Classification.

Shared DistilBERT encoder with 4 task heads:
  1. Sentiment (3-class classification) — trains on ALL rows
  2. Event (136-class classification) — trains on matched rows only
  3. Macro signal (regression) — trains on matched rows only
  4. Sector impacts (32-dim regression) — trains on matched rows only
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer


class MultiTaskModel(nn.Module):
    """Shared encoder + 4 task heads."""

    def __init__(
        self,
        base_model_name: str = "distilbert-base-uncased",
        num_events: int = 136,
        num_sectors: int = 32,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model_name)
        hidden_size = self.encoder.config.hidden_size  # 768 for DistilBERT

        self.dropout = nn.Dropout(dropout)

        # Task heads
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

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_embedding = outputs.last_hidden_state[:, 0, :]  # [CLS] token
        cls_embedding = self.dropout(cls_embedding)

        return {
            "sentiment_logits": self.sentiment_head(cls_embedding),
            "event_logits": self.event_head(cls_embedding),
            "macro_pred": self.macro_head(cls_embedding).squeeze(-1),
            "sector_pred": self.sector_head(cls_embedding),
        }


# ── Quick smoke test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Building MultiTaskModel...")
    model = MultiTaskModel()
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Total params:     {total_params:,}")
    print(f"  Trainable params: {trainable_params:,}")

    # Forward pass test
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    texts = ["Stock market rises on strong earnings", "Company files for bankruptcy"]
    tokens = tokenizer(texts, padding=True, return_tensors="pt")

    with torch.no_grad():
        out = model(**tokens)

    print(f"\nForward pass output shapes:")
    for k, v in out.items():
        print(f"  {k}: {v.shape}")

    print("\n✅ Model builds and runs correctly.")
