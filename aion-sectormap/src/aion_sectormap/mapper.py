# =============================================================================
# AION Open-Source Project: AION SectorMap
# File: mapper.py
# Description: Core SectorMapper class for NSE ticker → sector/industry mapping
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
Sector Mapper for AION.

This module provides the core SectorMapper class for mapping NSE ticker symbols
to sectors, industries, business groups, and Group Identification Numbers (GIN).

Classes:
    SectorMapper: Main class for sector/company/group mappings.

Example:
    >>> from aion_sectormap import SectorMapper
    >>> mapper = SectorMapper()
    >>> mapper.get_sector('RELIANCE')
    'Oil, Gas & Consumable Fuels'
    >>> mapper.get_industry('TCS')
    'Software & Services'
    >>> mapper.get_group('HDFCBANK')
    'HDFC Bank Limited'
    >>> mapper.get_tickers_in_sector('Financial Services')
    ['HDFCBANK', 'ICICIBANK', 'KOTAKBANK', ...]
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)


class SectorMapper:
    """
    Mapper for NSE ticker → sector/industry/group relationships.

    This class provides comprehensive mapping between NSE ticker symbols,
    sectors, industries, and business groups using the official NSE Group
    Companies dataset (591 companies, 44 sectors, 340+ groups).

    The mapper supports:
        - Forward lookups: ticker → sector/industry/group
        - Reverse lookups: sector → list of tickers
        - Batch processing: DataFrame → DataFrame with added columns
        - Unknown ticker handling with configurable fill values

    Attributes:
        data_path (str): Path to the JSON file with ticker mappings.
        sector_map (Dict): Dictionary with ticker → sector/industry/group data.

    Example:
        >>> mapper = SectorMapper()
        >>> sector = mapper.get_sector('RELIANCE')
        >>> industry = mapper.get_industry('TCS')
        >>> group = mapper.get_group('HDFCBANK')
        >>> tickers = mapper.get_tickers_in_sector('Financial Services')

        >>> # Batch processing with DataFrame
        >>> import pandas as pd
        >>> df = pd.DataFrame({'ticker': ['RELIANCE', 'TCS', 'HDFCBANK']})
        >>> df_mapped = mapper.map(df)
        >>> print(df_mapped)
             ticker                      sector  ...
        0  RELIANCE  Oil, Gas & Consumable Fuels  ...
        1       TCS         Software & Services  ...
        2  HDFCBANK          Financial Services  ...
    """

    def __init__(self, data_path: Optional[str] = None) -> None:
        """
        Initialize the SectorMapper.

        Loads the sector mapping data from a JSON file. If no path is provided,
        uses the default location within the package data directory.

        Args:
            data_path: Path to JSON file with ticker mappings.
                If None, uses default location in package data/ directory.

        Raises:
            FileNotFoundError: If data file not found at specified or default location.
            json.JSONDecodeError: If JSON file is malformed.

        Example:
            >>> # Use default data path
            >>> mapper = SectorMapper()

            >>> # Use custom data path
            >>> mapper = SectorMapper('/path/to/custom/sector_map.json')
        """
        if data_path is None:
            # Try multiple locations for default data
            possible_paths = [
                os.path.join(os.path.dirname(__file__), 'data', 'sector_map.json'),
                os.path.join(os.path.dirname(__file__), '..', 'data', 'sector_map.json'),
                'src/aion_sectormap/data/sector_map.json',
                'aion-sectormap/src/aion_sectormap/data/sector_map.json',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    data_path = path
                    break
            else:
                # Use package default
                data_path = os.path.join(os.path.dirname(__file__), 'data', 'sector_map.json')

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Sector mapping data not found at {data_path}")

        self.data_path = data_path
        self.sector_map: Dict[str, Dict[str, Any]] = {}
        self._sector_to_tickers: Dict[str, List[str]] = {}
        self._industry_to_tickers: Dict[str, List[str]] = {}
        self._group_to_tickers: Dict[str, List[str]] = {}
        self._gin_to_tickers: Dict[str, List[str]] = {}

        self._load_data()
        self._build_reverse_lookups()

    def _load_data(self) -> None:
        """Load sector mapping data from JSON file."""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.sector_map = json.load(f)
        logger.info(f"Loaded sector mappings for {len(self.sector_map)} tickers from {self.data_path}")

    def _build_reverse_lookups(self) -> None:
        """Build reverse lookup dictionaries for sector/industry/group → tickers."""
        for ticker, data in self.sector_map.items():
            sector = data.get('sector', 'Unknown')
            industry = data.get('industry', 'Unknown')
            group = data.get('group', 'Unknown')
            gin = data.get('gin', 'Unknown')

            # Sector → Tickers
            if sector not in self._sector_to_tickers:
                self._sector_to_tickers[sector] = []
            self._sector_to_tickers[sector].append(ticker)

            # Industry → Tickers
            if industry not in self._industry_to_tickers:
                self._industry_to_tickers[industry] = []
            self._industry_to_tickers[industry].append(ticker)

            # Group → Tickers
            if group not in self._group_to_tickers:
                self._group_to_tickers[group] = []
            self._group_to_tickers[group].append(ticker)

            # GIN → Tickers
            if gin not in self._gin_to_tickers:
                self._gin_to_tickers[gin] = []
            self._gin_to_tickers[gin].append(ticker)

    def get_sector(self, ticker: str, default: str = 'Unknown') -> str:
        """
        Get sector for a given NSE ticker.

        Args:
            ticker: NSE ticker symbol (case-insensitive).
            default: Default value to return if ticker not found.

        Returns:
            Sector name or default value if ticker not found.

        Example:
            >>> mapper.get_sector('RELIANCE')
            'Oil, Gas & Consumable Fuels'
            >>> mapper.get_sector('INVALID')
            'Unknown'
            >>> mapper.get_sector('INVALID', default='N/A')
            'N/A'
        """
        ticker_upper = ticker.upper()
        data = self.sector_map.get(ticker_upper)
        if data is None:
            logger.debug(f"Ticker {ticker} not found in sector map")
            return default
        return data.get('sector', default)

    def get_industry(self, ticker: str, default: str = 'Unknown') -> str:
        """
        Get industry for a given NSE ticker.

        Args:
            ticker: NSE ticker symbol (case-insensitive).
            default: Default value to return if ticker not found.

        Returns:
            Industry name or default value if ticker not found.

        Example:
            >>> mapper.get_industry('TCS')
            'Software & Services'
            >>> mapper.get_industry('INFY')
            'Software & Services'
        """
        ticker_upper = ticker.upper()
        data = self.sector_map.get(ticker_upper)
        if data is None:
            logger.debug(f"Ticker {ticker} not found in sector map")
            return default
        return data.get('industry', default)

    def get_group(self, ticker: str, default: str = 'Unknown') -> str:
        """
        Get business group for a given NSE ticker.

        Args:
            ticker: NSE ticker symbol (case-insensitive).
            default: Default value to return if ticker not found.

        Returns:
            Business group name or default value if ticker not found.

        Example:
            >>> mapper.get_group('HDFCBANK')
            'HDFC Bank Limited'
            >>> mapper.get_group('RELIANCE')
            'Mukesh Ambani Group'
        """
        ticker_upper = ticker.upper()
        data = self.sector_map.get(ticker_upper)
        if data is None:
            logger.debug(f"Ticker {ticker} not found in sector map")
            return default
        return data.get('group', default)

    def get_gin(self, ticker: str, default: str = 'Unknown') -> str:
        """
        Get Group Identification Number (GIN) for a given NSE ticker.

        Args:
            ticker: NSE ticker symbol (case-insensitive).
            default: Default value to return if ticker not found.

        Returns:
            GIN code or default value if ticker not found.

        Example:
            >>> mapper.get_gin('HDFCBANK')
            'HDFCBANKLIMI-01'
            >>> mapper.get_gin('RELIANCE')
            'MUKESHAMBANI-01'
        """
        ticker_upper = ticker.upper()
        data = self.sector_map.get(ticker_upper)
        if data is None:
            logger.debug(f"Ticker {ticker} not found in sector map")
            return default
        return data.get('gin', default)

    def get_company_name(self, ticker: str, default: str = 'Unknown') -> str:
        """
        Get full company name for a given NSE ticker.

        Args:
            ticker: NSE ticker symbol (case-insensitive).
            default: Default value to return if ticker not found.

        Returns:
            Full company name or default value if ticker not found.

        Example:
            >>> mapper.get_company_name('RELIANCE')
            'Reliance Industries Limited'
            >>> mapper.get_company_name('TCS')
            'Tata Consultancy Services Limited'
        """
        ticker_upper = ticker.upper()
        data = self.sector_map.get(ticker_upper)
        if data is None:
            logger.debug(f"Ticker {ticker} not found in sector map")
            return default
        return data.get('company_name', default)

    def get_tickers_in_sector(self, sector: str) -> List[str]:
        """
        Get all ticker symbols in a given sector.

        Args:
            sector: Sector name (case-insensitive).

        Returns:
            List of ticker symbols in the sector. Empty list if sector not found.

        Example:
            >>> mapper.get_tickers_in_sector('Financial Services')
            ['HDFCBANK', 'ICICIBANK', 'KOTAKBANK', ...]
            >>> mapper.get_tickers_in_sector('Software & Services')
            ['TCS', 'INFY', 'HCLTECH', ...]
        """
        sector_lower = sector.lower()
        for s, tickers in self._sector_to_tickers.items():
            if s.lower() == sector_lower:
                return tickers.copy()
        logger.debug(f"Sector {sector} not found")
        return []

    def get_tickers_in_industry(self, industry: str) -> List[str]:
        """
        Get all ticker symbols in a given industry.

        Args:
            industry: Industry name (case-insensitive).

        Returns:
            List of ticker symbols in the industry. Empty list if industry not found.

        Example:
            >>> mapper.get_tickers_in_industry('Software & Services')
            ['TCS', 'INFY', 'HCLTECH', ...]
        """
        industry_lower = industry.lower()
        for i, tickers in self._industry_to_tickers.items():
            if i.lower() == industry_lower:
                return tickers.copy()
        logger.debug(f"Industry {industry} not found")
        return []

    def get_tickers_in_group(self, group: str) -> List[str]:
        """
        Get all ticker symbols in a given business group.

        Args:
            group: Business group name (case-insensitive).

        Returns:
            List of ticker symbols in the group. Empty list if group not found.

        Example:
            >>> mapper.get_tickers_in_group('Mukesh Ambani Group')
            ['RELIANCE', 'NETWORK18', 'JAMNAGARUTILITIES']
            >>> mapper.get_tickers_in_group('HDFC Bank Limited')
            ['HDFCBANK', 'HDBFINANCIALSERVICES']
        """
        group_lower = group.lower()
        for g, tickers in self._group_to_tickers.items():
            if g.lower() == group_lower:
                return tickers.copy()
        logger.debug(f"Group {group} not found")
        return []

    def get_tickers_by_gin(self, gin: str) -> List[str]:
        """
        Get all ticker symbols with a given Group Identification Number (GIN).

        Args:
            gin: GIN code (case-insensitive).

        Returns:
            List of ticker symbols with the GIN. Empty list if GIN not found.

        Example:
            >>> mapper.get_tickers_by_gin('MUKESHAMBANI-01')
            ['RELIANCE', 'NETWORK18', ...]
        """
        gin_upper = gin.upper()
        return self._gin_to_tickers.get(gin_upper, []).copy()

    def get_all_sectors(self) -> List[str]:
        """
        Get list of all unique sectors.

        Returns:
            List of all sector names.

        Example:
            >>> sectors = mapper.get_all_sectors()
            >>> len(sectors)
            44
        """
        return list(self._sector_to_tickers.keys())

    def get_all_industries(self) -> List[str]:
        """
        Get list of all unique industries.

        Returns:
            List of all industry names.
        """
        return list(self._industry_to_tickers.keys())

    def get_all_groups(self) -> List[str]:
        """
        Get list of all unique business groups.

        Returns:
            List of all business group names.

        Example:
            >>> groups = mapper.get_all_groups()
            >>> len(groups)
            340
        """
        return list(self._group_to_tickers.keys())

    def get_all_tickers(self) -> List[str]:
        """
        Get list of all ticker symbols in the database.

        Returns:
            List of all ticker symbols.

        Example:
            >>> tickers = mapper.get_all_tickers()
            >>> len(tickers)
            591
        """
        return list(self.sector_map.keys())

    def map(
        self,
        df: pd.DataFrame,
        ticker_column: str = 'ticker',
        add_sector: bool = True,
        add_industry: bool = True,
        add_group: bool = True,
        add_gin: bool = False,
        add_company_name: bool = False,
        fill_value: str = 'Unknown',
    ) -> pd.DataFrame:
        """
        Add sector, industry, and group columns to a DataFrame.

        This method takes a DataFrame with a ticker column and adds new columns
        with sector, industry, group, and optionally GIN and company name mappings.

        Args:
            df: Input DataFrame with ticker symbols.
            ticker_column: Name of column containing ticker symbols.
                Default is 'ticker'.
            add_sector: Whether to add 'sector' column. Default is True.
            add_industry: Whether to add 'industry' column. Default is True.
            add_group: Whether to add 'group' column. Default is True.
            add_gin: Whether to add 'gin' column. Default is False.
            add_company_name: Whether to add 'company_name' column. Default is False.
            fill_value: Value to use for unknown tickers. Default is 'Unknown'.

        Returns:
            DataFrame with added sector/industry/group columns.

        Raises:
            KeyError: If ticker_column not found in DataFrame.

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'INVALID']})
            >>> df_mapped = mapper.map(df)
            >>> print(df_mapped)
                 ticker                      sector  ...
            0  RELIANCE  Oil, Gas & Consumable Fuels  ...
            1       TCS         Software & Services  ...
            2  HDFCBANK          Financial Services  ...
            3   INVALID                     Unknown  ...

            >>> # Add GIN and company name
            >>> df_mapped = mapper.map(df, add_gin=True, add_company_name=True)
        """
        if ticker_column not in df.columns:
            raise KeyError(f"Column '{ticker_column}' not found in DataFrame")

        # Create a copy to avoid modifying the original
        result_df = df.copy()

        # Get tickers as a list for mapping
        tickers = result_df[ticker_column].astype(str).str.upper()

        # Add sector column
        if add_sector:
            result_df['sector'] = tickers.apply(
                lambda x: self.sector_map.get(x, {}).get('sector', fill_value)
            )

        # Add industry column
        if add_industry:
            result_df['industry'] = tickers.apply(
                lambda x: self.sector_map.get(x, {}).get('industry', fill_value)
            )

        # Add group column
        if add_group:
            result_df['group'] = tickers.apply(
                lambda x: self.sector_map.get(x, {}).get('group', fill_value)
            )

        # Add GIN column
        if add_gin:
            result_df['gin'] = tickers.apply(
                lambda x: self.sector_map.get(x, {}).get('gin', fill_value)
            )

        # Add company name column
        if add_company_name:
            result_df['company_name'] = tickers.apply(
                lambda x: self.sector_map.get(x, {}).get('company_name', fill_value)
            )

        return result_df

    def get_sector_summary(self) -> pd.DataFrame:
        """
        Get summary of tickers per sector.

        Returns:
            DataFrame with sector names and ticker counts, sorted by count descending.

        Example:
            >>> summary = mapper.get_sector_summary()
            >>> print(summary.head())
                                 sector  ticker_count
            0              Financial Services           156
            1                    Software & Services            45
            2         Oil, Gas & Consumable Fuels            32
        """
        summary_data = [
            {'sector': sector, 'ticker_count': len(tickers)}
            for sector, tickers in self._sector_to_tickers.items()
        ]
        summary_df = pd.DataFrame(summary_data)
        return summary_df.sort_values('ticker_count', ascending=False).reset_index(drop=True)

    def get_group_summary(self) -> pd.DataFrame:
        """
        Get summary of tickers per business group.

        Returns:
            DataFrame with group names and ticker counts, sorted by count descending.

        Example:
            >>> summary = mapper.get_group_summary()
            >>> print(summary.head(10))
                                      group  ticker_count
            0         Mukesh Ambani Group            25
            1             HDFC Bank Limited            18
            2    Punjab National Bank            15
        """
        summary_data = [
            {'group': group, 'ticker_count': len(tickers)}
            for group, tickers in self._group_to_tickers.items()
        ]
        summary_df = pd.DataFrame(summary_data)
        return summary_df.sort_values('ticker_count', ascending=False).reset_index(drop=True)

    def search_ticker(self, query: str) -> pd.DataFrame:
        """
        Search for tickers by company name.

        Args:
            query: Search query (case-insensitive substring match).

        Returns:
            DataFrame with matching tickers and their sector/industry/group data.

        Example:
            >>> results = mapper.search_ticker('HDFC')
            >>> print(results)
                    ticker  ... company_name
            0     HDFCBANK  ... HDFC Bank Limited
            1  HDBFINANCIALSERVICES  ... HDB Financial Services Limited
        """
        query_lower = query.lower()
        matches = []

        for ticker, data in self.sector_map.items():
            company_name = data.get('company_name', '').lower()
            if query_lower in company_name:
                matches.append({
                    'ticker': ticker,
                    'sector': data.get('sector', 'Unknown'),
                    'industry': data.get('industry', 'Unknown'),
                    'group': data.get('group', 'Unknown'),
                    'gin': data.get('gin', 'Unknown'),
                    'company_name': data.get('company_name', 'Unknown'),
                })

        return pd.DataFrame(matches)

    def get_mapping_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the sector mapping database.

        Returns:
            Dictionary with mapping statistics.

        Example:
            >>> stats = mapper.get_mapping_stats()
            >>> print(stats)
            {
                'total_tickers': 591,
                'total_sectors': 44,
                'total_industries': 44,
                'total_groups': 340,
                'total_gins': 340
            }
        """
        return {
            'total_tickers': len(self.sector_map),
            'total_sectors': len(self._sector_to_tickers),
            'total_industries': len(self._industry_to_tickers),
            'total_groups': len(self._group_to_tickers),
            'total_gins': len(self._gin_to_tickers),
        }

    def __repr__(self) -> str:
        """Return string representation of SectorMapper."""
        stats = self.get_mapping_stats()
        return (
            f"SectorMapper(tickers={stats['total_tickers']}, "
            f"sectors={stats['total_sectors']}, "
            f"groups={stats['total_groups']})"
        )

    def __len__(self) -> int:
        """Return number of tickers in the mapping."""
        return len(self.sector_map)

    def __contains__(self, ticker: str) -> bool:
        """Check if a ticker exists in the mapping."""
        return ticker.upper() in self.sector_map
