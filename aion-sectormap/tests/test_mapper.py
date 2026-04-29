# =============================================================================
# AION Open-Source Project: AION SectorMap
# File: test_mapper.py
# Description: Unit tests for SectorMapper class
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
Unit Tests for SectorMapper.

This module contains comprehensive tests for the SectorMapper class,
including tests for:
    - Ticker lookups (sector, industry, group, GIN)
    - Reverse lookups (sector → tickers)
    - DataFrame mapping
    - Error handling
    - Edge cases

Run tests:
    pytest tests/test_mapper.py -v
    python -m pytest tests/test_mapper.py -v

Example:
    $ pytest tests/test_mapper.py -v
    $ pytest tests/test_mapper.py::TestSectorMapper::test_get_sector
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aion_sectormap import SectorMapper


class TestSectorMapperInit:
    """Tests for SectorMapper initialization."""

    def test_init_default_path(self) -> None:
        """Test initialization with default data path."""
        mapper = SectorMapper()
        assert len(mapper) > 0, "Mapper should have tickers loaded"
        assert isinstance(mapper.get_all_tickers(), list)

    def test_init_custom_path(self, sample_data_path: str) -> None:
        """Test initialization with custom data path."""
        mapper = SectorMapper(data_path=sample_data_path)
        assert len(mapper) == 5, "Should load 5 tickers from sample data"

    def test_init_file_not_found(self) -> None:
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            SectorMapper(data_path='/nonexistent/path/sector_map.json')

    def test_init_invalid_json(self, invalid_json_path: str) -> None:
        """Test initialization with invalid JSON file."""
        with pytest.raises(json.JSONDecodeError):
            SectorMapper(data_path=invalid_json_path)


class TestSectorMapperLookups:
    """Tests for ticker lookup methods."""

    @pytest.fixture
    def mapper(self) -> SectorMapper:
        """Create SectorMapper instance for tests."""
        return SectorMapper()

    def test_get_sector_real_tickers(self, mapper: SectorMapper) -> None:
        """Test get_sector with real NSE tickers."""
        # Test major tickers that should exist
        test_cases = [
            ('RELIANCE', 'Oil, Gas & Consumable Fuels'),
            ('HDFCBANK', 'Financial Services'),
            ('ICICIBANK', 'Financial Services'),
            ('SBIN', 'Financial Services'),
            ('TATASTEEL', 'Metals & Mining'),
            ('SUNPHARMA', 'Healthcare'),
        ]

        for ticker, expected_sector in test_cases:
            if ticker in mapper:
                sector = mapper.get_sector(ticker)
                assert sector == expected_sector, f"{ticker} should be in {expected_sector}"

    def test_get_sector_case_insensitive(self, mapper: SectorMapper) -> None:
        """Test that sector lookup is case-insensitive."""
        sector_upper = mapper.get_sector('RELIANCE')
        sector_lower = mapper.get_sector('reliance')
        sector_mixed = mapper.get_sector('Reliance')

        assert sector_upper == sector_lower == sector_mixed

    def test_get_sector_unknown_ticker(self, mapper: SectorMapper) -> None:
        """Test get_sector with unknown ticker."""
        sector = mapper.get_sector('INVALIDTICKER')
        assert sector == 'Unknown'

    def test_get_sector_custom_default(self, mapper: SectorMapper) -> None:
        """Test get_sector with custom default value."""
        sector = mapper.get_sector('INVALIDTICKER', default='N/A')
        assert sector == 'N/A'

    def test_get_industry(self, mapper: SectorMapper) -> None:
        """Test get_industry method."""
        if 'RELIANCE' in mapper:
            industry = mapper.get_industry('RELIANCE')
            assert industry != 'Unknown', "Should return valid industry"

    def test_get_group(self, mapper: SectorMapper) -> None:
        """Test get_group method."""
        if 'HDFCBANK' in mapper:
            group = mapper.get_group('HDFCBANK')
            assert group != 'Unknown', "Should return valid group"
            assert 'HDFC' in group.upper(), "HDFCBANK should be in HDFC group"

    def test_get_gin(self, mapper: SectorMapper) -> None:
        """Test get_gin method."""
        if 'RELIANCE' in mapper:
            gin = mapper.get_gin('RELIANCE')
            assert gin != 'Unknown', "Should return valid GIN"
            assert len(gin) > 0, "GIN should not be empty"

    def test_get_company_name(self, mapper: SectorMapper) -> None:
        """Test get_company_name method."""
        if 'RELIANCE' in mapper:
            name = mapper.get_company_name('RELIANCE')
            assert 'Reliance' in name, "Should return company name with 'Reliance'"


class TestReverseLookups:
    """Tests for reverse lookup methods (sector → tickers)."""

    @pytest.fixture
    def mapper(self) -> SectorMapper:
        """Create SectorMapper instance for tests."""
        return SectorMapper()

    def test_get_tickers_in_sector(self, mapper: SectorMapper) -> None:
        """Test getting all tickers in a sector."""
        # Financial Services should have many tickers
        tickers = mapper.get_tickers_in_sector('Financial Services')
        assert len(tickers) > 0, "Financial Services should have tickers"
        assert isinstance(tickers, list)

    def test_get_tickers_in_sector_case_insensitive(self, mapper: SectorMapper) -> None:
        """Test that sector lookup is case-insensitive."""
        tickers_upper = mapper.get_tickers_in_sector('Financial Services')
        tickers_lower = mapper.get_tickers_in_sector('financial services')
        tickers_mixed = mapper.get_tickers_in_sector('FINANCIAL SERVICES')

        assert tickers_upper == tickers_lower == tickers_mixed

    def test_get_tickers_in_unknown_sector(self, mapper: SectorMapper) -> None:
        """Test getting tickers in non-existent sector."""
        tickers = mapper.get_tickers_in_sector('NonExistent Sector')
        assert tickers == [], "Should return empty list for unknown sector"

    def test_get_tickers_in_industry(self, mapper: SectorMapper) -> None:
        """Test get_tickers_in_industry method."""
        tickers = mapper.get_tickers_in_industry('Financial Services')
        assert len(tickers) > 0

    def test_get_tickers_in_group(self, mapper: SectorMapper) -> None:
        """Test get_tickers_in_group method."""
        # Test with a known group
        groups = mapper.get_all_groups()
        if groups:
            group = groups[0]
            tickers = mapper.get_tickers_in_group(group)
            assert len(tickers) > 0

    def test_get_all_sectors(self, mapper: SectorMapper) -> None:
        """Test getting all sectors."""
        sectors = mapper.get_all_sectors()
        assert len(sectors) > 0, "Should have at least one sector"
        assert isinstance(sectors, list)
        assert 'Financial Services' in sectors, "Should have Financial Services sector"

    def test_get_all_groups(self, mapper: SectorMapper) -> None:
        """Test getting all groups."""
        groups = mapper.get_all_groups()
        assert len(groups) > 0, "Should have at least one group"
        assert isinstance(groups, list)

    def test_get_all_tickers(self, mapper: SectorMapper) -> None:
        """Test getting all tickers."""
        tickers = mapper.get_all_tickers()
        assert len(tickers) > 0, "Should have at least one ticker"
        assert isinstance(tickers, list)


class TestDataFrameMapping:
    """Tests for DataFrame mapping functionality."""

    @pytest.fixture
    def mapper(self) -> SectorMapper:
        """Create SectorMapper instance for tests."""
        return SectorMapper()

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Create sample DataFrame for testing."""
        return pd.DataFrame({
            'ticker': ['RELIANCE', 'HDFCBANK', 'TCS', 'INVALID'],
            'price': [2500.0, 1600.0, 3500.0, 100.0],
        })

    def test_map_basic(self, mapper: SectorMapper, sample_df: pd.DataFrame) -> None:
        """Test basic DataFrame mapping."""
        result = mapper.map(sample_df)

        assert 'sector' in result.columns
        assert 'industry' in result.columns
        assert 'group' in result.columns
        assert len(result) == len(sample_df)

    def test_map_custom_ticker_column(self, mapper: SectorMapper) -> None:
        """Test mapping with custom ticker column name."""
        df = pd.DataFrame({
            'symbol': ['RELIANCE', 'HDFCBANK'],
            'price': [2500.0, 1600.0],
        })

        result = mapper.map(df, ticker_column='symbol')
        assert 'sector' in result.columns

    def test_map_missing_ticker_column(self, mapper: SectorMapper, sample_df: pd.DataFrame) -> None:
        """Test mapping with non-existent ticker column."""
        with pytest.raises(KeyError):
            mapper.map(sample_df, ticker_column='nonexistent')

    def test_map_add_gin(self, mapper: SectorMapper, sample_df: pd.DataFrame) -> None:
        """Test mapping with GIN column."""
        result = mapper.map(sample_df, add_gin=True)
        assert 'gin' in result.columns

    def test_map_add_company_name(self, mapper: SectorMapper, sample_df: pd.DataFrame) -> None:
        """Test mapping with company name column."""
        result = mapper.map(sample_df, add_company_name=True)
        assert 'company_name' in result.columns

    def test_map_fill_value(self, mapper: SectorMapper, sample_df: pd.DataFrame) -> None:
        """Test mapping with custom fill value."""
        result = mapper.map(sample_df, fill_value='N/A')

        # Check that invalid ticker has custom fill value
        invalid_row = result[result['ticker'] == 'INVALID']
        if len(invalid_row) > 0:
            assert invalid_row.iloc[0]['sector'] == 'N/A'

    def test_map_preserves_original(self, mapper: SectorMapper, sample_df: pd.DataFrame) -> None:
        """Test that mapping doesn't modify original DataFrame."""
        original_columns = list(sample_df.columns)
        mapper.map(sample_df)
        assert list(sample_df.columns) == original_columns


class TestSummaryMethods:
    """Tests for summary and statistics methods."""

    @pytest.fixture
    def mapper(self) -> SectorMapper:
        """Create SectorMapper instance for tests."""
        return SectorMapper()

    def test_get_sector_summary(self, mapper: SectorMapper) -> None:
        """Test get_sector_summary method."""
        summary = mapper.get_sector_summary()

        assert isinstance(summary, pd.DataFrame)
        assert 'sector' in summary.columns
        assert 'ticker_count' in summary.columns
        assert len(summary) > 0

        # Check sorting (descending by count)
        counts = summary['ticker_count'].tolist()
        assert counts == sorted(counts, reverse=True)

    def test_get_group_summary(self, mapper: SectorMapper) -> None:
        """Test get_group_summary method."""
        summary = mapper.get_group_summary()

        assert isinstance(summary, pd.DataFrame)
        assert 'group' in summary.columns
        assert 'ticker_count' in summary.columns

    def test_get_mapping_stats(self, mapper: SectorMapper) -> None:
        """Test get_mapping_stats method."""
        stats = mapper.get_mapping_stats()

        assert isinstance(stats, dict)
        assert 'total_tickers' in stats
        assert 'total_sectors' in stats
        assert 'total_groups' in stats
        assert stats['total_tickers'] > 0
        assert stats['total_sectors'] > 0

    def test_search_ticker(self, mapper: SectorMapper) -> None:
        """Test search_ticker method."""
        # Search for HDFC
        results = mapper.search_ticker('HDFC')

        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0, "Should find HDFC companies"

        # All results should contain HDFC
        for _, row in results.iterrows():
            assert 'HDFC' in row['ticker'].upper() or 'HDFC' in row['company_name'].upper()


class TestSpecialMethods:
    """Tests for special methods (__repr__, __len__, __contains__)."""

    @pytest.fixture
    def mapper(self) -> SectorMapper:
        """Create SectorMapper instance for tests."""
        return SectorMapper()

    def test_repr(self, mapper: SectorMapper) -> None:
        """Test __repr__ method."""
        repr_str = repr(mapper)
        assert 'SectorMapper' in repr_str
        assert 'tickers=' in repr_str

    def test_len(self, mapper: SectorMapper) -> None:
        """Test __len__ method."""
        length = len(mapper)
        assert length > 0
        assert length == len(mapper.get_all_tickers())

    def test_contains_existing(self, mapper: SectorMapper) -> None:
        """Test __contains__ with existing ticker."""
        assert 'RELIANCE' in mapper
        assert 'HDFCBANK' in mapper

    def test_contains_not_existing(self, mapper: SectorMapper) -> None:
        """Test __contains__ with non-existing ticker."""
        assert 'INVALIDTICKER' not in mapper

    def test_contains_case_insensitive(self, mapper: SectorMapper) -> None:
        """Test __contains__ is case-insensitive."""
        assert 'reliance' in mapper
        assert 'Reliance' in mapper


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def mapper(self) -> SectorMapper:
        """Create SectorMapper instance for tests."""
        return SectorMapper()

    def test_empty_ticker(self, mapper: SectorMapper) -> None:
        """Test lookup with empty ticker."""
        sector = mapper.get_sector('')
        assert sector == 'Unknown'

    def test_whitespace_ticker(self, mapper: SectorMapper) -> None:
        """Test lookup with whitespace ticker."""
        sector = mapper.get_sector('   ')
        assert sector == 'Unknown'

    def test_special_characters_ticker(self, mapper: SectorMapper) -> None:
        """Test lookup with special characters in ticker."""
        sector = mapper.get_sector('REL@ANCE')
        assert sector == 'Unknown'

    def test_very_long_ticker(self, mapper: SectorMapper) -> None:
        """Test lookup with very long ticker."""
        sector = mapper.get_sector('A' * 100)
        assert sector == 'Unknown'

    def test_numeric_ticker(self, mapper: SectorMapper) -> None:
        """Test lookup with numeric ticker."""
        sector = mapper.get_sector('12345')
        assert sector == 'Unknown'


# Fixtures

@pytest.fixture
def sample_data_path(tmp_path: Path) -> str:
    """Create sample sector map JSON file for testing."""
    sample_data: Dict[str, Dict[str, Any]] = {
        'RELIANCE': {
            'sector': 'Oil, Gas & Consumable Fuels',
            'industry': 'Oil, Gas & Consumable Fuels',
            'group': 'Mukesh Ambani Group',
            'gin': 'MUKESHAMBANI-01',
            'company_name': 'Reliance Industries Limited',
        },
        'HDFCBANK': {
            'sector': 'Financial Services',
            'industry': 'Financial Services',
            'group': 'HDFC Bank Limited',
            'gin': 'HDFCBANKLIMI-01',
            'company_name': 'HDFC Bank Limited',
        },
        'TCS': {
            'sector': 'Software & Services',
            'industry': 'Software & Services',
            'group': 'Tata Sons',
            'gin': 'TATASONS-01',
            'company_name': 'Tata Consultancy Services Limited',
        },
        'INFY': {
            'sector': 'Software & Services',
            'industry': 'Software & Services',
            'group': 'Infosys Limited',
            'gin': 'INFOSYSLIMIT-01',
            'company_name': 'Infosys Limited',
        },
        'SBIN': {
            'sector': 'Financial Services',
            'industry': 'Financial Services',
            'group': 'State Bank of India',
            'gin': 'STATEBANKOFI-01',
            'company_name': 'State Bank of India',
        },
    }

    file_path = tmp_path / 'sector_map.json'
    with open(file_path, 'w') as f:
        json.dump(sample_data, f, indent=2)

    return str(file_path)


@pytest.fixture
def invalid_json_path(tmp_path: Path) -> str:
    """Create invalid JSON file for testing."""
    file_path = tmp_path / 'invalid.json'
    with open(file_path, 'w') as f:
        f.write('{ invalid json }')
    return str(file_path)


# Integration Tests

class TestIntegration:
    """Integration tests with real data."""

    def test_full_workflow(self) -> None:
        """Test complete workflow with real data."""
        # Initialize
        mapper = SectorMapper()

        # Get stats
        stats = mapper.get_mapping_stats()
        assert stats['total_tickers'] > 0

        # Lookup some tickers
        if 'RELIANCE' in mapper:
            sector = mapper.get_sector('RELIANCE')
            assert sector != 'Unknown'

        # Get sector tickers
        sectors = mapper.get_all_sectors()
        if sectors:
            tickers = mapper.get_tickers_in_sector(sectors[0])
            assert len(tickers) > 0

        # Map DataFrame
        df = pd.DataFrame({'ticker': ['RELIANCE', 'HDFCBANK']})
        mapped = mapper.map(df)
        assert len(mapped) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
