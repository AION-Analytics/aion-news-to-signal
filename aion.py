#!/usr/bin/env python3
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from sector_propagation_engine import SectorPropagationEngine
from stakeholder_impact_mapper import map_views


ROOT = Path(__file__).resolve().parent
VIX_PATH = ROOT / "dataset" / "india_vix_daily_spot.csv"


class VIXOverlay:
    def __init__(self, csv_path: Path = VIX_PATH) -> None:
        self.df = pd.read_csv(csv_path)
        self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce").dt.normalize()
        self.df["vix_close"] = pd.to_numeric(self.df["vix_close"], errors="coerce")
        self.df = self.df.dropna(subset=["date", "vix_close"]).sort_values("date").reset_index(drop=True)

    def snapshot(self, published_at: str | None = None) -> dict[str, Any]:
        if self.df.empty:
            return {
                "date": None,
                "vix_close": None,
                "regime": "unknown",
                "toggle": "balanced",
                "positive_multiplier": 1.0,
                "negative_multiplier": 1.0,
            }
        if published_at:
            dt = pd.to_datetime(published_at, errors="coerce")
            if not pd.isna(dt):
                subset = self.df[self.df["date"] <= dt.normalize()]
                row = subset.iloc[-1] if not subset.empty else self.df.iloc[-1]
            else:
                row = self.df.iloc[-1]
        else:
            row = self.df.iloc[-1]
        value = float(row["vix_close"])
        if value < 15:
            regime = "low"
            toggle = "opportunity"
            pos_mult = 1.10
            neg_mult = 0.90
        elif value > 25:
            regime = "high"
            toggle = "adversity"
            pos_mult = 0.90
            neg_mult = 1.20
        else:
            regime = "normal"
            toggle = "balanced"
            pos_mult = 1.00
            neg_mult = 1.00
        return {
            "date": str(pd.Timestamp(row["date"]).date()),
            "vix_close": round(value, 4),
            "regime": regime,
            "toggle": toggle,
            "positive_multiplier": pos_mult,
            "negative_multiplier": neg_mult,
        }

    def apply(self, vector: dict[str, float], snapshot: dict[str, Any]) -> dict[str, float]:
        out: dict[str, float] = {}
        for sector, value in vector.items():
            value = float(value)
            if value > 0:
                adj = value * float(snapshot["positive_multiplier"])
            elif value < 0:
                adj = value * float(snapshot["negative_multiplier"])
            else:
                adj = 0.0
            out[sector] = round(max(-1.0, min(1.0, adj)), 4)
        return out


@lru_cache(maxsize=1)
def _engine() -> SectorPropagationEngine:
    return SectorPropagationEngine()


@lru_cache(maxsize=1)
def _vix() -> VIXOverlay:
    return VIXOverlay()


def _top_items(vector: dict[str, float], positive: bool, limit: int = 3) -> dict[str, float]:
    items = sorted(vector.items(), key=lambda item: item[1], reverse=positive)
    if positive:
        items = [item for item in items if item[1] > 0][:limit]
    else:
        items = [item for item in items if item[1] < 0][:limit]
    return {sector: round(float(value), 4) for sector, value in items}


def _bias_summary(
    top_positive: dict[str, float],
    top_negative: dict[str, float],
) -> dict[str, list[str]]:
    return {
        "positive_bias": list(top_positive.keys()),
        "negative_bias": list(top_negative.keys()),
    }


def analyze(headline: str, published_at: str | None = None) -> dict[str, Any]:
    engine = _engine()
    result = engine.propagate(headline, published_at=published_at)
    vix_snapshot = _vix().snapshot(published_at)
    post_vix_vector = _vix().apply(result["combined_impact_vector"], vix_snapshot)
    view_payload = dict(result)
    view_payload["combined_impact_vector"] = post_vix_vector
    views = map_views(view_payload)

    event = result.get("cause_effect_rule_id") or result.get("resolved_event_id")
    confidence = (
        float(result.get("cause_effect_rule_score", 0.0))
        if result.get("cause_effect_rule_id")
        else max(float(result.get("model_confidence", 0.0)), float(result.get("taxonomy_confidence", 0.0)))
    )
    top_positive = _top_items(post_vix_vector, positive=True)
    top_negative = _top_items(post_vix_vector, positive=False)

    return {
        "headline": headline,
        "event": event,
        "confidence": round(confidence, 4),
        "vix_regime": vix_snapshot["regime"],
        "sector_vector": post_vix_vector,
        "top_positive_sectors": top_positive,
        "top_negative_sectors": top_negative,
        "sector_directional_bias": _bias_summary(top_positive, top_negative),
        "stakeholder_views": views,
        "raw_assignment": {
            "resolved_event_id": result.get("resolved_event_id"),
            "cause_effect_rule_id": result.get("cause_effect_rule_id"),
            "weather_triggered": bool(result.get("weather_triggered")),
        },
    }


__all__ = ["analyze"]
