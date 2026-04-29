# AION SectorMap

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**AION SectorMap** is a comprehensive Python package for mapping National Stock Exchange of India (NSE) ticker symbols to their corresponding sectors, industries, business groups, and Group Identification Numbers (GIN).

Part of the **AION** open-source ecosystem for financial data processing and analysis.

## Features

-  **Comprehensive Coverage**: 591+ NSE listed companies mapped to 44 sectors and 340+ business groups
- 🔍 **Multiple Lookup Methods**: Forward (ticker → sector) and reverse (sector → tickers) lookups
-  **Pandas Integration**: Batch process DataFrames with sector/industry/group columns
-  **Accurate Data**: Sourced from official NSE group companies data (updated January 2026)
-  **Fast Lookups**: Optimized dictionary-based lookups for high-performance applications
- 🛡️ **Error Handling**: Graceful handling of unknown tickers with configurable defaults

## Installation

### From PyPI (recommended)

```bash
pip install aion-sectormap
```

### From Source

```bash
git clone https://github.com/aion/aion-sectormap.git
cd aion-sectormap
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from aion_sectormap import SectorMapper

# Initialize the mapper
mapper = SectorMapper()

# Get sector for a ticker
sector = mapper.get_sector('RELIANCE')
print(sector)  # Output: Oil, Gas & Consumable Fuels

# Get industry for a ticker
industry = mapper.get_industry('TCS')
print(industry)  # Output: Software & Services

# Get business group for a ticker
group = mapper.get_group('HDFCBANK')
print(group)  # Output: HDFC Bank Limited

# Get all tickers in a sector
financial_tickers = mapper.get_tickers_in_sector('Financial Services')
print(f"Financial Services has {len(financial_tickers)} companies")

# Batch process a DataFrame
import pandas as pd

df = pd.DataFrame({
    'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY'],
    'price': [2500.0, 3500.0, 1600.0, 1400.0]
})

# Add sector, industry, and group columns
df_mapped = mapper.map(df)
print(df_mapped)
```

## Usage Examples

### Basic Lookups

```python
from aion_sectormap import SectorMapper

mapper = SectorMapper()

# Get sector
mapper.get_sector('RELIANCE')  # 'Oil, Gas & Consumable Fuels'

# Get industry
mapper.get_industry('TCS')  # 'Software & Services'

# Get business group
mapper.get_group('HDFCBANK')  # 'HDFC Bank Limited'

# Get GIN (Group Identification Number)
mapper.get_gin('RELIANCE')  # 'MUKESHAMBANI-01'

# Get full company name
mapper.get_company_name('TCS')  # 'Tata Consultancy Services Limited'

# Handle unknown tickers
mapper.get_sector('INVALID')  # 'Unknown'
mapper.get_sector('INVALID', default='N/A')  # 'N/A'
```

### Reverse Lookups

```python
# Get all tickers in a sector
financial_tickers = mapper.get_tickers_in_sector('Financial Services')
print(f"Found {len(financial_tickers)} financial services companies")

# Get all tickers in an industry
it_tickers = mapper.get_tickers_in_industry('Software & Services')

# Get all tickers in a business group
ambani_group = mapper.get_tickers_in_group('Mukesh Ambani Group')

# Get all sectors
all_sectors = mapper.get_all_sectors()
print(f"Total sectors: {len(all_sectors)}")

# Get all business groups
all_groups = mapper.get_all_groups()
print(f"Total groups: {len(all_groups)}")
```

### DataFrame Mapping

```python
import pandas as pd
from aion_sectormap import SectorMapper

mapper = SectorMapper()

# Sample portfolio
portfolio = pd.DataFrame({
    'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR'],
    'quantity': [100, 50, 200, 100, 75],
    'avg_price': [2400, 3400, 1500, 1350, 2500]
})

# Add sector and industry columns
portfolio = mapper.map(portfolio)

# Add GIN and company name
portfolio = mapper.map(
    portfolio,
    add_gin=True,
    add_company_name=True
)

# Custom fill value for unknown tickers
portfolio = mapper.map(portfolio, fill_value='N/A')
```

### Search and Statistics

```python
# Search for companies by name
hdfc_companies = mapper.search_ticker('HDFC')
print(hdfc_companies)

# Get sector summary
sector_summary = mapper.get_sector_summary()
print(sector_summary.head(10))

# Get group summary
group_summary = mapper.get_group_summary()
print(group_summary.head(10))

# Get mapping statistics
stats = mapper.get_mapping_stats()
print(stats)
# Output: {
#   'total_tickers': 591,
#   'total_sectors': 44,
#   'total_industries': 44,
#   'total_groups': 340,
#   'total_gins': 340
# }
```

## API Reference

### SectorMapper Class

#### Initialization

```python
SectorMapper(data_path: Optional[str] = None)
```

- `data_path`: Path to sector_map.json file. Uses package default if not specified.

#### Lookup Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_sector(ticker, default='Unknown')` | Get sector for ticker | `str` |
| `get_industry(ticker, default='Unknown')` | Get industry for ticker | `str` |
| `get_group(ticker, default='Unknown')` | Get business group for ticker | `str` |
| `get_gin(ticker, default='Unknown')` | Get GIN for ticker | `str` |
| `get_company_name(ticker, default='Unknown')` | Get company name for ticker | `str` |

#### Reverse Lookup Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_tickers_in_sector(sector)` | Get all tickers in sector | `List[str]` |
| `get_tickers_in_industry(industry)` | Get all tickers in industry | `List[str]` |
| `get_tickers_in_group(group)` | Get all tickers in group | `List[str]` |
| `get_tickers_by_gin(gin)` | Get all tickers with GIN | `List[str]` |
| `get_all_sectors()` | Get list of all sectors | `List[str]` |
| `get_all_industries()` | Get list of all industries | `List[str]` |
| `get_all_groups()` | Get list of all groups | `List[str]` |
| `get_all_tickers()` | Get list of all tickers | `List[str]` |

#### DataFrame Methods

```python
map(
    df: pd.DataFrame,
    ticker_column: str = 'ticker',
    add_sector: bool = True,
    add_industry: bool = True,
    add_group: bool = True,
    add_gin: bool = False,
    add_company_name: bool = False,
    fill_value: str = 'Unknown'
) -> pd.DataFrame
```

#### Summary Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_sector_summary()` | Tickers per sector | `pd.DataFrame` |
| `get_group_summary()` | Tickers per group | `pd.DataFrame` |
| `get_mapping_stats()` | Database statistics | `Dict` |
| `search_ticker(query)` | Search by company name | `pd.DataFrame` |

#### Special Methods

```python
len(mapper)  # Number of tickers
ticker in mapper  # Check if ticker exists
repr(mapper)  # String representation
```

## Data Structure

The package includes a comprehensive JSON database (`sector_map.json`) with the following structure:

```json
{
  "RELIANCE": {
    "sector": "Oil, Gas & Consumable Fuels",
    "industry": "Oil, Gas & Consumable Fuels",
    "group": "Mukesh Ambani Group",
    "gin": "MUKESHAMBANI-01",
    "company_name": "Reliance Industries Limited"
  },
  "TCS": {
    "sector": "Software & Services",
    "industry": "Software & Services",
    "group": "Tata Sons",
    "gin": "TATASONS-01",
    "company_name": "Tata Consultancy Services Limited"
  }
}
```

### Sector Coverage

The database covers 44 sectors including:

- Financial Services (195+ companies)
- Non Banking Financial Company (42+ companies)
- Power (27+ companies)
- Capital Goods (26+ companies)
- Realty (23+ companies)
- Construction (21+ companies)
- Services (19+ companies)
- Utilities (19+ companies)
- Chemicals (17+ companies)
- Oil, Gas & Consumable Fuels (15+ companies)
- Banks (14+ companies)
- Fast Moving Consumer Goods (12+ companies)
- Automobile and Auto Components (12+ companies)
- And 30+ more sectors...

## Updating the Mapping

To update the sector mapping from local data sources:

```bash
python scripts/update_map.py --source local --backup --validate
```

Options:
- `--source`: Data source (`nse` or `local`)
- `--backup`: Create backup of old mapping (default: True)
- `--validate`: Validate new mapping (default: True)
- `--force`: Force update even if validation fails

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_mapper.py::TestSectorMapperLookups -v

# Run with coverage
pytest tests/ --cov=aion_sectormap --cov-report=html
```

## Project Structure

```
aion-sectormap/
├── src/aion_sectormap/
│   ├── __init__.py          # Package initialization
│   ├── mapper.py            # SectorMapper class
│   ├── data/
│   │   └── sector_map.json  # Ticker → sector mapping
│   └── py.typed             # PEP 561 marker
├── scripts/
│   └── update_map.py        # Update script
├── tests/
│   ├── __init__.py
│   └── test_mapper.py       # Unit tests
├── README.md                # This file
├── LICENSE                  # Apache 2.0 License
├── setup.py                 # Package configuration
├── pyproject.toml           # Modern Python packaging
├── requirements.txt         # Dependencies
└── example.py               # Usage examples
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write Google-style docstrings
- Include unit tests for new features
- Ensure all tests pass before submitting PR

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

```
Copyright 2026 AION Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## AION Attribution

This package is part of the **AION** open-source ecosystem. AION provides a comprehensive suite of tools for financial data processing, analysis, and algorithmic trading in the Indian markets.

- **GitHub**: [https://github.com/aion](https://github.com/aion)
- **Documentation**: [https://aion.readthedocs.io](https://aion.readthedocs.io)

## Related Projects

- **aion-sentiment**: Market sentiment analysis for Indian stocks
- **aion-data**: Historical and real-time market data
- **aion-connectors**: Broker and exchange connectors

## Support

For issues, questions, or contributions:
- **Issues**: [GitHub Issues](https://github.com/aion/aion-sectormap/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aion/aion-sectormap/discussions)

## Changelog

### Version 0.1.0 (2026-03-14)

- Initial release
- 591+ NSE companies mapped
- 44 sectors covered
- 340+ business groups
- Complete test coverage
- Pandas DataFrame integration
