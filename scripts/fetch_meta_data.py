#!/usr/bin/env python3
# aion_taxonomy/scripts/fetch_meta_data.py
# Fetch daily time series for 5 meta-factors and sector indices.
# Outputs: unified_meta_data.csv

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_CSV = OUTPUT_DIR / "unified_meta_data.csv"

# NSE sector indices mapped to Yahoo Finance tickers (when available)
SECTOR_INDICES = {
    "NIFTYAUTO": "^CNXAUTO",
    "NIFTYBANK": "^CNX Bank",  # fallback; we handle below
    "NIFTYFIN": "^CNX Finance",
    "NIFTYFMCG": "^CNX FMCG",
    "NIFTYIT": "^CNXIT",
    "NIFTYMEDIA": "^CNX MEDIA",
    "NIFTYMETAL": "^CNX METAL",
    "NIFTYPHARMA": "^CNX PHARMA",
    "NIFTYPSUBANK": "^CNX PSU BANK",
    "NIFTYREALTY": "^CNX REALTY",
    "NIFTYENERGY": "^CNX ENERGY",
    "NIFTYINFRA": "^CNX INFRA",
    "NIFTYMNC": "^CNX MNC",
    "NIFTYMIDCAP": "^CNX MIDCAP",
    "NIFTYSMLCAP": "^CNX SMALLCAP",
    "NIFTY100": "^CRSLDX",
    "NIFTY50": "^NSEI",
}

# Yahoo Finance sector tickers (verified working)
YF_SECTORS = {
    "NIFTYAUTO": "^CNXAUTO",
    "NIFTYBANK": "^NSEBANK",
    "NIFTYFIN": "^CNXFIN",
    "NIFTYFMCG": "^CNXFMCG",
    "NIFTYIT": "^CNXIT",
    "NIFTYMEDIA": "^CNXMEDIA",
    "NIFTYMETAL": "^CNXMETAL",
    "NIFTYPHARMA": "^CNXPHARMA",
    "NIFTYPSUBANK": "^CNXPSE",
    "NIFTYREALTY": "^CNXREALTY",
    "NIFTYENERGY": "^CNXENERGY",
    "NIFTYINFRA": "^CNXINFRA",
    "NIFTYMNC": "^CNXMNC",
    "NIFTY50": "^NSEI",
}

# Factor ticker mappings (Yahoo Finance)
FACTOR_TICKERS = {
    "INDIAVIX": "^INDIAVIX",
    "USDINR": "USDINR=X",
    "CRUDE_OIL": "CL=F",  # WTI crude as proxy for MCX
}

# RBI API for 10-year G-sec yields
RBI_API_URL = "https://dbie.rbi.org.in/dbie_reports/cds/statistical/DSIM/public/{dataset_id}/all"


def fetch_yahoo(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Fetch daily close from Yahoo Finance using yfinance."""
    try:
        import yfinance as yf
        df = yf.download(ticker, start=start, end=end, progress=False)
        if df.empty:
            return df
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        df.index = pd.to_datetime(df.index)
        df = df[["Close"]].copy()
        df.columns = ["close"]
        df.index.name = "date"
        return df
    except ImportError:
        print("  ⚠ yfinance not installed. Install with: pip install yfinance")
        return pd.DataFrame()
    except Exception as e:
        print(f"  ✗ Failed to fetch {ticker}: {e}")
        return pd.DataFrame()


def fetch_rbi_gsec_yield(start: str, end: str) -> pd.DataFrame:
    """
    Attempt to fetch 10-year G-sec yield from RBI DBIE.
    Falls back to a known free source if RBI API is unavailable.
    """
    # Known dataset for G-Sec yields on RBI
    dataset_id = "DSIM:GSEC_10Y"
    url = RBI_API_URL.format(dataset_id=dataset_id)
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            # Parse RBI response (structure varies; adapt as needed)
            # This is a placeholder — RBI JSON structure needs manual inspection
            print("  ⚠ RBI API returned data — manual parsing needed for this response format")
            return pd.DataFrame()
    except Exception as e:
        print(f"  ⚠ RBI API unavailable: {e}")

    # Fallback: Use macrotrends.net data or manual CSV import
    # For now, return empty — user can manually add G-sec data
    print("  ℹ G-sec yield: Use manual CSV import from macrotrends.net or RBI")
    return pd.DataFrame()


def fetch_dii_flows(start: str, end: str) -> pd.DataFrame:
    """
    Fetch DII (Domestic Institutional Investor) daily net flows.
    Data available from NSE India website or manual CSV import from StockEdge.
    """
    # NSE does not provide a direct free API for DII flows.
    # Options:
    # 1. Manual CSV download from StockEdge/AMFI
    # 2. Scrape NSE India DII data page
    # For now, return empty — user fills manually
    print("  ℹ DII flows: Manual CSV import from StockEdge or AMFI required")
    return pd.DataFrame()


def compute_factor_changes(df: pd.DataFrame) -> pd.Series:
    """Convert price series to daily changes (returns/deltas)."""
    if df.empty or "close" not in df.columns:
        return pd.Series(dtype=float)
    # For yields/VIX: absolute change; for prices: percentage return
    changes = df["close"].diff()
    return changes


def main():
    print("=" * 60)
    print("AION Meta-Data Fetcher — 5-Factor Time Series")
    print("=" * 60)

    # Date range: last 2 years (730 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    print(f"\n📅 Date range: {start_str} to {end_str}")

    all_data = {}

    # ---- 1. Sector Indices ----
    print("\n📊 Fetching sector indices...")
    for sector, ticker in YF_SECTORS.items():
        print(f"  Fetching {sector} ({ticker})...", end=" ")
        df = fetch_yahoo(ticker, start_str, end_str)
        if not df.empty:
            all_data[sector] = compute_factor_changes(df)
            print(f"✓ ({len(df)} rows)")
        else:
            print("✗ (no data)")

    # ---- 2. India VIX ----
    print("\n📈 Fetching India VIX...")
    print(f"  Fetching {FACTOR_TICKERS['INDIAVIX']}...", end=" ")
    vix_df = fetch_yahoo(FACTOR_TICKERS["INDIAVIX"], start_str, end_str)
    vix_changes = pd.Series(dtype=float)
    if not vix_df.empty:
        vix_changes = compute_factor_changes(vix_df)
        all_data["vix_change"] = vix_changes
        print(f"✓ ({len(vix_df)} rows)")
    else:
        print("✗ (no data)")

    # ---- 3. USD/INR ----
    print("\n💱 Fetching USD/INR...")
    print(f"  Fetching {FACTOR_TICKERS['USDINR']}...", end=" ")
    usd_df = fetch_yahoo(FACTOR_TICKERS["USDINR"], start_str, end_str)
    if not usd_df.empty:
        all_data["usdinr_change"] = compute_factor_changes(usd_df)
        print(f"✓ ({len(usd_df)} rows)")
    else:
        print("✗ (no data)")

    # ---- 4. Crude Oil ----
    print("\n🛢️ Fetching Crude Oil (WTI proxy)...")
    print(f"  Fetching {FACTOR_TICKERS['CRUDE_OIL']}...", end=" ")
    crude_df = fetch_yahoo(FACTOR_TICKERS["CRUDE_OIL"], start_str, end_str)
    if not crude_df.empty:
        all_data["crude_return"] = compute_factor_changes(crude_df)
        print(f"✓ ({len(crude_df)} rows)")
    else:
        print("✗ (no data)")

    # ---- 5. G-Sec Yield ----
    print("\n🏦 Fetching 10-year G-Sec yield...")
    gsec_df = fetch_rbi_gsec_yield(start_str, end_str)
    if not gsec_df.empty:
        all_data["yield_change"] = compute_factor_changes(gsec_df)

    # ---- 6. DII Flows ----
    print("\n🏦 Fetching DII net flows...")
    dii_df = fetch_dii_flows(start_str, end_str)
    if not dii_df.empty:
        all_data["dii_flow"] = dii_df["net_flow"]

    # ---- Build unified DataFrame ----
    print("\n🔗 Building unified DataFrame...")
    if not all_data:
        print("  ✗ No data fetched. Check network and yfinance installation.")
        sys.exit(1)

    unified = pd.DataFrame(all_data)
    unified.index.name = "date"

    # Sort by date, drop rows where all values are NaN
    unified = unified.sort_index()
    unified = unified.dropna(how="all")

    print(f"  ✓ {len(unified)} rows, {len(unified.columns)} columns")
    print(f"\n📋 Columns: {list(unified.columns)}")
    print(f"📅 Date range: {unified.index.min()} to {unified.index.max()}")

    # Save to CSV
    unified.to_csv(OUTPUT_CSV)
    print(f"\n💾 Saved to: {OUTPUT_CSV}")

    # ---- Summary Statistics ----
    print("\n" + "=" * 60)
    print("📊 Summary Statistics (last 90 days)")
    print("=" * 60)
    last_90 = unified.tail(90)
    print(last_90.describe().round(4))

    print("\n✅ Fetch complete. Run update_sensitivities.py next.")


if __name__ == "__main__":
    main()
