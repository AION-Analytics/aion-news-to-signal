#!/usr/bin/env python3
# =============================================================================
# AION Open-Source Project: AION SectorMap
# File: example.py
# Description: Usage examples for AION SectorMap
# License: Apache License, Version 2.0
#
# Copyright 2026 AION Contributors
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
#
# AION Attribution: This file is part of the AION open-source ecosystem.
# Please visit https://github.com/aion for more information.
# =============================================================================
"""
AION SectorMap - Usage Examples.

This script demonstrates various use cases for the AION SectorMap package,
including basic lookups, DataFrame mapping, and sector analysis.

Run this script:
    python example.py
    python -m aion_sectormap.example

Requirements:
    - pandas>=2.0.0
    - aion-sectormap (this package)
"""

import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd

from aion_sectormap import SectorMapper


def example_basic_lookups() -> None:
    """Demonstrate basic ticker lookups."""
    print("=" * 70)
    print("Example 1: Basic Ticker Lookups")
    print("=" * 70)

    # Initialize the mapper
    mapper = SectorMapper()

    # Sample tickers to look up
    tickers = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN"]

    print("\nTicker → Sector/Industry/Group Mapping:\n")
    print(f"{'Ticker':<12} {'Company':<45} {'Sector':<35}")
    print("-" * 92)

    for ticker in tickers:
        if ticker in mapper:
            company = mapper.get_company_name(ticker)
            sector = mapper.get_sector(ticker)
            print(f"{ticker:<12} {company:<45} {sector:<35}")
        else:
            print(f"{ticker:<12} {'Not found':<45} {'-':<35}")

    # Demonstrate default values for unknown tickers
    print("\nHandling Unknown Tickers:")
    unknown_ticker = "INVALID"
    sector = mapper.get_sector(unknown_ticker)
    print(f"  {unknown_ticker} → {sector} (default)")

    sector_custom = mapper.get_sector(unknown_ticker, default="N/A")
    print(f"  {unknown_ticker} → {sector_custom} (custom default)")


def example_reverse_lookups() -> None:
    """Demonstrate reverse lookups (sector → tickers)."""
    print("\n" + "=" * 70)
    print("Example 2: Reverse Lookups (Sector → Tickers)")
    print("=" * 70)

    mapper = SectorMapper()

    # Get all sectors
    sectors = mapper.get_all_sectors()
    print(f"\nTotal Sectors: {len(sectors)}")
    print(f"Sample Sectors: {', '.join(sectors[:5])}")

    # Get tickers in Financial Services sector
    sector_name = "Financial Services"
    tickers = mapper.get_tickers_in_sector(sector_name)

    print(f"\n{sector_name} Sector:")
    print(f"  Total Companies: {len(tickers)}")
    print(f"  Sample Tickers: {', '.join(tickers[:10])}")

    # Get tickers in a business group
    groups = mapper.get_all_groups()
    if groups:
        sample_group = groups[0]
        group_tickers = mapper.get_tickers_in_group(sample_group)
        print(f"\nBusiness Group: {sample_group}")
        print(f"  Companies: {len(group_tickers)}")
        print(f"  Tickers: {', '.join(group_tickers[:5])}")


def example_dataframe_mapping() -> None:
    """Demonstrate DataFrame mapping functionality."""
    print("\n" + "=" * 70)
    print("Example 3: DataFrame Mapping")
    print("=" * 70)

    mapper = SectorMapper()

    # Create a sample portfolio DataFrame
    portfolio = pd.DataFrame(
        {
            "ticker": [
                "RELIANCE",
                "TCS",
                "HDFCBANK",
                "INFY",
                "HINDUNILVR",
                "ICICIBANK",
                "SBIN",
                "BAJFINANCE",
                "LT",
                "ITC",
            ],
            "quantity": [100, 50, 200, 100, 75, 150, 300, 80, 60, 120],
            "avg_price": [2400.0, 3400.0, 1500.0, 1350.0, 2500.0, 950.0, 550.0, 2800.0, 3200.0, 420.0],
        }
    )

    print("\nOriginal Portfolio:")
    print(portfolio.to_string(index=False))

    # Map sector and industry
    portfolio_mapped = mapper.map(portfolio)

    print("\nPortfolio with Sector & Industry:")
    print(
        portfolio_mapped[["ticker", "quantity", "avg_price", "sector", "industry"]].to_string(
            index=False
        )
    )

    # Map with additional columns
    portfolio_full = mapper.map(
        portfolio,
        add_gin=True,
        add_company_name=True,
    )

    print("\nPortfolio with Full Details:")
    print(
        portfolio_full[
            ["ticker", "company_name", "sector", "group", "gin"]
        ].to_string(index=False)
    )


def example_sector_analysis() -> None:
    """Demonstrate sector analysis capabilities."""
    print("\n" + "=" * 70)
    print("Example 4: Sector Analysis")
    print("=" * 70)

    mapper = SectorMapper()

    # Get sector summary
    sector_summary = mapper.get_sector_summary()

    print("\nSector Distribution (Top 10):")
    print(sector_summary.head(10).to_string(index=False))

    # Get group summary
    group_summary = mapper.get_group_summary()

    print("\nBusiness Group Distribution (Top 10):")
    print(group_summary.head(10).to_string(index=False))

    # Get mapping statistics
    stats = mapper.get_mapping_stats()

    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")


def example_search() -> None:
    """Demonstrate search functionality."""
    print("\n" + "=" * 70)
    print("Example 5: Search Companies")
    print("=" * 70)

    mapper = SectorMapper()

    # Search for HDFC companies
    print("\nSearching for 'HDFC':")
    hdfc_results = mapper.search_ticker("HDFC")

    if len(hdfc_results) > 0:
        print(
            hdfc_results[["ticker", "company_name", "sector"]].to_string(
                index=False, max_rows=10
            )
        )
    else:
        print("  No results found")

    # Search for Tata companies
    print("\nSearching for 'Tata':")
    tata_results = mapper.search_ticker("Tata")

    if len(tata_results) > 0:
        print(
            tata_results[["ticker", "company_name", "sector"]].to_string(
                index=False, max_rows=10
            )
        )
    else:
        print("  No results found")


def example_sector_allocation() -> None:
    """Demonstrate sector allocation calculation for a portfolio."""
    print("\n" + "=" * 70)
    print("Example 6: Portfolio Sector Allocation")
    print("=" * 70)

    mapper = SectorMapper()

    # Create a sample portfolio
    portfolio = pd.DataFrame(
        {
            "ticker": [
                "RELIANCE",
                "TCS",
                "HDFCBANK",
                "INFY",
                "HINDUNILVR",
                "ICICIBANK",
                "SBIN",
                "TATASTEEL",
                "SUNPHARMA",
                "MARUTI",
            ],
            "value": [500000, 300000, 400000, 250000, 200000, 350000, 280000, 180000, 220000, 150000],
        }
    )

    # Add sector mapping
    portfolio = mapper.map(portfolio)

    # Calculate sector allocation
    sector_allocation = (
        portfolio.groupby("sector")["value"]
        .sum()
        .reset_index()
        .sort_values("value", ascending=False)
    )
    sector_allocation["percentage"] = (
        sector_allocation["value"] / sector_allocation["value"].sum() * 100
    )

    print("\nPortfolio Sector Allocation:")
    print(
        sector_allocation.to_string(
            index=False,
            formatters={"value": lambda x: f"₹{x:,.0f}", "percentage": lambda x: f"{x:.1f}%"},
        )
    )

    # Calculate group allocation
    group_allocation = (
        portfolio.groupby("group")["value"]
        .sum()
        .reset_index()
        .sort_values("value", ascending=False)
    )
    group_allocation["percentage"] = (
        group_allocation["value"] / group_allocation["value"].sum() * 100
    )

    print("\nPortfolio Group Allocation (Top 10):")
    print(
        group_allocation.head(10).to_string(
            index=False,
            formatters={"value": lambda x: f"₹{x:,.0f}", "percentage": lambda x: f"{x:.1f}%"},
        )
    )


def example_special_methods() -> None:
    """Demonstrate special methods (__len__, __contains__, __repr__)."""
    print("\n" + "=" * 70)
    print("Example 7: Special Methods")
    print("=" * 70)

    mapper = SectorMapper()

    # Length
    print(f"\nTotal Tickers in Database: {len(mapper)}")

    # Contains
    test_tickers = ["RELIANCE", "TCS", "INVALID"]
    print("\nTicker Existence Check:")
    for ticker in test_tickers:
        exists = ticker in mapper
        print(f"  {ticker}: {'✓' if exists else '✗'}")

    # Representation
    print(f"\nMapper Representation: {repr(mapper)}")


def main() -> None:
    """Run all examples."""
    print("\n" + "=" * 70)
    print("AION SectorMap - Usage Examples")
    print("=" * 70)
    print(f"\nAION SectorMap provides comprehensive NSE ticker → sector/industry mapping")
    print(f"with {len(SectorMapper())}+ companies across 44 sectors.\n")

    try:
        # Run all examples
        example_basic_lookups()
        example_reverse_lookups()
        example_dataframe_mapping()
        example_sector_analysis()
        example_search()
        example_sector_allocation()
        example_special_methods()

        print("\n" + "=" * 70)
        print("Examples completed successfully!")
        print("=" * 70)
        print("\nFor more information, visit: https://github.com/aion/aion-sectormap")
        print("Documentation: https://github.com/aion/aion-sectormap#readme\n")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nMake sure sector_map.json exists in the data/ directory.")
        print("Run: python scripts/update_map.py --source local\n")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
