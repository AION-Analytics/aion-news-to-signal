# =============================================================================
# AION Open-Source Project: AION SectorMap
# File: __init__.py
# Description: NSE Ticker to Sector/Industry Mapping Package
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
AION SectorMap - NSE Ticker to Sector/Industry Mapping.

This package provides comprehensive mapping of NSE (National Stock Exchange of India)
ticker symbols to their corresponding sectors, industries, business groups, and
Group Identification Numbers (GIN).

Features:
    - Map 591+ NSE listed companies to sectors and industries
    - Business group identification with GIN codes
    - Pandas DataFrame integration for batch processing
    - Reverse lookups (sector → tickers)
    - Graceful handling of unknown tickers

Example:
    >>> from aion_sectormap import SectorMapper
    >>> mapper = SectorMapper()
    >>> mapper.get_sector('RELIANCE')
    'Oil, Gas & Consumable Fuels'
    >>> mapper.get_industry('TCS')
    'Software & Services'
    >>> mapper.get_group('HDFCBANK')
    'HDFC Bank Limited'

Classes:
    SectorMapper: Main class for sector/company/group mappings.

Data:
    The package includes a comprehensive JSON database with mappings for all
    NSE listed companies sourced from official NSE group companies data.
"""

from typing import List

from .mapper import SectorMapper

__version__ = "0.1.0"
__author__ = "AION Contributors"
__license__ = "Apache-2.0"

__all__: List[str] = [
    "SectorMapper",
    "__version__",
]
