# =============================================================================
# AION Taxonomy - Impact Computation
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
Impact Computation - Macro and sector signal calculation.

This module provides functionality to compute macro signals and sector-specific
signals based on classified events and context keywords.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Impact level keywords for contextual modifiers
IMPACT_LEVEL_KEYWORDS = {
    'severe': ['surprise', 'unexpected', 'larger than expected', 'shock', 'dramatic', 'sharp', 'major'],
    'mild': ['as expected', 'in line', 'slight', 'modest', 'gradual', 'minor'],
}


def get_macro_signal(
    event: Dict[str, Any],
    headline: str,
    context_keywords: Optional[List[str]] = None,
) -> Tuple[float, str]:
    """
    Compute macro signal from event classification.

    Args:
        event: Classified event dictionary from EventClassifier.classify().
        headline: Original headline text for context analysis.
        context_keywords: Optional additional context keywords.

    Returns:
        Tuple of (macro_signal, impact_level):
            - macro_signal: Float between -1 and 1
            - impact_level: Selected impact level ('mild', 'normal', or 'severe')

    Example:
        >>> event = classifier.classify("RBI unexpectedly hikes repo rate")
        >>> signal, level = get_macro_signal(event, headline)
        >>> print(f"Signal: {signal}, Level: {level}")
    """
    base_impact = event.get('base_impact', {})
    default_impact = event.get('default_impact', 'normal')
    market_weight = event.get('market_weight', 1.0)
    contextual_modifiers = event.get('contextual_modifiers', [])

    # Determine impact level from context
    impact_level = _select_impact_level(
        headline, default_impact, contextual_modifiers
    )

    # Get base impact value for selected level
    impact_value = base_impact.get(impact_level, 0.0)

    # Compute macro signal
    macro_signal = impact_value * market_weight

    # Clamp to [-1, 1]
    macro_signal = max(-1.0, min(1.0, macro_signal))

    logger.debug(f"Macro signal: {macro_signal:.3f} (impact: {impact_level}, weight: {market_weight})")

    return macro_signal, impact_level


def _select_impact_level(
    headline: str,
    default_impact: str,
    contextual_modifiers: List[Dict[str, Any]],
) -> str:
    """
    Select impact level based on context keywords.

    Args:
        headline: Original headline text.
        default_impact: Default impact level from event.
        contextual_modifiers: List of contextual modifier rules from event.

    Returns:
        Selected impact level ('mild', 'normal', or 'severe').
    """
    normalized_headline = headline.lower()

    # Check contextual modifiers first (event-specific rules)
    for modifier in contextual_modifiers:
        keywords = modifier.get('keywords', [])
        impact_level = modifier.get('impact_level')

        if impact_level and any(kw.lower() in normalized_headline for kw in keywords):
            logger.debug(f"Contextual modifier matched: {impact_level}")
            return impact_level

    # Check general impact level keywords
    severe_matches = sum(
        1 for kw in IMPACT_LEVEL_KEYWORDS['severe']
        if kw in normalized_headline
    )
    mild_matches = sum(
        1 for kw in IMPACT_LEVEL_KEYWORDS['mild']
        if kw in normalized_headline
    )

    # Decide based on matches
    if severe_matches > mild_matches:
        return 'severe'
    elif mild_matches > severe_matches:
        return 'mild'
    else:
        return default_impact


def get_sector_signal(
    macro_signal: float,
    event: Dict[str, Any],
    sector_id: str,
    flip_threshold: float = 0.35,
) -> Optional[Dict[str, Any]]:
    """
    Compute sector-specific signal from macro signal.

    Args:
        macro_signal: Computed macro signal (-1 to 1).
        event: Classified event dictionary.
        sector_id: Sector ID to compute signal for.
        flip_threshold: Threshold below which sector can flip macro sentiment.

    Returns:
        Dictionary containing:
            - sector_signal: Float signal for this sector
            - multiplier: Applied multiplier
            - bias: Applied bias ('aligned', 'inverse', or 'neutral')
            - rationale: Explanation from taxonomy
        Returns None if sector not present in event.sector_impacts.

    Example:
        >>> result = get_sector_signal(0.5, event, 'Banks')
        >>> print(result['sector_signal'])
    """
    sector_impacts = event.get('sector_impacts', {})

    # Check if sector has specific impact
    if sector_id not in sector_impacts:
        return None

    sector_config = sector_impacts[sector_id]
    multiplier = sector_config.get('multiplier', 1.0)
    bias = sector_config.get('bias', 'aligned')
    rationale = sector_config.get('rationale', '')

    # Determine bias sign
    if bias == 'aligned':
        bias_sign = 1.0
    elif bias == 'inverse':
        bias_sign = -1.0
    else:  # neutral
        bias_sign = 0.0

    # Compute sector signal
    sector_signal = macro_signal * multiplier * bias_sign

    # Apply flip rule for weak macro signals with inverse bias
    # If macro signal is weak and bias is inverse, sector may have opposite sentiment
    if abs(macro_signal) < flip_threshold and bias == 'inverse':
        # Allow sector to have positive sentiment even if macro is slightly negative
        # This is handled by the bias already, but we can soften the signal
        sector_signal = sector_signal * 0.5

    # Clamp to [-1, 1]
    sector_signal = max(-1.0, min(1.0, sector_signal))

    logger.debug(
        f"Sector signal for {sector_id}: {sector_signal:.3f} "
        f"(macro: {macro_signal:.3f}, multiplier: {multiplier}, bias: {bias})"
    )

    return {
        'sector_signal': sector_signal,
        'multiplier': multiplier,
        'bias': bias,
        'bias_sign': bias_sign,
        'rationale': rationale,
    }


def compute_all_sector_signals(
    macro_signal: float,
    event: Dict[str, Any],
    sector_ids: Optional[List[str]] = None,
    flip_threshold: float = 0.35,
) -> Dict[str, Dict[str, Any]]:
    """
    Compute signals for all sectors in the event.

    Args:
        macro_signal: Computed macro signal.
        event: Classified event dictionary.
        sector_ids: Optional list of sector IDs to compute. If None, uses all
                    sectors present in event.sector_impacts.
        flip_threshold: Threshold below which sector can flip macro sentiment.

    Returns:
        Dictionary mapping sector_id to signal details.
    """
    sector_impacts = event.get('sector_impacts', {})

    if sector_ids is None:
        sector_ids = list(sector_impacts.keys())

    results = {}
    for sector_id in sector_ids:
        signal = get_sector_signal(macro_signal, event, sector_id, flip_threshold=flip_threshold)
        if signal:
            results[sector_id] = signal

    return results
