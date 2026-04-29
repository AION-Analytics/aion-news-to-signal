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
Unit tests for aion_volweight package.

Tests cover:
- VIX regime detection
- Confidence multiplier retrieval
- Single value confidence adjustment
- DataFrame confidence weighting
- Edge cases and error handling
"""

import pytest
import pandas as pd
import numpy as np

from aion_volweight import (
    VIXRegime,
    get_regime,
    get_multiplier,
    adjust_confidence,
    weight_confidence,
    VIXRegimeConfig,
    get_regime_summary,
)


class TestVIXRegime:
    """Tests for VIXRegime enum."""

    def test_regime_values(self):
        """Test that regime enum values are correct."""
        assert VIXRegime.LOW.value == "LOW"
        assert VIXRegime.NORMAL.value == "NORMAL"
        assert VIXRegime.HIGH.value == "HIGH"
        assert VIXRegime.PANIC.value == "PANIC"

    def test_regime_string_comparison(self):
        """Test that regimes can be compared with strings."""
        assert VIXRegime.LOW == "LOW"
        assert VIXRegime.HIGH == VIXRegime.HIGH.value


class TestGetRegime:
    """Tests for get_regime function."""

    def test_low_regime(self):
        """Test LOW regime detection (VIX < 12)."""
        assert get_regime(0.0) == VIXRegime.LOW
        assert get_regime(5.0) == VIXRegime.LOW
        assert get_regime(11.9) == VIXRegime.LOW
        assert get_regime(11.99) == VIXRegime.LOW

    def test_normal_regime(self):
        """Test NORMAL regime detection (12 <= VIX < 15)."""
        assert get_regime(12.0) == VIXRegime.NORMAL
        assert get_regime(13.0) == VIXRegime.NORMAL
        assert get_regime(14.9) == VIXRegime.NORMAL
        assert get_regime(14.99) == VIXRegime.NORMAL

    def test_high_regime(self):
        """Test HIGH regime detection (15 <= VIX < 25)."""
        assert get_regime(16.0) == VIXRegime.HIGH
        assert get_regime(18.5) == VIXRegime.HIGH
        assert get_regime(20.0) == VIXRegime.HIGH
        assert get_regime(24.9) == VIXRegime.HIGH
        assert get_regime(24.99) == VIXRegime.HIGH

    def test_panic_regime(self):
        """Test PANIC regime detection (VIX >= 25)."""
        assert get_regime(25.0) == VIXRegime.PANIC
        assert get_regime(30.0) == VIXRegime.PANIC
        assert get_regime(50.0) == VIXRegime.PANIC
        assert get_regime(80.0) == VIXRegime.PANIC

    def test_boundary_values(self):
        """Test exact boundary values."""
        assert get_regime(12.0) == VIXRegime.NORMAL  # LOW/NORMAL boundary
        assert get_regime(16.0) == VIXRegime.HIGH  # NORMAL/HIGH boundary
        assert get_regime(25.0) == VIXRegime.PANIC  # HIGH/PANIC boundary

    def test_negative_vix_raises_error(self):
        """Test that negative VIX values raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            get_regime(-1.0)
        with pytest.raises(ValueError, match="cannot be negative"):
            get_regime(-100.0)

    def test_invalid_type_raises_error(self):
        """Test that non-numeric types raise TypeError."""
        with pytest.raises(TypeError):
            get_regime("15.0")  # type: ignore
        with pytest.raises(TypeError):
            get_regime(None)  # type: ignore

    def test_custom_config(self):
        """Test regime detection with custom configuration."""
        custom_config = VIXRegimeConfig(
            low_threshold=10.0,
            normal_threshold=20.0,
            high_threshold=30.0,
        )
        assert get_regime(11.0, config=custom_config) == VIXRegime.NORMAL
        assert get_regime(25.0, config=custom_config) == VIXRegime.HIGH


class TestGetMultiplier:
    """Tests for get_multiplier function."""

    def test_low_multiplier(self):
        """Test multiplier for LOW regime."""
        assert get_multiplier(VIXRegime.LOW) == 1.0
        assert get_multiplier("LOW") == 1.0

    def test_normal_multiplier(self):
        """Test multiplier for NORMAL regime."""
        assert get_multiplier(VIXRegime.NORMAL) == 1.0
        assert get_multiplier("NORMAL") == 1.0

    def test_high_multiplier(self):
        """Test multiplier for HIGH regime."""
        assert get_multiplier(VIXRegime.HIGH) == 0.8
        assert get_multiplier("HIGH") == 0.8

    def test_panic_multiplier(self):
        """Test multiplier for PANIC regime."""
        assert get_multiplier(VIXRegime.PANIC) == 0.5
        assert get_multiplier("PANIC") == 0.5

    def test_case_insensitive_string(self):
        """Test that string input is case-insensitive."""
        assert get_multiplier("low") == 1.0
        assert get_multiplier("Low") == 1.0
        assert get_multiplier("HIGH") == 0.8
        assert get_multiplier("high") == 0.8

    def test_invalid_regime_string(self):
        """Test that invalid regime strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid regime string"):
            get_multiplier("INVALID")
        with pytest.raises(ValueError, match="Invalid regime string"):
            get_multiplier("medium")

    def test_invalid_type_raises_error(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError):
            get_multiplier(123)  # type: ignore
        with pytest.raises(TypeError):
            get_multiplier(None)  # type: ignore

    def test_custom_config_multiplier(self):
        """Test multiplier with custom configuration."""
        custom_config = VIXRegimeConfig(high_multiplier=0.6, panic_multiplier=0.3)
        assert get_multiplier(VIXRegime.HIGH, config=custom_config) == 0.6
        assert get_multiplier(VIXRegime.PANIC, config=custom_config) == 0.3


class TestAdjustConfidence:
    """Tests for adjust_confidence function."""

    def test_no_adjustment_low_regime(self):
        """Test no adjustment in LOW regime."""
        assert adjust_confidence(0.95, vix_value=10.0) == 0.95
        assert adjust_confidence(0.50, vix_value=5.0) == 0.50

    def test_no_adjustment_normal_regime(self):
        """Test no adjustment in NORMAL regime."""
        assert adjust_confidence(0.95, vix_value=13.0) == 0.95
        assert adjust_confidence(0.50, vix_value=14.0) == 0.50

    def test_twenty_percent_discount_high_regime(self):
        """Test 20% discount in HIGH regime."""
        assert adjust_confidence(1.0, vix_value=20.0) == 0.8
        assert adjust_confidence(0.95, vix_value=18.5) == pytest.approx(0.76, rel=1e-2)
        assert adjust_confidence(0.50, vix_value=15.0) == 0.4

    def test_fifty_percent_discount_panic_regime(self):
        """Test 50% discount in PANIC regime."""
        assert adjust_confidence(1.0, vix_value=30.0) == 0.5
        assert adjust_confidence(0.95, vix_value=25.0) == pytest.approx(0.475, rel=1e-2)
        assert adjust_confidence(0.80, vix_value=50.0) == 0.4

    def test_zero_confidence(self):
        """Test with zero confidence."""
        assert adjust_confidence(0.0, vix_value=20.0) == 0.0
        assert adjust_confidence(0.0, vix_value=50.0) == 0.0

    def test_full_confidence(self):
        """Test with full confidence."""
        assert adjust_confidence(1.0, vix_value=10.0) == 1.0
        assert adjust_confidence(1.0, vix_value=20.0) == 0.8
        assert adjust_confidence(1.0, vix_value=30.0) == 0.5

    def test_confidence_out_of_range_low(self):
        """Test that confidence < 0 raises ValueError."""
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            adjust_confidence(-0.1, vix_value=15.0)

    def test_confidence_out_of_range_high(self):
        """Test that confidence > 1 raises ValueError."""
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            adjust_confidence(1.1, vix_value=15.0)

    def test_negative_vix_raises_error(self):
        """Test that negative VIX raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            adjust_confidence(0.9, vix_value=-1.0)

    def test_invalid_types(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError):
            adjust_confidence("0.9", vix_value=15.0)  # type: ignore
        with pytest.raises(TypeError):
            adjust_confidence(0.9, vix_value="15.0")  # type: ignore


class TestWeightConfidence:
    """Tests for weight_confidence function."""

    def test_basic_weighting_high_regime(self):
        """Test basic DataFrame weighting in HIGH regime."""
        df = pd.DataFrame({
            "headline": ["News A", "News B", "News C"],
            "sentiment_confidence": [0.95, 0.80, 0.60],
        })
        result = weight_confidence(df, vix_value=20.0)

        assert "sentiment_confidence_adjusted" in result.columns
        assert len(result) == 3
        assert result["sentiment_confidence_adjusted"].iloc[0] == pytest.approx(0.76, rel=1e-2)
        assert result["sentiment_confidence_adjusted"].iloc[1] == pytest.approx(0.64, rel=1e-2)
        assert result["sentiment_confidence_adjusted"].iloc[2] == pytest.approx(0.48, rel=1e-2)

    def test_basic_weighting_panic_regime(self):
        """Test basic DataFrame weighting in PANIC regime."""
        df = pd.DataFrame({
            "headline": ["News A", "News B"],
            "sentiment_confidence": [1.0, 0.5],
        })
        result = weight_confidence(df, vix_value=30.0)

        assert result["sentiment_confidence_adjusted"].iloc[0] == 0.5
        assert result["sentiment_confidence_adjusted"].iloc[1] == 0.25

    def test_custom_confidence_column(self):
        """Test with custom confidence column name."""
        df = pd.DataFrame({
            "text": ["News A"],
            "my_confidence": [0.90],
        })
        result = weight_confidence(df, vix_value=20.0, confidence_col="my_confidence")

        assert "my_confidence_adjusted" in result.columns
        assert result["my_confidence_adjusted"].iloc[0] == pytest.approx(0.72, rel=1e-2)

    def test_custom_output_column(self):
        """Test with custom output column name."""
        df = pd.DataFrame({
            "headline": ["News A"],
            "sentiment_confidence": [0.90],
        })
        result = weight_confidence(
            df, vix_value=20.0, output_col="vol_adjusted_conf"
        )

        assert "vol_adjusted_conf" in result.columns
        assert result["vol_adjusted_conf"].iloc[0] == pytest.approx(0.72, rel=1e-2)

    def test_original_dataframe_unchanged(self):
        """Test that original DataFrame is not modified."""
        df = pd.DataFrame({
            "headline": ["News A"],
            "sentiment_confidence": [0.90],
        })
        original_values = df["sentiment_confidence"].copy()

        result = weight_confidence(df, vix_value=20.0)

        pd.testing.assert_series_equal(df["sentiment_confidence"], original_values)
        assert "sentiment_confidence_adjusted" not in df.columns

    def test_missing_column_raises_error(self):
        """Test that missing confidence column raises ValueError."""
        df = pd.DataFrame({"headline": ["News A"]})

        with pytest.raises(ValueError, match="not found in DataFrame"):
            weight_confidence(df, vix_value=15.0, confidence_col="missing_col")

    def test_invalid_confidence_values(self):
        """Test that invalid confidence values raise ValueError."""
        df = pd.DataFrame({
            "headline": ["News A", "News B"],
            "sentiment_confidence": [0.90, 1.5],  # 1.5 is invalid
        })

        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            weight_confidence(df, vix_value=15.0)

    def test_negative_vix_raises_error(self):
        """Test that negative VIX raises ValueError."""
        df = pd.DataFrame({
            "headline": ["News A"],
            "sentiment_confidence": [0.90],
        })

        with pytest.raises(ValueError, match="cannot be negative"):
            weight_confidence(df, vix_value=-1.0)

    def test_invalid_dataframe_type(self):
        """Test that non-DataFrame raises TypeError."""
        with pytest.raises(TypeError):
            weight_confidence("not a dataframe", vix_value=15.0)  # type: ignore

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame({"sentiment_confidence": []})
        result = weight_confidence(df, vix_value=15.0)

        assert len(result) == 0
        assert "sentiment_confidence_adjusted" in result.columns

    def test_large_dataframe(self):
        """Test with large DataFrame for performance."""
        n = 10000
        df = pd.DataFrame({
            "headline": [f"News {i}" for i in range(n)],
            "sentiment_confidence": np.random.uniform(0.5, 1.0, n),
        })

        result = weight_confidence(df, vix_value=20.0)

        assert len(result) == n
        assert (result["sentiment_confidence_adjusted"] <= result["sentiment_confidence"]).all()


class TestGetRegimeSummary:
    """Tests for get_regime_summary function."""

    def test_low_regime_summary(self):
        """Test summary for LOW regime."""
        summary = get_regime_summary(10.0)
        assert "LOW" in summary
        assert "1.0" in summary
        assert "0% discount" in summary

    def test_high_regime_summary(self):
        """Test summary for HIGH regime."""
        summary = get_regime_summary(20.0)
        assert "HIGH" in summary
        assert "0.8" in summary
        assert "20% discount" in summary

    def test_panic_regime_summary(self):
        """Test summary for PANIC regime."""
        summary = get_regime_summary(30.0)
        assert "PANIC" in summary
        assert "0.5" in summary
        assert "50% discount" in summary

    def test_summary_format(self):
        """Test that summary has expected format."""
        summary = get_regime_summary(18.0)
        lines = summary.split("\n")
        assert len(lines) == 3
        assert "VIX Regime:" in lines[0]
        assert "Confidence Multiplier:" in lines[1]
        assert "Interpretation:" in lines[2]


class TestVIXRegimeConfig:
    """Tests for VIXRegimeConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = VIXRegimeConfig()
        assert config.low_threshold == 12.0
        assert config.normal_threshold == 15.0
        assert config.high_threshold == 25.0
        assert config.low_multiplier == 1.0
        assert config.normal_multiplier == 1.0
        assert config.high_multiplier == 0.8
        assert config.panic_multiplier == 0.5

    def test_custom_values(self):
        """Test custom configuration values."""
        config = VIXRegimeConfig(
            low_threshold=10.0,
            high_multiplier=0.7,
            panic_multiplier=0.4,
        )
        assert config.low_threshold == 10.0
        assert config.high_multiplier == 0.7
        assert config.panic_multiplier == 0.4

    def test_frozen_dataclass(self):
        """Test that config is immutable."""
        config = VIXRegimeConfig()
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            config.low_threshold = 10.0  # type: ignore

    def test_get_multiplier_for_regime(self):
        """Test get_multiplier_for_regime method."""
        config = VIXRegimeConfig(high_multiplier=0.6)
        assert config.get_multiplier_for_regime(VIXRegime.HIGH) == 0.6
        assert config.get_multiplier_for_regime(VIXRegime.LOW) == 1.0

    def test_get_regime_method(self):
        """Test get_regime method."""
        config = VIXRegimeConfig(low_threshold=10.0, normal_threshold=20.0)
        assert config.get_regime(8.0) == VIXRegime.LOW
        assert config.get_regime(15.0) == VIXRegime.NORMAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
