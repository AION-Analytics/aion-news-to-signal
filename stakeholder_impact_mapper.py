#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from sector_propagation_engine import SectorPropagationEngine


ROOT = Path(__file__).resolve().parent
ALIGNED_DAILY = ROOT / "dataset" / "aligned_4factor_daily.csv"

GROUP_TO_SECTORS = {
    "NIFTYAUTO": ["Automobile and Auto Components"],
    "NIFTYBANK": ["Banks", "NBFC"],
    "NIFTYFIN": ["Financial Services", "Broking Company"],
    "NIFTYFMCG": ["FMCG", "Consumer Durables", "Consumer Services"],
    "NIFTYIT": ["IT"],
    "NIFTYMEDIA": ["Media, Entertainment & Publication", "Services"],
    "NIFTYMETAL": ["Metals & Mining", "Materials", "Chemicals", "Cement"],
    "NIFTYPHARMA": ["Healthcare"],
    "NIFTYPSUBANK": ["Banks"],
    "NIFTYREALTY": ["Realty", "Construction"],
    "NIFTYENERGY": ["Energy", "Oil, Gas & Consumable Fuels", "Power", "Utilities"],
    "NIFTYINFRA": ["Construction", "Construction Materials", "Capital Goods", "Transportation"],
    "NIFTYMNC": ["Diversified", "Manufacturing"],
    "NIFTY50": ["Diversified"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map sector impacts into stakeholder-specific views.")
    parser.add_argument("--headline", default=None)
    parser.add_argument("--published-at", default=None)
    parser.add_argument("--input-json", default=None)
    return parser.parse_args()


def build_hypergraph() -> dict[str, dict[str, float]]:
    df = pd.read_csv(ALIGNED_DAILY)
    cols = [column for column in df.columns if column.startswith("NIFTY")]
    corr = df[cols].corr().fillna(0.0)
    graph: dict[str, dict[str, float]] = {}
    for left in cols:
        graph[left] = {}
        for right in cols:
            if left == right:
                continue
            value = float(corr.loc[left, right])
            if abs(value) >= 0.25:
                graph[left][right] = value
    return graph


def sector_to_group_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for group, sectors in GROUP_TO_SECTORS.items():
        for sector in sectors:
            mapping[sector] = group
    return mapping


def second_order_effects(combined_vector: dict[str, float], graph: dict[str, dict[str, float]]) -> dict[str, float]:
    sector_group = sector_to_group_map()
    group_signals: dict[str, float] = {}
    for sector, value in combined_vector.items():
        group = sector_group.get(sector)
        if group is None:
            continue
        group_signals[group] = group_signals.get(group, 0.0) + value

    propagated_groups = {group: 0.0 for group in graph}
    for group, signal in group_signals.items():
        for neighbor, weight in graph.get(group, {}).items():
            propagated_groups[neighbor] += signal * weight * 0.25

    sector_effects = {sector: 0.0 for sector in combined_vector}
    for sector, group in sector_group.items():
        sector_effects[sector] = propagated_groups.get(group, 0.0)
    return sector_effects


def top_items(vector: dict[str, float], *, top_n: int = 5, positive: bool = True) -> list[dict[str, float]]:
    items = sorted(vector.items(), key=lambda item: item[1], reverse=positive)
    filtered = [item for item in items if item[1] > 0] if positive else [item for item in items if item[1] < 0]
    return [{"sector": sector, "impact": round(value, 4)} for sector, value in filtered[:top_n]]


def map_views(propagation_result: dict[str, Any]) -> dict[str, Any]:
    graph = build_hypergraph()
    direct = propagation_result["combined_impact_vector"]
    second_order = second_order_effects(direct, graph)
    rule_meta = propagation_result.get("cause_effect_rule_metadata", {}) or {}

    intermediary_sectors = {"Transportation", "Financial Services", "Broking Company", "FMCG", "Consumer Services", "Diversified"}
    trader_vector = {sector: direct.get(sector, 0.0) + second_order.get(sector, 0.0) for sector in intermediary_sectors}

    producer_winners = []
    producer_losers = []
    for item in propagation_result.get("propagation_timeline", []):
        row = {
            "stakeholder_sector": item["sector"],
            "impact": round(float(item["impact"]), 4),
            "lag_days": int(item["lag_days"]),
            "rationale": item["rationale"],
        }
        if item["impact"] >= 0:
            producer_winners.append(row)
        else:
            producer_losers.append(row)

    investor_vector = {sector: direct.get(sector, 0.0) + second_order.get(sector, 0.0) for sector in direct}

    fiscal_sectors = {"Financial Services", "Banks", "NBFC", "Construction", "Cement", "Realty", "Power", "Utilities", "IT"}
    fiscal_vector = {sector: investor_vector.get(sector, 0.0) for sector in fiscal_sectors}

    trade_sectors = {
        "Transportation",
        "Textiles",
        "Chemicals",
        "Consumer Durables",
        "FMCG",
        "Financial Services",
        "Oil, Gas & Consumable Fuels",
        "Materials",
    }
    trade_vector = {sector: investor_vector.get(sector, 0.0) for sector in trade_sectors}

    return {
        "producer_view": {
            "winners": producer_winners,
            "losers": producer_losers,
        },
        "trader_intermediary_view": {
            "winners": top_items(trader_vector, positive=True),
            "losers": top_items(trader_vector, positive=False),
            "second_order_effects": {k: round(v, 4) for k, v in trader_vector.items()},
        },
        "investor_view": {
            "top_risers": top_items(investor_vector, positive=True),
            "top_fallers": top_items(investor_vector, positive=False),
            "cascade_timeline": propagation_result.get("propagation_timeline", []),
        },
        "government_fiscal_view": {
            "opportunities": top_items(fiscal_vector, positive=True),
            "risks": top_items(fiscal_vector, positive=False),
            "rebuild_signals": [
                item
                for item in propagation_result.get("propagation_timeline", [])
                if item["sector"] in {"Construction", "Cement", "Power"}
            ],
        },
        "international_trade_view": {
            "opportunities": top_items(trade_vector, positive=True),
            "risks": top_items(trade_vector, positive=False),
            "competitor_gains": rule_meta.get("competitor_gain", []),
        },
    }


def main() -> None:
    args = parse_args()
    if args.input_json:
        propagation_result = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    elif args.headline:
        engine = SectorPropagationEngine()
        propagation_result = engine.propagate(args.headline, published_at=args.published_at)
    else:
        raise SystemExit("Provide --headline or --input-json")

    result = {
        "headline": propagation_result.get("headline"),
        "cause_effect_rule_id": propagation_result.get("cause_effect_rule_id"),
        "views": map_views(propagation_result),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
