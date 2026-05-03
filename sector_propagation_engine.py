#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str((ROOT / "aion_taxonomy" / "src").resolve()))

from aion_taxonomy.pipeline import TaxonomyPipeline  # noqa: E402


TAXONOMY_PATH = ROOT / "aion_taxonomy" / "taxonomy_india_v2_calibrated.yaml"
CAUSE_EFFECT_RULES_PATH = (
    ROOT / "aion_taxonomy" / "cause_effect_rules_v3.yaml"
    if (ROOT / "aion_taxonomy" / "cause_effect_rules_v3.yaml").exists()
    else (
        ROOT / "aion_taxonomy" / "cause_effect_rules_v2.yaml"
        if (ROOT / "aion_taxonomy" / "cause_effect_rules_v2.yaml").exists()
        else ROOT / "aion_taxonomy" / "cause_effect_rules_v1.yaml"
    )
)
SECTOR_ORDER_PATH = ROOT / "models" / "aion_sentiment_unified_v4_1" / "sector_order.json"
HISTORICAL_LABELED_PATH = ROOT / "real_headlines_labeled_v2.csv"

WEATHER_EVENT_PATTERNS = {
    "heatwave": [r"\bheatwave\b", r"\bextreme heat\b", r"\brecord temperature\b"],
    "extreme heat": [r"\bextreme heat\b", r"\bbrutal heat\b", r"\bscorching heat\b"],
    "record temperature": [r"\brecord temperature\b", r"\brecord heat\b"],
    "unseasonal rainfall": [r"\bunseasonal rain(?:fall)?\b", r"\boff[- ]season rain\b"],
    "unseasonal rain": [r"\bunseasonal rain(?:fall)?\b", r"\buntimely rain\b"],
    "hailstorm": [r"\bhailstorm\b", r"\bhail\b"],
    "excess rain": [r"\bexcess rain(?:fall)?\b", r"\bheavy rain(?:fall)?\b", r"\bdownpour\b"],
    "excess rainfall": [r"\bexcess rain(?:fall)?\b", r"\bexcess rainfall\b"],
    "heavy rainfall": [r"\bheavy rain(?:fall)?\b", r"\btorrential rain\b"],
    "torrential rain": [r"\btorrential rain\b", r"\brelentless rain\b"],
    "heavy downpour": [r"\bheavy downpour\b", r"\bintense downpour\b"],
    "western disturbance": [r"\bwestern disturbance\b"],
    "floods": [r"\bfloods?\b", r"\bflooding\b", r"\bflash floods?\b"],
    "landslides": [r"\blandslides?\b"],
    "cloudburst": [r"\bcloudburst\b"],
    "drought": [r"\bdrought\b", r"\bdry spell\b", r"\bscanty rainfall\b", r"\brainfall deficit\b"],
    "deficient monsoon": [r"\bdeficient monsoon\b", r"\bbelow normal monsoon\b"],
    "cyclone": [r"\bcyclone\b", r"\bcyclonic storm\b", r"\blandfall\b"],
    "cyclonic storm": [r"\bcyclonic storm\b", r"\bdeep depression\b"],
    "storm surge": [r"\bstorm surge\b", r"\bsea surge\b"],
    "normal monsoon": [r"\bnormal monsoon\b", r"\bgood monsoon\b", r"\babove normal rainfall\b"],
    "dry winter": [r"\bdry winter\b", r"\bsnow deficit\b"],
    "cold wave": [r"\bcold wave\b", r"\bfrost\b"],
    "earthquake": [r"\bearthquake\b", r"\bseismic shock\b"],
}

CROP_PATTERNS = {
    "wheat": [r"\bwheat\b"],
    "rabi crop": [r"\brabi\b"],
    "apple": [r"\bapple(?:s)?\b"],
    "stone fruit": [r"\bstone fruit\b", r"\bpeach(?:es)?\b", r"\bplum(?:s)?\b"],
    "horticulture": [r"\bhorticulture\b", r"\borchard(?:s)?\b"],
    "paddy": [r"\bpaddy\b"],
    "rice": [r"\brice\b"],
    "kharif crop": [r"\bkharif\b"],
    "tomato": [r"\btomato(?:es)?\b"],
    "onion": [r"\bonion(?:s)?\b"],
    "potato": [r"\bpotato(?:es)?\b"],
    "vegetables": [r"\bvegetable(?:s)?\b"],
    "sugar": [r"\bsugar\b", r"\bsugarcane\b"],
    "cotton": [r"\bcotton\b", r"\bkapas\b"],
    "pulses": [r"\bpulses?\b", r"\bdal\b"],
    "turmeric": [r"\bturmeric\b", r"\bhaldi\b"],
    "soybean": [r"\bsoybean\b", r"\bsoy\b"],
    "shrimp": [r"\bshrimp\b", r"\bprawn\b", r"\baquaculture\b"],
}

COMMODITY_PATTERNS = {
    **CROP_PATTERNS,
    "non-basmati rice": [r"\bnon[- ]?basmati rice\b"],
}

POLICY_ACTION_PATTERNS = {
    "export ban": [r"\bexport ban\b", r"\bbanned exports?\b", r"\bexports? (?:are )?banned\b"],
    "export restriction": [r"\bexport restriction\b", r"\brestricted exports?\b", r"\bcurbs? on exports?\b"],
    "minimum export price": [r"\bminimum export price\b", r"\bmep\b"],
    "export duty": [r"\bexport duty\b", r"\bexport tax\b", r"\bduty on exports?\b"],
}

SEVERITY_PATTERNS = {
    "moderate": [r"\bmoderate\b", r"\bpatchy\b", r"\blocali[sz]ed\b", r"\bpartial\b"],
    "severe": [
        r"\bsevere\b", r"\bheavy damage\b", r"\bstandstill\b", r"\bshutdown\b",
        r"\bdisrupted\b", r"\bmajor\b", r"\bwidespread\b", r"\bhard hit\b",
    ],
    "extreme": [
        r"\bextreme\b", r"\bdevastating\b", r"\bcatastrophic\b", r"\brecord[- ]breaking\b",
        r"\bworst\b", r"\bthreefold\b", r"\bcollapsed\b", r"\ball[- ]time low\b",
    ],
}

DURATION_PATTERNS = {
    "> 6 months": [
        r"\b(?:more than|over)\s+6\s+months\b",
        r"\b(?:more than|over)\s+six\s+months\b",
        r"\bsix[- ]month\b",
        r"\bmonths[- ]long\b",
        r"\bprolonged\b",
        r"\bextended\b",
        r"\blong[- ]running\b",
    ],
}

REGION_PATTERNS = {
    "Punjab": [r"\bpunjab\b"],
    "Haryana": [r"\bharyana\b"],
    "Uttar Pradesh": [r"\buttar pradesh\b"],
    "Madhya Pradesh": [r"\bmadhya pradesh\b"],
    "Rajasthan": [r"\brajasthan\b"],
    "Himachal Pradesh": [r"\bhimachal pradesh\b", r"\bhimachal\b"],
    "Jammu & Kashmir": [r"\bjammu(?:\s*&\s*|\s+and\s+)?kashmir\b", r"\bj&k\b"],
    "Uttarakhand": [r"\buttarakhand\b"],
    "West Bengal": [r"\bwest bengal\b", r"\bhaldia\b"],
    "Assam": [r"\bassam\b"],
    "Odisha": [r"\bodisha\b", r"\bparadeep\b"],
    "Maharashtra": [r"\bmaharashtra\b", r"\bjnpa\b", r"\bnhava sheva\b", r"\bmumbai\b"],
    "Karnataka": [r"\bkarnataka\b"],
    "Telangana": [r"\btelangana\b"],
    "Andhra Pradesh": [r"\bandhra pradesh\b", r"\bvisakhapatnam\b", r"\bvizag\b", r"\bkakinada\b"],
    "Gujarat": [r"\bgujarat\b", r"\bmundra\b", r"\bkandla\b"],
    "Tamil Nadu": [r"\btamil nadu\b", r"\bchennai\b"],
    "Kerala": [r"\bkerala\b"],
    "Sikkim": [r"\bsikkim\b"],
}

MONTH_MAP = {
    month.lower(): month
    for month in [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
}

CAUSE_SECTOR_TO_MODEL_WEIGHTS: dict[str, dict[str, float]] = {
    "Agriculture & Allied": {
        "FMCG": 0.35,
        "Fertilizer": 0.30,
        "Automobile and Auto Components": 0.10,
        "Consumer Services": 0.10,
        "Financial Services": 0.10,
        "Transportation": 0.05,
    },
    "Agriculture & Horticulture": {
        "FMCG": 0.30,
        "Fertilizer": 0.20,
        "Transportation": 0.20,
        "Consumer Services": 0.15,
        "Diversified": 0.15,
    },
    "Automobile and Auto Components": {"Automobile and Auto Components": 1.0},
    "FMCG": {"FMCG": 1.0},
    "Consumer Services": {"Consumer Services": 1.0},
    "Financial Services": {"Financial Services": 0.7, "Banks": 0.2, "NBFC": 0.1},
    "Construction": {"Construction": 0.6, "Construction Materials": 0.2, "Capital Goods": 0.2},
    "Power": {"Power": 0.7, "Utilities": 0.3},
    "Energy": {"Energy": 0.6, "Oil, Gas & Consumable Fuels": 0.4},
    "Consumer Durables": {"Consumer Durables": 1.0},
    "Transportation": {"Transportation": 0.7, "Aviation": 0.3},
    "Fertilizer": {"Fertilizer": 1.0},
    "Cement": {"Cement": 1.0},
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s&]+", " ", text)
    return " ".join(text.split())


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalize_text(text))


def match_labels(text: str, patterns: dict[str, list[str]]) -> list[str]:
    normalized = normalize_text(text)
    matched: list[str] = []
    for label, label_patterns in patterns.items():
        if any(re.search(pattern, normalized) for pattern in label_patterns):
            matched.append(label)
    return matched


def extract_months(text: str, published_at: str | None = None) -> list[str]:
    normalized = normalize_text(text)
    months = [pretty for slug, pretty in MONTH_MAP.items() if re.search(rf"\b{slug}\b", normalized)]
    if not months and published_at:
        try:
            parsed = pd.to_datetime(published_at)
            months = [parsed.strftime("%B")]
        except Exception:
            pass
    return months


@dataclass
class RuleMatch:
    rule_id: str
    score: float
    matched_fields: dict[str, list[str]]
    rule: dict[str, Any]
    matched_field_count: int
    defined_field_count: int


def canonical_value(value: str) -> str:
    value = normalize_text(value)
    value = value.replace("rainfall", "rain")
    value = value.replace("exports", "export")
    value = value.replace("restrictions", "restriction")
    return value


def match_condition_values(observed_values: list[str], rule_values: list[str]) -> list[str]:
    canonical_rules = {canonical_value(value): value for value in rule_values}
    overlaps: list[str] = []
    for observed in observed_values:
        observed_key = canonical_value(observed)
        if observed_key in canonical_rules:
            overlaps.append(observed)
    return overlaps


class CauseEffectRuleEngine:
    def __init__(self, rules_path: Path, sector_order: list[str]) -> None:
        payload = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        self.metadata = payload.get("metadata", {})
        self.rules = payload.get("cause_effect_rules", [])
        self.sector_order = sector_order

    def extract_conditions(self, headline: str, published_at: str | None = None) -> dict[str, list[str]]:
        return {
            "weather_type": match_labels(headline, WEATHER_EVENT_PATTERNS),
            "crop_type": match_labels(headline, CROP_PATTERNS),
            "commodity": match_labels(headline, COMMODITY_PATTERNS),
            "region": match_labels(headline, REGION_PATTERNS),
            "month": extract_months(headline, published_at=published_at),
            "severity": match_labels(headline, SEVERITY_PATTERNS),
            "policy_action": match_labels(headline, POLICY_ACTION_PATTERNS),
            "duration": match_labels(headline, DURATION_PATTERNS),
        }

    def match(self, headline: str, published_at: str | None = None) -> RuleMatch | None:
        observed = self.extract_conditions(headline, published_at=published_at)
        best: RuleMatch | None = None
        hard_required_fields = {"weather_type", "policy_action"}
        for rule in self.rules:
            condition = rule.get("condition", {})
            matched_fields: dict[str, list[str]] = {}
            hard_hits = 0
            hard_total = 0
            optional_hits = 0
            optional_total = 0
            defined_field_count = 0

            for field, raw_values in condition.items():
                rule_values = [str(item) for item in raw_values]
                if not rule_values:
                    continue
                if any(canonical_value(value) == "any" for value in rule_values):
                    matched_fields[field] = ["any"]
                    continue
                defined_field_count += 1
                overlaps = match_condition_values(observed.get(field, []), rule_values)
                matched_fields[field] = overlaps
                if field in hard_required_fields:
                    hard_total += 1
                    if not overlaps:
                        hard_hits = -1
                        break
                    hard_hits += 1
                else:
                    optional_total += 1
                    if overlaps:
                        optional_hits += 1

            if hard_hits < 0:
                continue
            if optional_total > 0 and optional_hits == 0:
                continue

            matched_field_count = max(hard_hits, 0) + optional_hits
            coverage_ratio = matched_field_count / max(defined_field_count, 1)
            score = min(1.0, 0.3 + 0.15 * max(hard_hits, 0) + 0.1 * optional_hits + 0.02 * defined_field_count)
            if best is None or (
                coverage_ratio,
                matched_field_count,
                defined_field_count,
                score,
            ) > (
                best.matched_field_count / max(best.defined_field_count, 1),
                best.matched_field_count,
                best.defined_field_count,
                best.score,
            ):
                best = RuleMatch(
                    rule_id=rule["id"],
                    score=score,
                    matched_fields=matched_fields,
                    rule=rule,
                    matched_field_count=matched_field_count,
                    defined_field_count=defined_field_count,
                )
        return best

    def to_sector_vector(self, propagation: list[dict[str, Any]]) -> dict[str, float]:
        vector = {sector: 0.0 for sector in self.sector_order}
        for item in propagation:
            cause_sector = item["sector"]
            mapping = CAUSE_SECTOR_TO_MODEL_WEIGHTS.get(cause_sector, {})
            if not mapping:
                continue
            for sector, weight in mapping.items():
                vector[sector] += float(item["impact"]) * weight
        return {sector: max(-1.0, min(1.0, value)) for sector, value in vector.items()}

    def propagation_timeline(self, match: RuleMatch) -> list[dict[str, Any]]:
        return [
            {
                "rule_id": match.rule_id,
                "sector": item["sector"],
                "impact": float(item["impact"]),
                "lag_days": int(item["lag_days"]),
                "rationale": item["rationale"],
            }
            for item in match.rule.get("propagation", [])
        ]


class EventHistoryModel:
    def __init__(self, historical_csv: Path) -> None:
        self.transitions: dict[str, Counter[str]] = defaultdict(Counter)
        self.token_event_counts: dict[str, Counter[str]] = defaultdict(Counter)
        self.event_counts: Counter[str] = Counter()
        self.total_rows = 0
        if historical_csv.exists():
            self._fit(historical_csv)

    def _fit(self, historical_csv: Path) -> None:
        df = pd.read_csv(historical_csv, usecols=["headline", "event_id"], low_memory=False)
        df = df[df["event_id"].fillna("") != ""].copy()
        previous_event: str | None = None
        for row in df.to_dict(orient="records"):
            event_id = str(row["event_id"])
            headline = str(row["headline"])
            self.event_counts[event_id] += 1
            self.total_rows += 1
            for token in set(tokenize(headline)):
                self.token_event_counts[token][event_id] += 1
            if previous_event is not None:
                self.transitions[previous_event][event_id] += 1
            previous_event = event_id

    def transition_score(self, previous_event: str | None, candidate_event: str) -> float:
        if not previous_event or previous_event not in self.transitions:
            return 0.0
        total = sum(self.transitions[previous_event].values())
        if total == 0:
            return 0.0
        return self.transitions[previous_event][candidate_event] / total

    def token_pmi_score(self, headline: str, candidate_event: str) -> float:
        if self.total_rows == 0 or self.event_counts[candidate_event] == 0:
            return 0.0
        scores: list[float] = []
        for token in set(tokenize(headline)):
            token_total = sum(self.token_event_counts[token].values())
            joint = self.token_event_counts[token][candidate_event]
            if token_total == 0 or joint == 0:
                continue
            p_token = token_total / self.total_rows
            p_event = self.event_counts[candidate_event] / self.total_rows
            p_joint = joint / self.total_rows
            scores.append(math.log2(p_joint / (p_token * p_event)))
        if not scores:
            return 0.0
        return sum(scores) / len(scores)


class SectorPropagationEngine:
    def __init__(
        self,
        taxonomy_path: Path = TAXONOMY_PATH,
        cause_effect_rules_path: Path = CAUSE_EFFECT_RULES_PATH,
        sector_order_path: Path = SECTOR_ORDER_PATH,
        historical_labeled_path: Path = HISTORICAL_LABELED_PATH,
    ) -> None:
        self.sector_order = json.loads(sector_order_path.read_text(encoding="utf-8"))
        self.taxonomy_pipeline = TaxonomyPipeline(taxonomy_path=str(taxonomy_path))
        self.cause_effect = CauseEffectRuleEngine(cause_effect_rules_path, self.sector_order)
        self.history = EventHistoryModel(historical_labeled_path)

    def taxonomy_sector_vector(self, taxonomy_result: dict[str, Any]) -> dict[str, float]:
        vector = {sector: 0.0 for sector in self.sector_order}
        for sector, payload in taxonomy_result.get("sector_signals", {}).items():
            vector[sector] = float(payload.get("sector_signal", 0.0))
        return vector

    def disambiguate_event(
        self,
        headline: str,
        base_event_id: str | None,
        candidate_events: list[str],
        previous_events: list[str] | None,
    ) -> tuple[str | None, dict[str, float]]:
        previous_event = previous_events[-1] if previous_events else None
        scores: dict[str, float] = {}
        for event_id in candidate_events:
            score = 0.0
            if base_event_id == event_id:
                score += 0.5
            score += 0.3 * self.history.transition_score(previous_event, event_id)
            score += 0.2 * max(self.history.token_pmi_score(headline, event_id), 0.0)
            scores[event_id] = score
        if not scores:
            return base_event_id, {}
        best_event = max(scores.items(), key=lambda item: item[1])[0]
        return best_event, scores

    def propagate(
        self,
        headline: str,
        published_at: str | None = None,
        previous_events: list[str] | None = None,
        event_prediction: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        taxonomy_result = self.taxonomy_pipeline.process(headline=headline, date=published_at)
        taxonomy_event = taxonomy_result.get("event", {})
        taxonomy_event_id = taxonomy_event.get("event_id")
        taxonomy_confidence = float(taxonomy_result.get("confidence", 0.0))

        if event_prediction:
            model_event_id = event_prediction.get("event_id")
            model_confidence = float(event_prediction.get("confidence", 0.0))
        else:
            model_event_id = taxonomy_event_id
            model_confidence = taxonomy_confidence

        rule_match = self.cause_effect.match(headline, published_at=published_at)
        weather_triggered = bool(rule_match and rule_match.score >= 0.5)

        candidate_events = [event_id for event_id in {taxonomy_event_id, model_event_id} if event_id]
        if weather_triggered and rule_match:
            candidate_events.append(rule_match.rule_id)
        resolved_event_id = model_event_id
        markov_scores: dict[str, float] = {}

        if model_confidence < 0.7 and candidate_events:
            resolved_event_id, markov_scores = self.disambiguate_event(
                headline=headline,
                base_event_id=model_event_id,
                candidate_events=candidate_events,
                previous_events=previous_events,
            )

        direct_vector = self.taxonomy_sector_vector(taxonomy_result)
        propagation_timeline: list[dict[str, Any]] = []
        propagated_vector = {sector: 0.0 for sector in self.sector_order}

        if weather_triggered and rule_match:
            propagation_timeline = self.cause_effect.propagation_timeline(rule_match)
            propagated_vector = self.cause_effect.to_sector_vector(propagation_timeline)

        combined_vector = {
            sector: max(-1.0, min(1.0, direct_vector[sector] + propagated_vector[sector]))
            for sector in self.sector_order
        }

        return {
            "headline": headline,
            "published_at": published_at,
            "taxonomy_event_id": taxonomy_event_id,
            "taxonomy_confidence": taxonomy_confidence,
            "model_event_id": model_event_id,
            "model_confidence": model_confidence,
            "resolved_event_id": resolved_event_id,
            "markov_scores": markov_scores,
            "weather_triggered": weather_triggered,
            "cause_effect_rule_id": rule_match.rule_id if rule_match and weather_triggered else None,
            "cause_effect_rule_score": round(rule_match.score, 6) if rule_match and weather_triggered else 0.0,
            "matched_rule_fields": rule_match.matched_fields if rule_match and weather_triggered else {},
            "cause_effect_rule_metadata": {
                "source": rule_match.rule.get("source"),
                "evidence": rule_match.rule.get("evidence"),
                "confidence": rule_match.rule.get("confidence"),
                "competitor_gain": rule_match.rule.get("competitor_gain", []),
            }
            if rule_match and weather_triggered
            else {},
            "taxonomy_macro_signal": taxonomy_result.get("macro_signal", 0.0),
            "direct_impact_vector": direct_vector,
            "propagated_impact_vector": propagated_vector,
            "combined_impact_vector": combined_vector,
            "propagation_timeline": propagation_timeline,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cause-effect sector propagation engine.")
    parser.add_argument("--headline", required=True)
    parser.add_argument("--published-at", default=None)
    parser.add_argument("--previous-events", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    previous_events = [item for item in args.previous_events.split(",") if item]
    engine = SectorPropagationEngine()
    result = engine.propagate(
        headline=args.headline,
        published_at=args.published_at,
        previous_events=previous_events,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
