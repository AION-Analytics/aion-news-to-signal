# =============================================================================
# AION Taxonomy - Confidence Computation
# =============================================================================
# Copyright (c) 2026 AION Contributors
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
# =============================================================================
"""
Confidence Computation - Blending multiple confidence components.

This module provides functionality to compute overall confidence by blending
taxonomy match, model probability, data quality, and agreement scores.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default weights for confidence components
DEFAULT_WEIGHTS = {
    'model_probability': 0.4,
    'taxonomy_match': 0.3,
    'data_quality': 0.2,
    'agreement_score': 0.1,
}


def compute_confidence(
    taxonomy_match: float,
    data_quality: float = 0.9,
    model_probability: Optional[float] = None,
    agreement_score: Optional[float] = None,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Compute overall confidence from multiple components.

    Uses weighted linear combination of confidence components.

    Args:
        taxonomy_match: Score from event classification (0-1).
        data_quality: Data quality score (0-1). Default 0.9.
        model_probability: Probability from sentiment model (0-1). Optional.
        agreement_score: Agreement between taxonomy and model (0-1). Optional.
        weights: Component weights. Uses DEFAULT_WEIGHTS if None.

    Returns:
        Overall confidence score (0-1).

    Example:
        >>> confidence = compute_confidence(
        ...     taxonomy_match=0.85,
        ...     data_quality=0.9,
        ...     model_probability=0.92,
        ...     agreement_score=1.0
        ... )
        >>> print(f"Confidence: {confidence:.2%}")
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    # Normalize weights
    total_weight = sum(weights.values())
    if total_weight == 0:
        logger.warning("All weights are zero, using equal weights")
        weights = {k: 1.0 / len(weights) for k in weights}
    else:
        weights = {k: v / total_weight for k, v in weights.items()}

    # Build component list
    components = []

    # Taxonomy match (always present)
    components.append(('taxonomy_match', taxonomy_match, weights.get('taxonomy_match', 0.25)))

    # Data quality (always present)
    components.append(('data_quality', data_quality, weights.get('data_quality', 0.25)))

    # Model probability (optional)
    if model_probability is not None:
        components.append(('model_probability', model_probability, weights.get('model_probability', 0.25)))
    else:
        # Redistribute weight if model probability not available
        remaining_weight = weights.get('model_probability', 0.25)
        for i, (name, value, weight) in enumerate(components):
            components[i] = (name, value, weight + remaining_weight / len(components))

    # Agreement score (optional)
    if agreement_score is not None:
        components.append(('agreement_score', agreement_score, weights.get('agreement_score', 0.25)))
    else:
        # Redistribute weight if agreement score not available
        remaining_weight = weights.get('agreement_score', 0.25)
        for i, (name, value, weight) in enumerate(components):
            components[i] = (name, value, weight + remaining_weight / len(components))

    # Compute weighted sum
    confidence = sum(value * weight for name, value, weight in components)

    # Clamp to [0, 1]
    confidence = max(0.0, min(1.0, confidence))

    logger.debug(
        f"Confidence: {confidence:.3f} (components: {[f'{n}={v:.2f}*{w:.2f}' for n, v, w in components]})"
    )

    return confidence


def compute_agreement_score(
    taxonomy_signal: float,
    model_label: str,
    model_confidence: float,
    threshold: float = 0.5,
) -> float:
    """
    Compute agreement score between taxonomy signal and model prediction.

    Args:
        taxonomy_signal: Signal from taxonomy (-1 to 1, negative=negative, positive=positive).
        model_label: Model's predicted label ('positive', 'neutral', 'negative').
        model_confidence: Model's confidence (0-1).
        threshold: Threshold for considering signal as positive/negative.

    Returns:
        Agreement score (0-1). 1.0 = full agreement, 0.0 = full disagreement.

    Example:
        >>> agreement = compute_agreement_score(0.6, 'positive', 0.85)
        >>> print(f"Agreement: {agreement:.2f}")
    """
    # Convert taxonomy signal to direction
    if taxonomy_signal > threshold:
        taxonomy_direction = 'positive'
    elif taxonomy_signal < -threshold:
        taxonomy_direction = 'negative'
    else:
        taxonomy_direction = 'neutral'

    # Check agreement
    if taxonomy_direction == model_label:
        # Full agreement
        agreement = 1.0
    elif taxonomy_direction == 'neutral' or model_label == 'neutral':
        # Partial agreement if one is neutral
        agreement = 0.5
    else:
        # Disagreement
        agreement = 0.0

    # Weight by model confidence
    agreement = agreement * model_confidence + (1 - model_confidence) * 0.5

    logger.debug(
        f"Agreement: {agreement:.3f} (taxonomy: {taxonomy_direction}, model: {model_label})"
    )

    return agreement


def compute_confidence_with_bounds(
    confidence: float,
    min_confidence: float = 0.0,
    max_confidence: float = 1.0,
) -> float:
    """
    Apply confidence bounds.

    Args:
        confidence: Raw confidence score.
        min_confidence: Minimum allowed confidence.
        max_confidence: Maximum allowed confidence.

    Returns:
        Bounded confidence score.
    """
    return max(min_confidence, min(max_confidence, confidence))
