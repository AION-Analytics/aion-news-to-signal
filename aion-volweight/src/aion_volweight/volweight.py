# Copyright 2026 AION Analytics
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
"""
VIX-based sentiment confidence adjustment module.

This module provides functionality to adjust sentiment confidence scores
based on market volatility regimes using the VIX (Volatility Index).

VIX Regime Classification:
    - LOW: VIX < 12 (Market complacency, full confidence)
    - NORMAL: 12 <= VIX < 15 (Typical market conditions, full confidence)
    - HIGH: 16 <= VIX < 25 (Elevated volatility, 20% confidence discount)
    - PANIC: VIX >= 25 (Market stress, 50% confidence discount)

Example:
    >>> from aion_volweight import adjust_confidence, get_regime
    >>>
    >>> # Get regime for current VIX
    >>> regime = get_regime(18.5)
    >>> print(f"Current regime: {regime}")
    HIGH
    >>>
    >>> # Adjust confidence score
    >>> adjusted = adjust_confidence(0.95, vix_value=18.5)
    >>> print(f"Adjusted confidence: {adjusted:.2f}")
    Adjusted confidence: 0.76
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union

import pandas as pd


class VIXRegime(str, Enum):
    """
    VIX volatility regime classification.

    Attributes:
        LOW: VIX < 12 - Market complacency, low volatility
        NORMAL: 12 <= VIX < 15 - Typical market conditions
        HIGH: 16 <= VIX < 25 - Elevated volatility, increased uncertainty
        PANIC: VIX >= 25 - Market stress, high volatility
    """

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    PANIC = "PANIC"


@dataclass(frozen=True)
class VIXRegimeConfig:
    """
    Configuration for VIX regime thresholds and confidence multipliers.

    This dataclass defines the boundaries and multipliers for each
    volatility regime. The default values are based on empirical
    analysis of market behavior.

    Attributes:
        low_threshold: Upper bound for LOW regime (exclusive)
        normal_threshold: Upper bound for NORMAL regime (exclusive)
        high_threshold: Upper bound for HIGH regime (exclusive)
        low_multiplier: Confidence multiplier for LOW regime
        normal_multiplier: Confidence multiplier for NORMAL regime
        high_multiplier: Confidence multiplier for HIGH regime
        panic_multiplier: Confidence multiplier for PANIC regime

    Example:
        >>> config = VIXRegimeConfig()
        >>> print(f"HIGH regime multiplier: {config.high_multiplier}")
        HIGH regime multiplier: 0.8
    """

    low_threshold: float = 12.0
    normal_threshold: float = 15.0
    high_threshold: float = 25.0
    low_multiplier: float = 1.0
    normal_multiplier: float = 1.0
    high_multiplier: float = 0.8
    panic_multiplier: float = 0.5

    def get_multiplier_for_regime(self, regime: VIXRegime) -> float:
        """
        Get the confidence multiplier for a specific regime.

        Args:
            regime: The VIX regime to get multiplier for

        Returns:
            The confidence multiplier (0.0 to 1.0)

        Raises:
            ValueError: If regime is not a valid VIXRegime
        """
        multipliers = {
            VIXRegime.LOW: self.low_multiplier,
            VIXRegime.NORMAL: self.normal_multiplier,
            VIXRegime.HIGH: self.high_multiplier,
            VIXRegime.PANIC: self.panic_multiplier,
        }
        return multipliers[regime]

    def get_regime(self, vix_value: float) -> VIXRegime:
        """
        Determine the VIX regime for a given VIX value.

        Args:
            vix_value: The VIX index value

        Returns:
            The corresponding VIX regime

        Raises:
            ValueError: If vix_value is negative
        """
        if vix_value < 0:
            raise ValueError(f"VIX value cannot be negative: {vix_value}")

        if vix_value < self.low_threshold:
            return VIXRegime.LOW
        elif vix_value < self.normal_threshold:
            return VIXRegime.NORMAL
        elif vix_value < self.high_threshold:
            return VIXRegime.HIGH
        else:
            return VIXRegime.PANIC


# Default configuration instance
_DEFAULT_CONFIG = VIXRegimeConfig()


def get_regime(vix_value: float, config: VIXRegimeConfig | None = None) -> VIXRegime:
    """
    Get the VIX regime for a given VIX value.

    Determines the market volatility regime based on the VIX (Volatility Index)
    value. The regime classification helps adjust sentiment confidence scores
    appropriately for market conditions.

    Args:
        vix_value: The VIX index value (must be non-negative)
        config: Optional custom configuration. Uses default if not provided.

    Returns:
        The VIX regime (LOW, NORMAL, HIGH, or PANIC)

    Raises:
        ValueError: If vix_value is negative
        TypeError: If vix_value is not a number

    Example:
        >>> get_regime(10.5)
        <VIXRegime.LOW: 'LOW'>
        >>> get_regime(13.0)
        <VIXRegime.NORMAL: 'NORMAL'>
        >>> get_regime(20.0)
        <VIXRegime.HIGH: 'HIGH'>
        >>> get_regime(30.0)
        <VIXRegime.PANIC: 'PANIC'>
    """
    if not isinstance(vix_value, (int, float)):
        raise TypeError(f"vix_value must be a number, got {type(vix_value).__name__}")

    cfg = config if config is not None else _DEFAULT_CONFIG
    return cfg.get_regime(float(vix_value))


def get_multiplier(
    regime: VIXRegime | str, config: VIXRegimeConfig | None = None
) -> float:
    """
    Get the confidence multiplier for a VIX regime.

    Returns the multiplier used to adjust sentiment confidence scores
    based on the market volatility regime. Higher volatility results
    in lower multipliers (more conservative confidence).

    Args:
        regime: The VIX regime (VIXRegime enum or string)
        config: Optional custom configuration. Uses default if not provided.

    Returns:
        The confidence multiplier (0.0 to 1.0)

    Raises:
        ValueError: If regime is not a valid VIXRegime
        TypeError: If regime is not a VIXRegime or string

    Example:
        >>> get_multiplier(VIXRegime.LOW)
        1.0
        >>> get_multiplier(VIXRegime.HIGH)
        0.8
        >>> get_multiplier(VIXRegime.PANIC)
        0.5
        >>> get_multiplier("HIGH")  # String input also works
        0.8
    """
    cfg = config if config is not None else _DEFAULT_CONFIG

    if isinstance(regime, str):
        try:
            regime = VIXRegime(regime.upper())
        except ValueError as e:
            raise ValueError(
                f"Invalid regime string: {regime}. "
                f"Must be one of: {[r.value for r in VIXRegime]}"
            ) from e
    elif not isinstance(regime, VIXRegime):
        raise TypeError(
            f"regime must be VIXRegime or str, got {type(regime).__name__}"
        )

    return cfg.get_multiplier_for_regime(regime)


def adjust_confidence(
    confidence: float, vix_value: float, config: VIXRegimeConfig | None = None
) -> float:
    """
    Adjust a sentiment confidence score based on VIX volatility.

    Applies a volatility-based discount to sentiment confidence scores.
    During high volatility periods, confidence scores are reduced to
    reflect increased market uncertainty.

    Args:
        confidence: The original sentiment confidence score (0.0 to 1.0)
        vix_value: The current VIX index value
        config: Optional custom configuration. Uses default if not provided.

    Returns:
        The adjusted confidence score (0.0 to 1.0)

    Raises:
        ValueError: If confidence is outside [0.0, 1.0] or vix_value is negative
        TypeError: If inputs are not numbers

    Example:
        >>> # Normal market conditions - no adjustment
        >>> adjust_confidence(0.90, vix_value=13.0)
        0.9
        >>>
        >>> # High volatility - 20% discount
        >>> adjust_confidence(0.90, vix_value=20.0)
        0.72
        >>>
        >>> # Panic conditions - 50% discount
        >>> adjust_confidence(0.90, vix_value=35.0)
        0.45
    """
    if not isinstance(confidence, (int, float)):
        raise TypeError(
            f"confidence must be a number, got {type(confidence).__name__}"
        )
    if not isinstance(vix_value, (int, float)):
        raise TypeError(f"vix_value must be a number, got {type(vix_value).__name__}")

    confidence = float(confidence)
    vix_value = float(vix_value)

    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"confidence must be between 0.0 and 1.0, got {confidence}")
    if vix_value < 0:
        raise ValueError(f"vix_value cannot be negative, got {vix_value}")

    cfg = config if config is not None else _DEFAULT_CONFIG
    regime = cfg.get_regime(vix_value)
    multiplier = cfg.get_multiplier_for_regime(regime)

    adjusted = confidence * multiplier
    # Ensure result stays in valid range [0.0, 1.0]
    return max(0.0, min(1.0, adjusted))


def weight_confidence(
    df: pd.DataFrame,
    vix_value: float,
    confidence_col: str = "sentiment_confidence",
    output_col: str | None = None,
    config: VIXRegimeConfig | None = None,
) -> pd.DataFrame:
    """
    Adjust sentiment confidence scores in a DataFrame based on VIX volatility.

    Creates a new column with volatility-adjusted confidence scores.
    This is useful for batch processing of sentiment analysis results
    where you want to account for market conditions.

    Args:
        df: DataFrame containing sentiment confidence scores
        vix_value: The current VIX index value
        confidence_col: Name of the column containing original confidence scores
        output_col: Name for the adjusted column. If None, uses
                    '{confidence_col}_adjusted'
        config: Optional custom configuration. Uses default if not provided.

    Returns:
        DataFrame with an additional column containing adjusted confidence scores

    Raises:
        ValueError: If confidence_col is not in DataFrame or contains invalid values
        TypeError: If inputs are of incorrect types

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'headline': ['News A', 'News B', 'News C'],
        ...     'sentiment_confidence': [0.95, 0.80, 0.60]
        ... })
        >>> result = weight_confidence(df, vix_value=20.0)
        >>> print(result.columns.tolist())
        ['headline', 'sentiment_confidence', 'sentiment_confidence_adjusted']
        >>> print(result['sentiment_confidence_adjusted'].tolist())
        [0.76, 0.64, 0.48]
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df).__name__}")
    if not isinstance(vix_value, (int, float)):
        raise TypeError(f"vix_value must be a number, got {type(vix_value).__name__}")
    if not isinstance(confidence_col, str):
        raise TypeError(
            f"confidence_col must be a string, got {type(confidence_col).__name__}"
        )

    if confidence_col not in df.columns:
        raise ValueError(
            f"Column '{confidence_col}' not found in DataFrame. "
            f"Available columns: {list(df.columns)}"
        )

    if vix_value < 0:
        raise ValueError(f"vix_value cannot be negative, got {vix_value}")

    # Determine output column name
    if output_col is None:
        output_col = f"{confidence_col}_adjusted"

    if output_col in df.columns:
        raise ValueError(
            f"Output column '{output_col}' already exists in DataFrame. "
            "Please specify a different output_col name."
        )

    cfg = config if config is not None else _DEFAULT_CONFIG

    # Get regime and multiplier once for efficiency
    regime = cfg.get_regime(vix_value)
    multiplier = cfg.get_multiplier_for_regime(regime)

    # Validate confidence values
    confidence_series = df[confidence_col]
    if not ((confidence_series >= 0.0) & (confidence_series <= 1.0)).all():
        invalid_mask = ~((confidence_series >= 0.0) & (confidence_series <= 1.0))
        invalid_indices = df.index[invalid_mask].tolist()
        raise ValueError(
            f"Confidence values must be between 0.0 and 1.0. "
            f"Invalid values found at indices: {invalid_indices[:10]}"
            f"{'...' if len(invalid_indices) > 10 else ''}"
        )

    # Create a copy to avoid modifying the original DataFrame
    result_df = df.copy()
    result_df[output_col] = (confidence_series * multiplier).clip(0.0, 1.0)

    return result_df


def get_regime_summary(vix_value: float) -> str:
    """
    Get a human-readable summary of the current VIX regime.

    Provides a descriptive summary including the regime name, multiplier,
    and interpretation of market conditions.

    Args:
        vix_value: The current VIX index value

    Returns:
        A formatted string describing the regime

    Example:
        >>> print(get_regime_summary(18.5))
        VIX Regime: HIGH (16.0 <= VIX < 25.0)
        Confidence Multiplier: 0.8 (20% discount)
        Interpretation: Elevated volatility - reduce confidence by 20%
    """
    regime = get_regime(vix_value)
    multiplier = get_multiplier(regime)
    discount_pct = (1.0 - multiplier) * 100

    regime_descriptions = {
        VIXRegime.LOW: "Market complacency - low volatility environment",
        VIXRegime.NORMAL: "Typical market conditions - normal volatility",
        VIXRegime.HIGH: "Elevated volatility - increased market uncertainty",
        VIXRegime.PANIC: "Market stress - high volatility environment",
    }

    regime_ranges = {
        VIXRegime.LOW: "VIX < 12.0",
        VIXRegime.NORMAL: "12.0 <= VIX < 15.0",
        VIXRegime.HIGH: "16.0 <= VIX < 25.0",
        VIXRegime.PANIC: "VIX >= 25.0",
    }

    return (
        f"VIX Regime: {regime.value} ({regime_ranges[regime]})\n"
        f"Confidence Multiplier: {multiplier} ({discount_pct:.0f}% discount)\n"
        f"Interpretation: {regime_descriptions[regime]}"
    )
