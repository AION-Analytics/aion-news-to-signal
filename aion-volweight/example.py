#!/usr/bin/env python3
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
Example usage of AION VolWeight package.

This script demonstrates various use cases for VIX-based sentiment
confidence adjustment.

AION Open Source Ecosystem
"""

import pandas as pd

from aion_volweight import (
    VIXRegime,
    VIXRegimeConfig,
    adjust_confidence,
    get_multiplier,
    get_regime,
    get_regime_summary,
    weight_confidence,
)


def example_basic_usage():
    """Demonstrate basic VIX regime detection and confidence adjustment."""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)

    # Sample VIX values representing different market conditions
    vix_values = [10.0, 13.0, 18.5, 30.0]
    original_confidence = 0.90

    print(f"\nOriginal Confidence: {original_confidence}\n")

    for vix in vix_values:
        regime = get_regime(vix)
        multiplier = get_multiplier(regime)
        adjusted = adjust_confidence(original_confidence, vix)

        print(f"VIX: {vix:5.1f} | Regime: {regime.value:6} | "
              f"Multiplier: {multiplier:.1f} | "
              f"Adjusted: {adjusted:.2f}")

    print()


def example_regime_summary():
    """Demonstrate regime summary output."""
    print("=" * 60)
    print("Example 2: Regime Summary")
    print("=" * 60)

    for vix in [10.0, 13.0, 20.0, 35.0]:
        print(f"\nVIX = {vix}:")
        print(get_regime_summary(vix))
        print("-" * 40)

    print()


def example_dataframe_processing():
    """Demonstrate DataFrame batch processing."""
    print("=" * 60)
    print("Example 3: DataFrame Processing")
    print("=" * 60)

    # Create sample sentiment analysis results
    df = pd.DataFrame({
        'headline': [
            'Company A reports strong quarterly earnings beat',
            'Market uncertainty grows amid trade tensions',
            'Tech sector shows resilience despite challenges',
            'Central bank signals potential rate changes',
            'Energy sector rallies on supply concerns',
        ],
        'sentiment_confidence': [0.95, 0.80, 0.70, 0.85, 0.75],
        'sentiment_label': ['positive', 'negative', 'positive', 'neutral', 'positive'],
        'ticker': ['AAPL', 'SPY', 'QQQ', 'TLT', 'XLE'],
    })

    print("\nOriginal DataFrame:")
    print(df.to_string(index=False))

    # Process with different VIX levels
    vix_scenarios = [
        (13.0, "Normal Market"),
        (20.0, "High Volatility"),
        (35.0, "Panic Conditions"),
    ]

    for vix, scenario in vix_scenarios:
        print(f"\n{scenario} (VIX = {vix}):")
        adjusted_df = weight_confidence(df, vix_value=vix)
        print(adjusted_df[['headline', 'sentiment_confidence', 
                          'sentiment_confidence_adjusted']].to_string(index=False))

    print()


def example_custom_config():
    """Demonstrate custom configuration."""
    print("=" * 60)
    print("Example 4: Custom Configuration")
    print("=" * 60)

    # Create custom regime configuration
    custom_config = VIXRegimeConfig(
        low_threshold=10.0,      # More conservative LOW threshold
        normal_threshold=18.0,   # Extended NORMAL regime
        high_threshold=30.0,     # Higher threshold for HIGH regime
        high_multiplier=0.7,     # 30% discount in HIGH regime
        panic_multiplier=0.4,    # 60% discount in PANIC regime
    )

    vix = 22.0
    original_confidence = 0.85

    # Default config
    default_regime = get_regime(vix)
    default_adjusted = adjust_confidence(original_confidence, vix)

    # Custom config
    custom_regime = get_regime(vix, config=custom_config)
    custom_adjusted = adjust_confidence(original_confidence, vix, config=custom_config)

    print(f"\nVIX: {vix}")
    print(f"Original Confidence: {original_confidence}")
    print(f"\nDefault Config:")
    print(f"  Regime: {default_regime.value}")
    print(f"  Adjusted: {default_adjusted:.2f}")
    print(f"\nCustom Config:")
    print(f"  Regime: {custom_regime.value}")
    print(f"  Adjusted: {custom_adjusted:.2f}")
    print()


def example_integration_pipeline():
    """Demonstrate integration with a sentiment analysis pipeline."""
    print("=" * 60)
    print("Example 5: Integration Pipeline")
    print("=" * 60)

    def simulate_sentiment_analysis(headlines: list[str]) -> pd.DataFrame:
        """Simulate sentiment analysis results."""
        # In real usage, this would call an actual sentiment analysis model
        import random
        random.seed(42)  # For reproducibility

        return pd.DataFrame({
            'headline': headlines,
            'sentiment_confidence': [random.uniform(0.7, 0.98) for _ in headlines],
            'sentiment_score': [random.uniform(-1, 1) for _ in headlines],
        })

    def process_with_volatility_adjustment(
        sentiment_df: pd.DataFrame,
        current_vix: float
    ) -> pd.DataFrame:
        """Process sentiment results with volatility adjustment."""
        # Adjust confidence based on VIX
        adjusted_df = weight_confidence(
            sentiment_df,
            vix_value=current_vix,
            confidence_col='sentiment_confidence',
            output_col='vol_adjusted_confidence'
        )

        # Add regime information
        regime = get_regime(current_vix)
        adjusted_df['vix_regime'] = regime.value
        adjusted_df['vix_multiplier'] = get_multiplier(regime)

        # Calculate weighted sentiment score
        adjusted_df['weighted_sentiment'] = (
            adjusted_df['sentiment_score'] * adjusted_df['vol_adjusted_confidence']
        )

        return adjusted_df

    # Sample headlines
    headlines = [
        "Tech giant announces breakthrough in AI technology",
        "Federal Reserve hints at policy shift in upcoming meeting",
        "Oil prices surge on Middle East tensions",
        "Retail sales data exceeds expectations",
        "Banking sector faces regulatory scrutiny",
    ]

    # Simulate sentiment analysis
    sentiment_results = simulate_sentiment_analysis(headlines)

    # Current market conditions
    current_vix = 18.5

    # Process with volatility adjustment
    final_results = process_with_volatility_adjustment(sentiment_results, current_vix)

    print(f"\nCurrent VIX: {current_vix} ({get_regime(current_vix).value} regime)")
    print(f"Multiplier: {get_multiplier(get_regime(current_vix))}")
    print("\nFinal Results:")
    print(final_results.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

    # Summary statistics
    print("\nSummary Statistics:")
    print(f"  Average Original Confidence: {sentiment_results['sentiment_confidence'].mean():.3f}")
    print(f"  Average Adjusted Confidence: {final_results['vol_adjusted_confidence'].mean():.3f}")
    print(f"  Average Weighted Sentiment: {final_results['weighted_sentiment'].mean():.3f}")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("AION VolWeight - Usage Examples")
    print("VIX-based Sentiment Confidence Adjustment")
    print("=" * 60 + "\n")

    example_basic_usage()
    example_regime_summary()
    example_dataframe_processing()
    example_custom_config()
    example_integration_pipeline()

    print("=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
