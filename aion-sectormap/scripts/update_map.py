# =============================================================================
# AION Open-Source Project: AION SectorMap
# File: update_map.py
# Description: Script to update sector mapping from NSE data sources
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
Update Sector Mapping Script.

This script updates the sector mapping database by:
    1. Downloading fresh data from NSE website or local sources
    2. Validating mapping completeness
    3. Creating backup of old mapping
    4. Updating sector_map.json
    5. Logging changes

Usage:
    python scripts/update_map.py [--source nse|local] [--backup] [--validate]

Example:
    $ python scripts/update_map.py --source local --backup --validate
    $ python scripts/update_map.py  # Uses defaults
"""

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: 'requests' library not available. NSE scraping disabled.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SectorMapUpdater:
    """
    Updater for AION SectorMap database.

    This class handles downloading, validating, and updating the sector
    mapping database from various data sources.

    Attributes:
        data_path (str): Path to sector_map.json file.
        backup_path (str): Path to backup directory.
        source (str): Data source ('nse' or 'local').

    Example:
        >>> updater = SectorMapUpdater()
        >>> updater.run_update(backup=True, validate=True)
    """

    def __init__(
        self,
        data_path: Optional[str] = None,
        backup_dir: Optional[str] = None,
        source: str = 'local',
    ) -> None:
        """
        Initialize the SectorMapUpdater.

        Args:
            data_path: Path to sector_map.json file.
                Defaults to package data directory.
            backup_dir: Directory for backup files.
                Defaults to 'backups' subdirectory.
            source: Data source ('nse' or 'local').
                'nse' attempts to scrape NSE website.
                'local' uses local Excel/CSV files.

        Raises:
            ValueError: If source is invalid.
        """
        if source not in ('nse', 'local'):
            raise ValueError(f"Invalid source: {source}. Must be 'nse' or 'local'")

        # Set data path
        if data_path is None:
            data_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'src',
                'aion_sectormap',
                'data',
                'sector_map.json',
            )
        self.data_path = os.path.abspath(data_path)

        # Set backup directory
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(self.data_path), 'backups')
        self.backup_dir = os.path.abspath(backup_dir)

        self.source = source
        self.stats: Dict[str, Any] = {}

        logger.info(f"SectorMapUpdater initialized")
        logger.info(f"  Data path: {self.data_path}")
        logger.info(f"  Backup dir: {self.backup_dir}")
        logger.info(f"  Source: {self.source}")

    def load_current_mapping(self) -> Dict[str, Any]:
        """
        Load current sector mapping from JSON file.

        Returns:
            Current sector mapping dictionary.

        Raises:
            FileNotFoundError: If mapping file not found.
            json.JSONDecodeError: If JSON is malformed.
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Sector map not found at {self.data_path}")

        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_backup(self) -> Optional[str]:
        """
        Create backup of current sector mapping.

        Returns:
            Path to backup file, or None if no backup created.

        Example:
            >>> updater = SectorMapUpdater()
            >>> backup_path = updater.create_backup()
            >>> print(f"Backup created: {backup_path}")
        """
        if not os.path.exists(self.data_path):
            logger.warning("No existing mapping to backup")
            return None

        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)

        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'sector_map_backup_{timestamp}.json'
        backup_path = os.path.join(self.backup_dir, backup_filename)

        # Copy file
        shutil.copy2(self.data_path, backup_path)
        logger.info(f"Created backup: {backup_path}")

        return backup_path

    def fetch_from_nse(self) -> Optional[Dict[str, Any]]:
        """
        Fetch sector mapping data from NSE website.

        Returns:
            Sector mapping dictionary, or None if fetch failed.

        Note:
            This method requires the 'requests' library.
            NSE website scraping may be rate-limited.
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available. Cannot fetch from NSE.")
            return None

        logger.info("Fetching data from NSE website...")

        try:
            # NSE API endpoints
            indices = [
                'NIFTY 50',
                'NIFTY NEXT 50',
                'NIFTY 100',
                'NIFTY 500',
            ]

            all_companies: List[Dict[str, Any]] = []

            for index in indices:
                url = f"https://www.nseindia.com/api/equity-stockIndices?index={index.replace(' ', '%20')}"

                headers = {
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.nseindia.com/market-data/constituents",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                }

                session = requests.Session()
                session.headers.update(headers)

                # First request to set cookies
                session.get("https://www.nseindia.com/", timeout=10)

                # Fetch index constituents
                response = session.get(url, timeout=15)
                response.raise_for_status()

                data = response.json()
                records = data.get('records', [])

                for record in records:
                    all_companies.append({
                        'symbol': record.get('symbol', ''),
                        'company_name': record.get('companyName', ''),
                        'sector': index,
                    })

            logger.info(f"Fetched {len(all_companies)} companies from NSE")
            return self._companies_to_mapping(all_companies)

        except Exception as e:
            logger.error(f"Failed to fetch from NSE: {e}")
            return None

    def fetch_from_local(self, excel_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch sector mapping data from local Excel file.

        Args:
            excel_path: Path to Excel file with company data.
                Defaults to standard location in project.

        Returns:
            Sector mapping dictionary, or None if fetch failed.
        """
        if excel_path is None:
            # Try common locations
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', '..', 'Empirical List of Group Companies with GIN (Updated up to 31-Jan-2026).xlsx'),
                'Empirical List of Group Companies with GIN (Updated up to 31-Jan-2026).xlsx',
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    excel_path = path
                    break
            else:
                logger.error("Local Excel file not found")
                return None

        logger.info(f"Loading data from {excel_path}")

        try:
            df = pd.read_excel(excel_path)

            # Convert to mapping
            companies = []
            for _, row in df.iterrows():
                companies.append({
                    'symbol': self._company_to_ticker(row['Name of the Company']),
                    'company_name': row['Name of the Company'],
                    'sector': row['Sector'],
                    'group': row['Group Name'],
                    'gin': row['Group Identification Number (GIN)'],
                })

            logger.info(f"Loaded {len(companies)} companies from Excel")
            return self._companies_to_mapping(companies)

        except Exception as e:
            logger.error(f"Failed to load Excel file: {e}")
            return None

    def _company_to_ticker(self, company_name: str) -> str:
        """
        Convert company name to ticker symbol.

        Args:
            company_name: Full company name.

        Returns:
            Ticker symbol.
        """
        import re

        # Direct mappings for known companies
        ticker_map = {
            'Reliance Industries Limited': 'RELIANCE',
            'Tata Consultancy Services Limited': 'TCS',
            'HDFC Bank Limited': 'HDFCBANK',
            'ICICI Bank Limited': 'ICICIBANK',
            'Infosys Limited': 'INFY',
            'State Bank of India': 'SBIN',
            'Bajaj Finance Limited': 'BAJFINANCE',
            'Larsen and Toubro Limited': 'LT',
        }

        name = company_name.strip()
        if name in ticker_map:
            return ticker_map[name]

        # Generate ticker from name
        clean_name = re.sub(r'[^A-Z0-9]', '', name.upper())
        for suffix in ['LIMITED', 'LTD', 'PVT', 'PRIVATE', 'CORPORATION', 'COMPANY']:
            clean_name = clean_name.replace(suffix, '')

        return clean_name[:15]

    def _companies_to_mapping(
        self,
        companies: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Convert company list to sector mapping dictionary.

        Args:
            companies: List of company dictionaries.

        Returns:
            Sector mapping dictionary.
        """
        mapping: Dict[str, Dict[str, Any]] = {}

        for company in companies:
            ticker = company.get('symbol', '')
            if not ticker:
                continue

            mapping[ticker] = {
                'sector': company.get('sector', 'Unknown'),
                'industry': company.get('sector', 'Unknown'),
                'group': company.get('group', 'Unknown'),
                'gin': company.get('gin', 'Unknown'),
                'company_name': company.get('company_name', 'Unknown'),
            }

        return mapping

    def validate_mapping(
        self,
        mapping: Dict[str, Dict[str, Any]],
    ) -> Tuple[bool, List[str]]:
        """
        Validate sector mapping completeness.

        Args:
            mapping: Sector mapping dictionary to validate.

        Returns:
            Tuple of (is_valid, list of issues).
        """
        issues: List[str] = []

        # Check minimum tickers
        if len(mapping) < 100:
            issues.append(f"Low ticker count: {len(mapping)} (expected > 100)")

        # Check required fields
        required_fields = ['sector', 'industry', 'group', 'gin', 'company_name']
        for ticker, data in mapping.items():
            for field in required_fields:
                if field not in data:
                    issues.append(f"Ticker {ticker}: Missing field '{field}'")

        # Check for unknown values
        unknown_count = sum(
            1 for data in mapping.values()
            if data.get('sector') == 'Unknown'
        )
        if unknown_count > len(mapping) * 0.1:
            issues.append(f"High unknown sector count: {unknown_count}/{len(mapping)}")

        is_valid = len(issues) == 0

        if is_valid:
            logger.info("Mapping validation passed")
        else:
            logger.warning(f"Mapping validation failed with {len(issues)} issues")
            for issue in issues[:5]:
                logger.warning(f"  - {issue}")

        return is_valid, issues

    def save_mapping(self, mapping: Dict[str, Dict[str, Any]]) -> None:
        """
        Save sector mapping to JSON file.

        Args:
            mapping: Sector mapping dictionary.
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved mapping to {self.data_path}")

    def compare_mappings(
        self,
        old_mapping: Dict[str, Dict[str, Any]],
        new_mapping: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Compare old and new mappings to identify changes.

        Args:
            old_mapping: Previous sector mapping.
            new_mapping: Updated sector mapping.

        Returns:
            Dictionary with change statistics.
        """
        old_tickers = set(old_mapping.keys())
        new_tickers = set(new_mapping.keys())

        added = new_tickers - old_tickers
        removed = old_tickers - new_tickers
        common = old_tickers & new_tickers

        # Check for data changes in common tickers
        changed_data = []
        for ticker in common:
            if old_mapping[ticker] != new_mapping[ticker]:
                changed_data.append(ticker)

        return {
            'added': len(added),
            'removed': len(removed),
            'changed_data': len(changed_data),
            'total_old': len(old_mapping),
            'total_new': len(new_mapping),
            'added_tickers': list(added)[:10],  # Sample
            'removed_tickers': list(removed)[:10],
        }

    def run_update(
        self,
        backup: bool = True,
        validate: bool = True,
        force: bool = False,
    ) -> bool:
        """
        Run complete update process.

        Args:
            backup: Whether to create backup of old mapping.
            validate: Whether to validate new mapping.
            force: Whether to force update even if validation fails.

        Returns:
            True if update successful, False otherwise.

        Example:
            >>> updater = SectorMapUpdater()
            >>> success = updater.run_update(backup=True, validate=True)
            >>> if success:
            ...     print("Update completed successfully")
        """
        logger.info("=" * 60)
        logger.info("Starting AION SectorMap Update")
        logger.info("=" * 60)

        self.stats['start_time'] = datetime.now().isoformat()

        # Load current mapping
        try:
            old_mapping = self.load_current_mapping()
            logger.info(f"Loaded current mapping: {len(old_mapping)} tickers")
        except FileNotFoundError:
            old_mapping = {}
            logger.info("No existing mapping found")

        # Create backup
        if backup and old_mapping:
            self.create_backup()

        # Fetch new data
        if self.source == 'nse':
            new_mapping = self.fetch_from_nse()
        else:
            new_mapping = self.fetch_from_local()

        if new_mapping is None:
            logger.error("Failed to fetch new data")
            self.stats['success'] = False
            return False

        # Validate
        if validate:
            is_valid, issues = self.validate_mapping(new_mapping)
            if not is_valid and not force:
                logger.error("Validation failed. Use --force to override.")
                self.stats['success'] = False
                self.stats['validation_issues'] = issues
                return False

        # Compare
        if old_mapping:
            changes = self.compare_mappings(old_mapping, new_mapping)
            logger.info(f"Changes: +{changes['added']} -{changes['removed']} ~{changes['changed_data']}")
            self.stats['changes'] = changes

        # Save
        self.save_mapping(new_mapping)

        self.stats['end_time'] = datetime.now().isoformat()
        self.stats['success'] = True
        self.stats['total_tickers'] = len(new_mapping)

        logger.info("=" * 60)
        logger.info("Update completed successfully")
        logger.info(f"Total tickers: {len(new_mapping)}")
        logger.info("=" * 60)

        return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Get update statistics.

        Returns:
            Dictionary with update statistics.
        """
        return self.stats


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update AION SectorMap database from NSE data sources"
    )

    parser.add_argument(
        '--source',
        type=str,
        choices=['nse', 'local'],
        default='local',
        help='Data source to use (default: local)'
    )

    parser.add_argument(
        '--backup',
        action='store_true',
        default=True,
        help='Create backup of old mapping (default: True)'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        default=True,
        help='Validate new mapping (default: True)'
    )

    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force update even if validation fails'
    )

    parser.add_argument(
        '--data-path',
        type=str,
        help='Path to sector_map.json file'
    )

    parser.add_argument(
        '--excel-path',
        type=str,
        help='Path to Excel file (for local source)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create updater
    updater = SectorMapUpdater(
        data_path=args.data_path,
        source=args.source,
    )

    # Run update
    success = updater.run_update(
        backup=not args.no_backup,
        validate=not args.no_validate,
        force=args.force,
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
