from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from huggingface_hub import snapshot_download
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .model_runtime import MultiTaskModel
from .sector_engine import CauseEffectRuleEngine, SectorPropagationEngine
from .stakeholder import map_views
from .taxonomy_impact import compute_all_sector_signals, get_macro_signal


PACKAGE_ROOT = files("aion")
MODEL_REPO_ID = "AION-Analytics/aion-news-to-signal"
BASE_MODEL_REPO_ID = "distilbert-base-uncased"
CAUSE_EFFECT_SUBDIR = "cause_effect_rule_classifier_v3"


def _cache_root() -> Path:
    if os.getenv("AION_CACHE_DIR"):
        return Path(os.getenv("AION_CACHE_DIR", "")).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "aion-news-to-signal"
    return Path.home() / ".cache" / "aion-news-to-signal"


def _local_files_only() -> bool:
    return os.getenv("AION_LOCAL_FILES_ONLY", "").strip().lower() in {"1", "true", "yes"}


def _explicit_model_snapshot_dir(repo_id: str) -> Path | None:
    env_keys = []
    if repo_id == MODEL_REPO_ID:
        env_keys.extend(["AION_MODEL_SNAPSHOT_DIR", "AION_NEWS_TO_SIGNAL_MODEL_DIR"])
    elif repo_id == BASE_MODEL_REPO_ID:
        env_keys.extend(["AION_BASE_MODEL_SNAPSHOT_DIR", "AION_DISTILBERT_SNAPSHOT_DIR"])
    for key in env_keys:
        raw = os.getenv(key, "").strip()
        if raw:
            return Path(raw).expanduser()
    return None


def _repo_cache_dir(repo_id: str) -> Path:
    return _cache_root() / "hf" / f"models--{repo_id.replace('/', '--')}"


def _required_patterns(repo_id: str, allow_patterns: list[str]) -> list[str]:
    if repo_id == MODEL_REPO_ID:
        return [
            "config.json",
            "event_mapping.json",
            "sector_order.json",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
            "pytorch_model.bin",
            f"{CAUSE_EFFECT_SUBDIR}/*",
        ]
    if repo_id == BASE_MODEL_REPO_ID:
        return [
            "config.json",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
            "__ANY_MODEL_FILE__",
        ]
    return allow_patterns


def _snapshot_complete(snapshot_dir: Path, repo_id: str, allow_patterns: list[str]) -> bool:
    if not snapshot_dir.exists():
        return False
    for pattern in _required_patterns(repo_id, allow_patterns):
        if pattern == "__ANY_MODEL_FILE__":
            if not (
                (snapshot_dir / "model.safetensors").exists()
                or (snapshot_dir / "pytorch_model.bin").exists()
            ):
                return False
            continue
        if pattern.endswith("/*"):
            subdir = snapshot_dir / pattern[:-2]
            if not subdir.is_dir() or not any(subdir.iterdir()):
                return False
        else:
            if not (snapshot_dir / pattern).exists():
                return False
    return True


def _best_local_snapshot(repo_id: str, allow_patterns: list[str]) -> Path | None:
    snapshots_dir = _repo_cache_dir(repo_id) / "snapshots"
    if not snapshots_dir.is_dir():
        return None
    candidates = [
        snap
        for snap in snapshots_dir.iterdir()
        if snap.is_dir() and _snapshot_complete(snap, repo_id, allow_patterns)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _resource_path(*parts: str) -> Any:
    node = PACKAGE_ROOT
    for part in parts:
        node = node.joinpath(part)
    return node


@dataclass
class ArtifactPaths:
    model_snapshot: Path
    base_model_snapshot: Path
    taxonomy_path: Path
    cause_rules_path: Path
    vix_path: Path
    aligned_daily_path: Path


def _download_snapshot(repo_id: str, allow_patterns: list[str]) -> Path:
    explicit_dir = _explicit_model_snapshot_dir(repo_id)
    if explicit_dir is not None:
        if _snapshot_complete(explicit_dir, repo_id, allow_patterns):
            return explicit_dir
        raise RuntimeError(
            f"Configured local snapshot directory for {repo_id} is incomplete: {explicit_dir}"
        )

    try:
        snapshot_dir = Path(
            snapshot_download(
                repo_id=repo_id,
                allow_patterns=allow_patterns,
                cache_dir=str(_cache_root() / "hf"),
                local_files_only=_local_files_only(),
            )
        )
        if _snapshot_complete(snapshot_dir, repo_id, allow_patterns):
            return snapshot_dir
        fallback = _best_local_snapshot(repo_id, allow_patterns)
        if fallback is not None:
            return fallback
        raise RuntimeError(
            f"Resolved snapshot for {repo_id} is incomplete: {snapshot_dir}"
        )
    except Exception as exc:
        fallback = _best_local_snapshot(repo_id, allow_patterns)
        if fallback is not None:
            return fallback
        mode = "offline cache" if _local_files_only() else "download"
        raise RuntimeError(
            f"Unable to resolve required model artifacts for {repo_id}. "
            f"Failed during {mode}. Set AION_LOCAL_FILES_ONLY=0 or ensure the cache exists."
        ) from exc


@lru_cache(maxsize=1)
def resolve_artifacts() -> ArtifactPaths:
    model_snapshot = _download_snapshot(
        MODEL_REPO_ID,
        [
            "README.md",
            "config.json",
            "event_mapping.json",
            "sector_order.json",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
            "pytorch_model.bin",
            f"{CAUSE_EFFECT_SUBDIR}/*",
        ],
    )
    base_model_snapshot = _download_snapshot(
        BASE_MODEL_REPO_ID,
        [
            "config.json",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
            "special_tokens_map.json",
            "model.safetensors",
            "pytorch_model.bin",
        ],
    )
    with as_file(_resource_path("taxonomy", "taxonomy_india_v2_calibrated.yaml")) as taxonomy_path, \
         as_file(_resource_path("taxonomy", "cause_effect_rules_v3.yaml")) as cause_rules_path, \
         as_file(_resource_path("data", "india_vix_daily_spot.csv")) as vix_path, \
         as_file(_resource_path("data", "aligned_4factor_daily.csv")) as aligned_daily_path:
        return ArtifactPaths(
            model_snapshot=model_snapshot,
            base_model_snapshot=base_model_snapshot,
            taxonomy_path=Path(taxonomy_path),
            cause_rules_path=Path(cause_rules_path),
            vix_path=Path(vix_path),
            aligned_daily_path=Path(aligned_daily_path),
        )


def _device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@dataclass
class ClassifierPrediction:
    label: str
    confidence: float
    top_labels: list[dict[str, float]]
    sector_vector: dict[str, float] | None = None
    macro_pred: float | None = None


class CauseEffectRuleClassifier:
    def __init__(self, model_dir: Path, device: torch.device) -> None:
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_dir), local_files_only=True)
        self.model.to(self.device)
        self.model.eval()
        label_map = json.loads((model_dir / "label_map.json").read_text(encoding="utf-8"))
        self.id2label = {int(k): v for k, v in label_map["id2label"].items()}

    def predict(self, headline: str, max_length: int = 96) -> ClassifierPrediction:
        inputs = self.tokenizer(headline, return_tensors="pt", truncation=True, max_length=max_length)
        inputs = {k: v.to(self.device) for k, v in inputs.items() if k != "token_type_ids"}
        with torch.no_grad():
            logits = self.model(**inputs).logits[0]
        probs = torch.softmax(logits, dim=-1).detach().cpu().numpy()
        best_idx = int(np.argmax(probs))
        order = list(np.argsort(probs)[::-1][:3])
        return ClassifierPrediction(
            label=self.id2label[best_idx],
            confidence=float(probs[best_idx]),
            top_labels=[{"label": self.id2label[int(idx)], "prob": round(float(probs[idx]), 4)} for idx in order],
        )


class UnifiedEventClassifier:
    def __init__(self, model_dir: Path, base_model_dir: Path, device: torch.device) -> None:
        self.device = device
        config = json.loads((model_dir / "config.json").read_text(encoding="utf-8"))
        event_mapping = json.loads((model_dir / "event_mapping.json").read_text(encoding="utf-8"))
        self.id2label = {int(k): v for k, v in event_mapping.items()}
        self.sector_order = json.loads((model_dir / "sector_order.json").read_text(encoding="utf-8"))
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True)
        self.model = MultiTaskModel(
            base_model_name=str(base_model_dir),
            num_events=int(config["num_events"]),
            num_sectors=int(config["num_sectors"]),
        )
        state_path = model_dir / "pytorch_model.bin"
        try:
            state = torch.load(state_path, map_location="cpu", weights_only=True)
        except TypeError:
            state = torch.load(state_path, map_location="cpu")
        self.model.load_state_dict(state)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, headline: str, max_length: int = 128) -> ClassifierPrediction:
        inputs = self.tokenizer(headline, return_tensors="pt", truncation=True, max_length=max_length)
        inputs = {k: v.to(self.device) for k, v in inputs.items() if k != "token_type_ids"}
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs["event_logits"][0]
        sector_logits = outputs["sector_pred"][0]
        macro_pred = float(outputs["macro_pred"][0].detach().cpu().item())
        probs = torch.softmax(logits, dim=-1).detach().cpu().numpy()
        best_idx = int(np.argmax(probs))
        order = list(np.argsort(probs)[::-1][:3])
        sector_values = sector_logits.detach().cpu().numpy().tolist()
        sector_vector = {
            sector: round(max(-1.0, min(1.0, float(value))), 4)
            for sector, value in zip(self.sector_order, sector_values)
        }
        return ClassifierPrediction(
            label=self.id2label[best_idx],
            confidence=float(probs[best_idx]),
            top_labels=[{"label": self.id2label[int(idx)], "prob": round(float(probs[idx]), 4)} for idx in order],
            sector_vector=sector_vector,
            macro_pred=macro_pred,
        )


class VIXOverlay:
    def __init__(self, csv_path: Path) -> None:
        self.df = pd.read_csv(csv_path)
        self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce").dt.normalize()
        self.df["vix_close"] = pd.to_numeric(self.df["vix_close"], errors="coerce")
        self.df = self.df.dropna(subset=["date", "vix_close"]).sort_values("date").reset_index(drop=True)

    def snapshot(self, published_at: str | None = None) -> dict[str, Any]:
        if self.df.empty:
            return {"date": None, "vix_close": None, "regime": "unknown", "toggle": "balanced", "positive_multiplier": 1.0, "negative_multiplier": 1.0}
        if published_at:
            dt = pd.to_datetime(published_at, errors="coerce")
            if not pd.isna(dt):
                if getattr(dt, "tzinfo", None) is not None:
                    dt = dt.tz_localize(None)
                subset = self.df[self.df["date"] <= dt.normalize()]
                row = subset.iloc[-1] if not subset.empty else self.df.iloc[-1]
            else:
                row = self.df.iloc[-1]
        else:
            row = self.df.iloc[-1]
        value = float(row["vix_close"])
        if value < 15:
            return {"date": str(pd.Timestamp(row["date"]).date()), "vix_close": round(value, 4), "regime": "low", "toggle": "opportunity", "positive_multiplier": 1.10, "negative_multiplier": 0.90}
        if value > 25:
            return {"date": str(pd.Timestamp(row["date"]).date()), "vix_close": round(value, 4), "regime": "high", "toggle": "adversity", "positive_multiplier": 0.90, "negative_multiplier": 1.20}
        return {"date": str(pd.Timestamp(row["date"]).date()), "vix_close": round(value, 4), "regime": "normal", "toggle": "balanced", "positive_multiplier": 1.00, "negative_multiplier": 1.00}

    def apply(self, vector: dict[str, float], snapshot: dict[str, Any]) -> dict[str, float]:
        out = {}
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


def _load_rule_lookup(rules_path: Path) -> dict[str, dict[str, Any]]:
    import yaml

    payload = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    return {rule["id"]: rule for rule in payload.get("cause_effect_rules", [])}


def _rule_vector(engine: CauseEffectRuleEngine, rule_lookup: dict[str, dict[str, Any]], rule_id: str) -> tuple[list[dict[str, Any]], dict[str, float]]:
    rule = rule_lookup[rule_id]
    timeline = [
        {
            "rule_id": rule_id,
            "sector": item["sector"],
            "impact": float(item["impact"]),
            "lag_days": int(item["lag_days"]),
            "rationale": item["rationale"],
        }
        for item in rule.get("propagation", [])
    ]
    return timeline, engine.to_sector_vector(timeline)


def _clamp_combined(direct_vector: dict[str, float], propagated_vector: dict[str, float]) -> dict[str, float]:
    return {
        sector: round(max(-1.0, min(1.0, float(direct_vector.get(sector, 0.0)) + float(propagated_vector.get(sector, 0.0)))), 4)
        for sector in direct_vector
    }


def _top_items(vector: dict[str, float], positive: bool, limit: int = 3) -> dict[str, float]:
    items = sorted(vector.items(), key=lambda item: item[1], reverse=positive)
    if positive:
        items = [item for item in items if item[1] > 0][:limit]
    else:
        items = [item for item in items if item[1] < 0][:limit]
    return {sector: round(float(value), 4) for sector, value in items}


_MARKET_CONTEXT_RE = re.compile(
    r"\b("
    r"rbi|sebi|nse|bse|nifty|sensex|banknifty|stock|stocks|share|shares|equity|bond|yield|"
    r"rupee|dollar|forex|currency|repo|rate|inflation|cpi|wpi|gdp|monetary|policy|"
    r"oil|crude|brent|wti|fuel|lpg|gas|png|cng|diesel|petrol|atf|power|electricity|coal|"
    r"bank|banks|nbfc|credit|loan|loans|lending|default|rating|downgrade|upgrade|"
    r"company|corporate|earnings|profit|profits|revenue|sales|results|filing|ipo|dividend|buyback|"
    r"merger|acquisition|deal|investment|fii|dii|promoter|auditor|director|"
    r"tax|gst|duty|tariff|import|imports|export|exports|subsidy|cabinet|ministry|government|"
    r"monsoon|drought|flood|heatwave|crop|commodity|commodities|metal|metals|pharma|it|auto|fmcg"
    r")\b",
    re.IGNORECASE,
)


def _has_market_context(headline: str) -> bool:
    return bool(_MARKET_CONTEXT_RE.search(headline or ""))


def _deterministic_macro_overlay(headline: str, sector_order: list[str]) -> dict[str, Any] | None:
    """Package-level guardrail for macro events the frozen classifier underspecifies.

    This keeps corrections in the plug-and-play package instead of in downstream
    crawlers. It does not modify model weights.
    """
    text = re.sub(r"\s+", " ", (headline or "").strip().lower())
    if not text:
        return None

    def vector_from(mapping: dict[str, float]) -> dict[str, float]:
        vector = {sector: 0.0 for sector in sector_order}
        for sector, impact in mapping.items():
            if sector in vector:
                vector[sector] = round(float(impact), 4)
        return vector

    lpg_hit = bool(
        re.search(
            r"\b(lpg|commercial lpg|bulk lpg|non[- ]domestic lpg|industrial lpg|cylinder|fuel price|atf|aviation turbine fuel|png|piped natural gas|cng)\b",
            text,
        )
    )
    price_hike_hit = bool(
        re.search(
            r"\b(hike|hikes|hiked|increase|increases|increased|raise|raises|raised|boost|boosts|surge|surges|climb|climbs|jump|jumps|spike|spikes|uptick|higher)\b",
            text,
        )
    )
    price_cut_hit = bool(
        re.search(
            r"\b(cut|cuts|reduced?|reduction|slash|slashes|lower|lowers|drop|drops|fall|falls|rollback|relief|ease|eases)\b",
            text,
        )
    )
    if lpg_hit and (price_hike_hit or price_cut_hit):
        hike_vector = {
            "Oil, Gas & Consumable Fuels": 1.0,
            "Energy": 0.519,
            "IT": 0.015,
            "Healthcare": -0.13,
            "Aviation": -0.621,
            "Transportation": -0.297,
            "Financial Services": -0.0227,
            "Banks": -0.021,
            "NBFC": -0.042,
            "Textiles": -0.72,
            "Chemicals": -0.62,
            "FMCG": -0.4,
            "Consumer Services": -0.55,
            "Metals & Mining": -0.35,
            "Construction Materials": -0.3,
            "Automobile and Auto Components": -0.4,
            "Capital Goods": -0.25,
            "Manufacturing": -0.3,
            "Consumer Durables": -0.25,
            "Cement": -0.35,
            "Fertilizer": -0.3,
        }
        if price_cut_hit and not price_hike_hit:
            hike_vector = {sector: -0.75 * impact for sector, impact in hike_vector.items()}
        return {
            "event": "fuel_price_policy_change",
            "confidence": 0.88,
            "macro_signal": 0.35 if price_hike_hit else -0.25,
            "sector_vector": vector_from(hike_vector),
            "assignment_type": "deterministic_macro_overlay",
        }

    geo_hit = bool(
        re.search(
            r"\b(iran|israel|lebanon|west asia|middle east|war|attack|attacks|invasion|conflict|military|bombing|strike|shelling|hostilities|missile|ceasefire|truce|peace talks?|peace offer|tensions?|geopolitical)\b",
            text,
        )
    )
    crude_hit = bool(re.search(r"\b(crude|oil|brent|wti)\b", text))
    crude_up_hit = bool(
        re.search(
            r"\b(jump|jumps|jumped|surge|surges|surged|spike|spikes|spiked|higher|above|rally|rallies|rise|rises|rose|climb|climbs|climbed|gain|gains|gained|push(?:es)? oil higher|no breakthrough|stall|stalls|stalled)\b",
            text,
        )
    )
    rate_hike_risk = bool(re.search(r"\b(fed|federal reserve).{0,40}\b(hik|tighten|hawkish)\b", text))
    dollar_risk = bool(re.search(r"\bdollar strengthens?\b|\bstronger dollar\b", text))
    failed_peace = bool(
        re.search(
            r"\b(no breakthrough|unacceptable|talks? falter|peace offer|disagree|tensions?|jitters?)\b",
            text,
        )
    )
    if not (geo_hit or (crude_hit and crude_up_hit) or rate_hike_risk or dollar_risk):
        return None

    event_id = "energy_supply_shock" if crude_hit and crude_up_hit else "geopolitical_conflict"
    if rate_hike_risk and geo_hit:
        event_id = "geopolitical_conflict"
    if dollar_risk and (geo_hit or failed_peace):
        event_id = "geopolitical_conflict"

    macro_signal = -0.32
    if event_id == "energy_supply_shock":
        vector = vector_from(
            {
                "Oil, Gas & Consumable Fuels": 0.625,
                "Energy": 0.36,
                "Aviation": -0.72,
                "Transportation": -0.54,
                "Chemicals": -0.465,
                "Fertilizer": -0.465,
                "Cement": -0.34,
                "Metals & Mining": -0.30,
                "Automobile and Auto Components": -0.28,
                "FMCG": -0.12,
                "Consumer Durables": -0.10,
            }
        )
        macro_signal = -0.38
    else:
        vector = vector_from(
            {
                "Oil, Gas & Consumable Fuels": 0.35,
                "Energy": 0.25,
                "IT": 0.15,
                "Healthcare": 0.10,
                "Aviation": -0.30,
                "Transportation": -0.20,
                "Metals & Mining": -0.15,
                "Automobile and Auto Components": -0.10,
                "Financial Services": -0.10,
                "Banks": -0.10,
                "NBFC": -0.10,
                "Consumer Durables": -0.05,
            }
        )
    return {
        "event": event_id,
        "confidence": 0.88,
        "macro_signal": macro_signal,
        "sector_vector": vector,
        "assignment_type": "deterministic_macro_overlay",
    }


def _taxonomy_vector_from_event(engine: SectorPropagationEngine, event_id: str, headline: str) -> tuple[dict[str, float], float]:
    event = engine.taxonomy_pipeline.get_event_details(event_id)
    vector = {sector: 0.0 for sector in engine.sector_order}
    if not event:
        return vector, 0.0
    event_payload = {"event_id": event_id, **event}
    macro_signal, _ = get_macro_signal(event_payload, headline)
    sector_signals = compute_all_sector_signals(macro_signal, event_payload, flip_threshold=engine.taxonomy_pipeline.flip_threshold)
    for sector, payload in sector_signals.items():
        if sector in vector:
            vector[sector] = round(float(payload.get("sector_signal", 0.0)), 4)
    return vector, float(macro_signal)


def _augment_producer_view(views: dict[str, Any], vector: dict[str, float], assignment_type: str) -> dict[str, Any]:
    producer = views["producer_view"]
    if producer.get("winners") or producer.get("losers"):
        return views
    sorted_pos = [(k, v) for k, v in sorted(vector.items(), key=lambda item: item[1], reverse=True) if v > 0][:2]
    sorted_neg = [(k, v) for k, v in sorted(vector.items(), key=lambda item: item[1]) if v < 0][:2]
    views["producer_view"] = {
        "winners": [{"stakeholder_sector": s, "impact": round(float(v), 4), "lag_days": 0, "rationale": f"Derived from {assignment_type} sector projection."} for s, v in sorted_pos],
        "losers": [{"stakeholder_sector": s, "impact": round(float(v), 4), "lag_days": 0, "rationale": f"Derived from {assignment_type} sector projection."} for s, v in sorted_neg],
    }
    return views


class LocalAIONPipeline:
    def __init__(self) -> None:
        artifacts = resolve_artifacts()
        device = _device()
        self.event_classifier = UnifiedEventClassifier(artifacts.model_snapshot, artifacts.base_model_snapshot, device)
        self.rule_classifier = CauseEffectRuleClassifier(artifacts.model_snapshot / CAUSE_EFFECT_SUBDIR, device)
        self.engine = SectorPropagationEngine(
            taxonomy_path=artifacts.taxonomy_path,
            cause_effect_rules_path=artifacts.cause_rules_path,
            sector_order_path=artifacts.model_snapshot / "sector_order.json",
            historical_labeled_path=None,
        )
        from . import stakeholder as stakeholder_module

        stakeholder_module.ALIGNED_DAILY = artifacts.aligned_daily_path
        self.rule_lookup = _load_rule_lookup(artifacts.cause_rules_path)
        self.vix = VIXOverlay(artifacts.vix_path)

    def analyze(self, headline: str, published_at: str | None = None) -> dict[str, Any]:
        headline = (headline or "").strip()
        if not headline:
            raise ValueError("headline is required")

        prediction = self.rule_classifier.predict(headline)
        event_prediction = self.event_classifier.predict(headline)
        base_result = self.engine.propagate(
            headline,
            published_at=published_at,
            event_prediction={"event_id": event_prediction.label, "confidence": event_prediction.confidence},
        )
        deterministic_rule_id = base_result.get("cause_effect_rule_id")
        deterministic_score = float(base_result.get("cause_effect_rule_score", 0.0))

        if prediction.label != "no_rule" and prediction.confidence >= 0.80:
            final_rule_id = prediction.label
            assignment_type = "classifier_rule"
            assignment_confidence = prediction.confidence
        elif deterministic_rule_id:
            final_rule_id = deterministic_rule_id
            assignment_type = "deterministic_rule"
            assignment_confidence = deterministic_score
        elif event_prediction.confidence >= 0.10:
            final_rule_id = "no_rule"
            assignment_type = "event_model_fallback"
            assignment_confidence = event_prediction.confidence
        elif base_result.get("taxonomy_event_id"):
            final_rule_id = "no_rule"
            assignment_type = "taxonomy_fallback"
            assignment_confidence = float(base_result.get("taxonomy_confidence", 0.0))
        else:
            final_rule_id = "no_rule"
            assignment_type = "no_match"
            assignment_confidence = 0.0

        if final_rule_id != "no_rule" and final_rule_id in self.rule_lookup:
            timeline, propagated_vector = _rule_vector(self.engine.cause_effect, self.rule_lookup, final_rule_id)
            pre_vix_vector = _clamp_combined(base_result["direct_impact_vector"], propagated_vector)
        elif assignment_type == "event_model_fallback":
            event_direct_vector, event_macro_signal = _taxonomy_vector_from_event(self.engine, event_prediction.label, headline)
            fallback_direct = event_direct_vector if any(abs(v) > 0 for v in event_direct_vector.values()) else (event_prediction.sector_vector or {sector: 0.0 for sector in self.engine.sector_order})
            timeline = []
            propagated_vector = {sector: 0.0 for sector in self.engine.sector_order}
            pre_vix_vector = _clamp_combined(fallback_direct, propagated_vector)
            base_result["taxonomy_macro_signal"] = event_macro_signal if event_macro_signal else float(event_prediction.macro_pred or 0.0)
        else:
            timeline = base_result.get("propagation_timeline", [])
            propagated_vector = {k: round(float(v), 4) for k, v in base_result["propagated_impact_vector"].items()}
            pre_vix_vector = {k: round(float(v), 4) for k, v in base_result["combined_impact_vector"].items()}

        vix_snapshot = self.vix.snapshot(published_at=published_at)
        post_vix_vector = self.vix.apply(pre_vix_vector, vix_snapshot)
        overlay = _deterministic_macro_overlay(headline, self.engine.sector_order)
        if overlay:
            final_rule_id = str(overlay["event"])
            assignment_type = str(overlay["assignment_type"])
            assignment_confidence = max(float(assignment_confidence), float(overlay["confidence"]))
            base_result["taxonomy_macro_signal"] = float(overlay["macro_signal"])
            post_vix_vector = self.vix.apply(overlay["sector_vector"], vix_snapshot)
            timeline = []
        elif (
            assignment_type in {"event_model_fallback", "taxonomy_fallback", "no_match"}
            and not _has_market_context(headline)
            and float(assignment_confidence) < 0.50
        ):
            final_rule_id = "no_rule"
            assignment_type = "no_match_non_financial_guard"
            assignment_confidence = 0.0
            base_result["taxonomy_macro_signal"] = 0.0
            post_vix_vector = {sector: 0.0 for sector in self.engine.sector_order}
            timeline = []
        view_payload = {
            **base_result,
            "cause_effect_rule_id": None if final_rule_id == "no_rule" else final_rule_id,
            "combined_impact_vector": post_vix_vector,
            "propagation_timeline": timeline,
        }
        views = map_views(view_payload)
        views = _augment_producer_view(views, post_vix_vector, assignment_type)
        if final_rule_id != "no_rule":
            event_value = final_rule_id
        elif assignment_type in {"no_match", "no_match_non_financial_guard"}:
            event_value = None
        else:
            event_value = base_result.get("resolved_event_id") or event_prediction.label

        return {
            "headline": headline,
            "event": event_value,
            "confidence": round(float(assignment_confidence), 4),
            "macro_signal": round(float(base_result.get("taxonomy_macro_signal", 0.0) or 0.0), 4),
            "vix_regime": vix_snapshot["regime"],
            "sector_vector": post_vix_vector,
            "top_positive_sectors": _top_items(post_vix_vector, positive=True),
            "top_negative_sectors": _top_items(post_vix_vector, positive=False),
            "trade_direction_signals": {
                "long": list(_top_items(post_vix_vector, positive=True).keys()),
                "short": list(_top_items(post_vix_vector, positive=False).keys()),
            },
            "stakeholder_views": views,
            "raw_assignment": {
                "assignment_type": assignment_type,
                "resolved_event_id": base_result.get("resolved_event_id"),
                "taxonomy_event_id": base_result.get("taxonomy_event_id"),
                "model_event_id": event_prediction.label,
                "cause_effect_rule_id": None if final_rule_id == "no_rule" else final_rule_id,
                "weather_triggered": bool(base_result.get("weather_triggered")),
            },
        }


@lru_cache(maxsize=1)
def get_pipeline() -> LocalAIONPipeline:
    return LocalAIONPipeline()


def analyze(headline: str, published_at: str | None = None) -> dict[str, Any]:
    return get_pipeline().analyze(headline, published_at=published_at)
