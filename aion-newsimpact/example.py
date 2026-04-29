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
Example usage of AION NewsImpact package.

This script demonstrates various use cases for historical news impact
analysis using semantic search.

AION Open Source Ecosystem
"""

import pandas as pd

from aion_newsimpact import NewsImpact, ImpactQueryResult


def create_sample_data() -> pd.DataFrame:
    """Create sample historical news data."""
    return pd.DataFrame({
        "headline": [
            "Apple reports record quarterly earnings, beats expectations",
            "Google parent Alphabet misses revenue targets",
            "Microsoft announces major AI investment",
            "Amazon stock surges on strong cloud growth",
            "Tesla faces production challenges in Q4",
            "Meta platforms cuts workforce amid restructuring",
            "Nvidia unveils new AI chip architecture",
            "Intel struggles with manufacturing delays",
            "Semiconductor shortage impacts auto industry",
            "Tech sector rallies on positive economic data",
            "Federal Reserve signals potential rate changes",
            "Market volatility increases amid trade tensions",
            "Banking sector faces regulatory scrutiny",
            "Energy stocks surge on oil price spike",
            "Healthcare stocks gain on drug approval news",
            "Consumer spending shows unexpected strength",
            "Manufacturing data indicates economic slowdown",
            "Retail earnings exceed analyst expectations",
            "Housing market shows signs of cooling",
            "Employment report beats forecasts",
        ],
        "date": [
            "2025-01-15", "2025-01-18", "2025-01-22", "2025-01-25", "2025-01-28",
            "2025-02-01", "2025-02-05", "2025-02-08", "2025-02-12", "2025-02-15",
            "2025-02-18", "2025-02-22", "2025-02-25", "2025-03-01", "2025-03-05",
            "2025-03-08", "2025-03-12", "2025-03-15", "2025-03-18", "2025-03-22",
        ],
        "returns_1d": [
            0.032, -0.028, 0.025, 0.018, -0.015,
            -0.022, 0.035, -0.012, -0.008, 0.022,
            0.008, -0.018, -0.015, 0.042, 0.028,
            0.012, -0.020, 0.015, -0.010, 0.018,
        ],
        "ticker": [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "META", "NVDA", "INTC", "SOXX", "QQQ",
            "TLT", "SPY", "XLF", "XLE", "XLV",
            "XLY", "XLI", "XRT", "XHB", "SPY",
        ],
        "sector": [
            "Technology", "Technology", "Technology", "Consumer", "Consumer",
            "Technology", "Technology", "Technology", "Technology", "Technology",
            "Financial", "Broad Market", "Financial", "Energy", "Healthcare",
            "Consumer", "Industrial", "Consumer", "Real Estate", "Broad Market",
        ],
    })


def example_basic_query():
    """Demonstrate basic query functionality."""
    print("=" * 70)
    print("Example 1: Basic Query")
    print("=" * 70)

    df = create_sample_data()
    analyzer = NewsImpact(df, text_column="headline")

    # Query for earnings-related headlines
    query = "Company reports strong quarterly earnings"
    print(f"\nQuery: '{query}'\n")

    results = analyzer.query(query, top_k=5)

    print(f"Found {len(results)} similar historical headlines\n")
    print(f"Average Similarity: {results.average_similarity:.3f}")
    print(f"Average 1-Day Return: {results.average_return:.2%}")
    print(f"Return Std Dev: {results.return_std:.2%}\n")

    print("Top Results:")
    print("-" * 70)
    for i, (headline, date, sim, ret, ticker) in enumerate(
        zip(
            results.headlines,
            results.dates,
            results.similarity_scores,
            results.returns_1d,
            results.tickers,
        )
    ):
        print(f"{i + 1}. [{sim:.3f}] {date} | {ticker}")
        print(f"   {headline}")
        print(f"   1-Day Return: {ret:+.2%}")
        print()


def example_impact_statistics():
    """Demonstrate impact statistics."""
    print("=" * 70)
    print("Example 2: Impact Statistics")
    print("=" * 70)

    df = create_sample_data()
    analyzer = NewsImpact(df, text_column="headline")

    stats = analyzer.get_impact_stats()

    print("\nHistorical Impact Statistics")
    print("-" * 70)
    print(f"Total Headlines: {stats['total_headlines']}")
    print(f"Date Range: {stats['date_range'][0]} to {stats['date_range'][1]}")
    print()
    print("Return Statistics:")
    print(f"  Average 1-Day Return: {stats['avg_return_1d']:.2%}")
    print(f"  Std Deviation: {stats['std_return_1d']:.2%}")
    print(f"  Minimum Return: {stats['min_return']:.2%}")
    print(f"  Maximum Return: {stats['max_return']:.2%}")
    print()
    print("Impact Distribution:")
    print(f"  Positive Impact: {stats['positive_impact_pct']:.1f}%")
    print(f"  Negative Impact: {stats['negative_impact_pct']:.1f}%")
    print(f"  Neutral Impact: {stats['neutral_impact_pct']:.1f}%")
    print()


def example_adding_headlines():
    """Demonstrate adding new headlines."""
    print("=" * 70)
    print("Example 3: Adding New Headlines")
    print("=" * 70)

    df = create_sample_data()
    analyzer = NewsImpact(df, text_column="headline")

    print(f"\nInitial headline count: {len(analyzer.historical_df)}")

    # Add new headlines
    new_data = pd.DataFrame({
        "headline": [
            "Tech giant announces breakthrough in quantum computing",
            "AI startup valued at $10 billion in latest funding round",
        ],
        "date": ["2025-04-01", "2025-04-05"],
        "returns_1d": [0.045, 0.038],
        "ticker": ["GOOGL", "Private"],
        "sector": ["Technology", "Technology"],
    })

    analyzer.add_headlines(new_data, rebuild_index=True)

    print(f"After adding headlines: {len(analyzer.historical_df)}")

    # Query to verify new headlines are included
    results = analyzer.query("quantum computing breakthrough", top_k=3)

    print("\nQuery results for 'quantum computing breakthrough':")
    for i, (headline, sim) in enumerate(
        zip(results.headlines, results.similarity_scores)
    ):
        print(f"  {i + 1}. [{sim:.3f}] {headline}")
    print()


def example_dataframe_output():
    """Demonstrate DataFrame output."""
    print("=" * 70)
    print("Example 4: DataFrame Output")
    print("=" * 70)

    df = create_sample_data()
    analyzer = NewsImpact(df, text_column="headline")

    results = analyzer.query("Federal Reserve interest rate decision", top_k=5)

    # Convert to DataFrame
    result_df = results.to_dataframe()

    print("\nQuery Results as DataFrame:")
    print(result_df.to_string(index=False))
    print()


def example_multiple_queries():
    """Demonstrate multiple queries for analysis."""
    print("=" * 70)
    print("Example 5: Multiple Queries Analysis")
    print("=" * 70)

    df = create_sample_data()
    analyzer = NewsImpact(df, text_column="headline")

    queries = [
        "Earnings beat expectations",
        "Revenue misses estimates",
        "New product announcement",
        "Regulatory concerns",
        "Market volatility",
    ]

    print("\nMultiple Query Analysis")
    print("-" * 70)
    print(f"{'Query':<35} {'Avg Sim':>10} {'Avg Return':>12} {'Count':>8}")
    print("-" * 70)

    for query in queries:
        results = analyzer.query(query, top_k=5)
        print(
            f"{query[:34]:<35} "
            f"{results.average_similarity:>10.3f} "
            f"{results.average_return:>11.2%} "
            f"{len(results):>8}"
        )
    print()


def example_integration_with_volweight():
    """Demonstrate integration with aion-volweight."""
    print("=" * 70)
    print("Example 6: Integration with AION VolWeight")
    print("=" * 70)

    try:
        from aion_volweight import adjust_confidence, get_regime

        df = create_sample_data()
        analyzer = NewsImpact(df, text_column="headline")

        query = "Company reports strong earnings"
        current_vix = 18.5  # HIGH regime

        results = analyzer.query(query, top_k=5)

        # Get base confidence from similarity
        base_confidence = results.average_similarity

        # Adjust based on VIX
        adjusted_confidence = adjust_confidence(base_confidence, current_vix)

        print(f"\nQuery: '{query}'")
        print(f"Current VIX: {current_vix} ({get_regime(current_vix).value} regime)")
        print()
        print("Impact Analysis:")
        print(f"  Base Confidence (similarity): {base_confidence:.3f}")
        print(f"  Vol-Adjusted Confidence: {adjusted_confidence:.3f}")
        print(f"  Historical Avg Return: {results.average_return:.2%}")
        print(f"  Return Volatility: {results.return_std:.2%}")
        print()

    except ImportError:
        print("\naion-volweight not installed. Skipping integration example.")
        print("Install with: pip install aion-volweight\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("AION NewsImpact - Usage Examples")
    print("Historical News Impact Analysis using Semantic Search")
    print("=" * 70 + "\n")

    example_basic_query()
    example_impact_statistics()
    example_adding_headlines()
    example_dataframe_output()
    example_multiple_queries()
    example_integration_with_volweight()

    print("=" * 70)
    print("Examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
