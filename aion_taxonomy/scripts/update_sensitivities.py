#!/usr/bin/env python3
# aion_taxonomy/scripts/update_sensitivities.py
# Compute 90-day rolling correlations between sector indices and 5 meta-factors.
# Outputs: aion_taxonomy/src/aion_taxonomy/data/sector_sensitivities.json

import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
UNIFIED_CSV = DATA_DIR / "unified_meta_data.csv"
GSEC_CSV = Path(__file__).parent.parent.parent / "dataset" / "India 10-Year Bond Yield Historical Data.csv"
OUTPUT_JSON = SCRIPT_DIR.parent / "src" / "aion_taxonomy" / "data" / "sector_sensitivities.json"

ROLLING_WINDOW = 90  # trading days

def load_unified_data() -> pd.DataFrame:
    """Load Yahoo Finance sector indices + VIX + USD/INR + Crude."""
    df = pd.read_csv(UNIFIED_CSV, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df

def load_gsec_data() -> pd.Series:
    """Load G-Sec 10Y yield daily changes."""
    df = pd.read_csv(GSEC_CSV, parse_dates=["date"])
    df = df.set_index("date").sort_index()
    # Convert price to daily change (absolute change in yield)
    df["yield_change"] = df["price"].astype(float).diff()
    return df["yield_change"]

def build_factor_returns(yf_df: pd.DataFrame, gsec_changes: pd.Series) -> pd.DataFrame:
    """Build 5 meta-factor daily returns/changes time series."""
    factors = pd.DataFrame(index=yf_df.index)
    
    # 1. interest_rate: G-Sec yield daily change
    factors["interest_rate"] = gsec_changes.reindex(yf_df.index)
    
    # 2. crude_oil: Crude oil daily change (already in unified CSV)
    if "crude_return" in yf_df.columns:
        factors["crude_oil"] = yf_df["crude_return"]
    else:
        factors["crude_oil"] = 0.0
    
    # 3. rupee: USD/INR daily change
    if "usdinr_change" in yf_df.columns:
        factors["rupee"] = yf_df["usdinr_change"]
    else:
        factors["rupee"] = 0.0
    
    # 4. risk_sentiment: India VIX daily change (inverted — VIX up = risk off = negative sentiment)
    if "vix_change" in yf_df.columns:
        factors["risk_sentiment"] = -yf_df["vix_change"]  # Inverted
    else:
        factors["risk_sentiment"] = 0.0
    
    # 5. liquidity: Use NIFTY50 daily changes as proxy
    if "NIFTY50" in yf_df.columns:
        factors["liquidity"] = yf_df["NIFTY50"].pct_change(fill_method=None)
    else:
        factors["liquidity"] = 0.0
    
    # Drop rows with too many NaNs
    factors = factors.dropna(how="all")
    
    # Forward fill small gaps (1-2 days)
    factors = factors.ffill(limit=2)
    
    return factors

def compute_rolling_correlations(
    sector_returns: pd.DataFrame,
    factor_returns: pd.DataFrame,
    window: int = ROLLING_WINDOW,
) -> dict:
    """Compute rolling correlations for each sector against each factor."""
    factors = ["interest_rate", "crude_oil", "rupee", "risk_sentiment", "liquidity"]
    results = {}
    
    for sector in sector_returns.columns:
        sector_data = sector_returns[sector].dropna()
        
        # Compute rolling correlation with each factor
        corr_dict = {}
        for factor in factors:
            # Align indices
            aligned = pd.concat([sector_data, factor_returns[factor]], axis=1).dropna()
            if len(aligned) < window:
                # Use static default if not enough data
                corr_dict[factor] = 0.0
            else:
                # Rolling correlation
                rolling_corr = aligned.iloc[:, 0].rolling(window=window).corr(aligned.iloc[:, 1])
                # Take the latest value
                latest = rolling_corr.dropna().iloc[-1] if rolling_corr.dropna().shape[0] > 0 else 0.0
                corr_dict[factor] = round(float(latest), 4)
        
        results[sector] = {
            **corr_dict,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        }
    
    return results

def main():
    print("=" * 60)
    print("AION Sector Sensitivity Calculator — 90-Day Rolling Correlations")
    print("=" * 60)
    
    # Load data
    print("\n📊 Loading unified Yahoo Finance data...")
    yf_df = load_unified_data()
    print(f"  Loaded {len(yf_df)} rows, {len(yf_df.columns)} columns")
    print(f"  Date range: {yf_df.index.min()} to {yf_df.index.max()}")
    
    print("\n🏦 Loading G-Sec 10Y yield data...")
    gsec_changes = load_gsec_data()
    print(f"  Loaded {len(gsec_changes)} rows")
    print(f"  Date range: {gsec_changes.index.min()} to {gsec_changes.index.max()}")
    
    # Build factor returns
    print("\n🔗 Building 5-factor returns...")
    factors = build_factor_returns(yf_df, gsec_changes)
    print(f"  Factors: {list(factors.columns)}")
    print(f"  Non-NA rows: {len(factors.dropna())}")
    
    # Sector columns (these are already daily changes from compute_factor_changes)
    factor_cols = {"vix_change", "usdinr_change", "crude_return"}
    sector_cols = [c for c in yf_df.columns if c not in factor_cols]
    
    # The sector data is already daily changes (absolute), not prices
    # Use them directly for correlation (scale-invariant)
    sector_changes = yf_df[sector_cols].copy()
    
    # Drop rows with all NaN
    sector_changes = sector_changes.dropna(how="all")
    print(f"\n📈 Sector changes: {len(sector_changes.columns)} sectors, {len(sector_changes)} rows")
    
    # Compute rolling correlations
    print(f"\n📐 Computing {ROLLING_WINDOW}-day rolling correlations...")
    sensitivities = compute_rolling_correlations(sector_changes, factors, ROLLING_WINDOW)
    
    print(f"\n✅ Computed sensitivities for {len(sensitivities)} sectors")
    for sector, sens in list(sensitivities.items())[:3]:
        print(f"  {sector}: {sens}")
    
    # Save to JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        import json
        json.dump(sensitivities, f, indent=2)
    
    print(f"\n💾 Saved to: {OUTPUT_JSON}")
    print(f"\n✅ Sensitivity calculation complete.")


if __name__ == "__main__":
    main()
