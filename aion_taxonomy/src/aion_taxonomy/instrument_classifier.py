# aion_taxonomy/src/aion_taxonomy/instrument_classifier.py

import json
import os

# Load sector map from aion-sectormap package
_SECTOR_MAP_PATH = os.path.join(
    os.path.dirname(__file__),
    '../../../aion-sectormap/src/aion_sectormap/data/sector_map.json'
)
_SECTOR_MAP = {}
if os.path.exists(_SECTOR_MAP_PATH):
    with open(_SECTOR_MAP_PATH, 'r') as f:
        _SECTOR_MAP = json.load(f)

# Load dynamic sensitivities (rolling correlations)
_SENSITIVITIES_PATH = os.path.join(os.path.dirname(__file__), 'data', 'sector_sensitivities.json')
_SECTOR_SENSITIVITIES = {}
if os.path.exists(_SENSITIVITIES_PATH):
    with open(_SENSITIVITIES_PATH, 'r') as f:
        _SECTOR_SENSITIVITIES = json.load(f)

def classify_instrument(tradingsymbol, segment, exchange, underlying=None):
    """
    Returns a dict with asset_class, asset_subclass, underlying_symbol, sector.
    Now handles:
      - Equity spot (EQ) with sector lookup from sector_map.json
      - Index derivative (NFO-/BFO-)
      - Commodity (MCX-/NCO-)
      - Currency derivative (CDS-)
      - Bond / Government security (BOND, G-SEC)
    """
    result = {
        "asset_class": None,
        "asset_subclass": None,
        "underlying": underlying,
        "sector": None
    }

    # 1. Equity spot
    if segment == 'EQ' and exchange in ['NSE', 'BSE']:
        result["asset_class"] = "equity"
        result["asset_subclass"] = "spot"
        ticker = tradingsymbol.upper()
        if ticker in _SECTOR_MAP:
            result["sector"] = _SECTOR_MAP[ticker].get("sector", "Unknown Equity")
        else:
            result["sector"] = "Unknown Equity"
        return result

    # 2. Index derivative
    if segment.startswith('NFO-') or segment.startswith('BFO-'):
        result["asset_class"] = "derivative"
        result["asset_subclass"] = "index_option" if 'OPT' in segment else "index_future"
        result["sector"] = "Financial Services -> Index Derivatives"
        return result

    # 3. Commodity (MCX or NCO segments)
    if segment.startswith('MCX-') or segment.startswith('NCO-'):
        result["asset_class"] = "commodity"
        sym = (underlying or tradingsymbol).upper()
        if 'GOLD' in sym or 'SILVER' in sym or 'GOLDM' in sym or 'SILVERM' in sym:
            result["asset_subclass"] = "precious_metal"
        elif 'CRUDE' in sym or 'NATURALGAS' in sym:
            result["asset_subclass"] = "energy"
        elif 'COPPER' in sym or 'ZINC' in sym or 'ALUMINI' in sym:
            result["asset_subclass"] = "base_metal"
        else:
            result["asset_subclass"] = "other_commodity"
        result["sector"] = f"Commodities -> {result['asset_subclass'].replace('_', ' ').title()}"
        return result

    # 4. Currency derivative (CDS segment)
    if segment.startswith('CDS-'):
        result["asset_class"] = "currency"
        result["asset_subclass"] = "derivative"
        result["sector"] = "Financial Services -> Currency Derivatives"
        return result

    # 5. Bond / Government security
    if segment in ['BOND', 'G-SEC'] or 'GSEC' in segment.upper() or 'GOVT' in segment.upper():
        result["asset_class"] = "fixed_income"
        result["asset_subclass"] = "government_security"
        result["sector"] = "Fixed Income -> Government Bonds"
        return result

    # 6. Unknown fallback
    return result

# Load static meta-factor sensitivities (fallback)
_META_PATH = os.path.join(os.path.dirname(__file__), 'data', 'meta_factor_sensitivities.json')
_META_SENSITIVITIES = {}
if os.path.exists(_META_PATH):
    with open(_META_PATH, 'r') as f:
        _META_SENSITIVITIES = json.load(f)

def get_meta_factors(instrument_info):
    """
    Given an instrument_info dict (output of classify_instrument), return a dict of meta-factor sensitivities.
    For equity spot, uses dynamic sensitivities from sector_sensitivities.json if available.
    Otherwise falls back to static mappings.
    """
    asset_class = instrument_info.get('asset_class')
    subclass = instrument_info.get('asset_subclass')
    sector = instrument_info.get('sector')

    # Special handling for equity spot: use dynamic sensitivities if sector exists in rolling correlations
    if asset_class == 'equity' and subclass == 'spot' and sector and sector != 'Unknown Equity':
        # Map sector name to the NIFTY sector index key used in sector_sensitivities.json
        # We need a mapping from the sector string (e.g., "Oil, Gas & Consumable Fuels") to the NIFTY index name (e.g., "NIFTYENERGY")
        sector_to_index = {
            "Oil, Gas & Consumable Fuels": "NIFTYENERGY",
            "Financial Services": "NIFTYBANK",
            "Automobile and Auto Components": "NIFTYAUTO",
            "Fast Moving Consumer Goods": "NIFTYFMCG",
            "Information Technology": "NIFTYIT",
            "IT": "NIFTYIT",
            "Pharmaceuticals": "NIFTYPHARMA",
            "Metals & Mining": "NIFTYMETAL",
            "Realty": "NIFTYREALTY",
            "Construction": "NIFTYINFRA",
            "Media": "NIFTYMEDIA",
            "Power": "NIFTYENERGY",
            "Healthcare": "NIFTYPHARMA",
            "Consumer Durables": "NIFTYCONDUR",
            "Telecommunications": "NIFTYMNC",
            "FMCG": "NIFTYFMCG",
            "Automobiles & Components": "NIFTYAUTO",
            "Banks": "NIFTYBANK",
            "Energy": "NIFTYENERGY",
        }
        index_key = sector_to_index.get(sector)
        if index_key and index_key in _SECTOR_SENSITIVITIES:
            # Return the dynamic sensitivities (already includes interest_rate, crude_oil, rupee, risk_sentiment)
            # Note: liquidity is missing; we'll set to 0 for now
            dyn = _SECTOR_SENSITIVITIES[index_key]
            return {
                "interest_rate": dyn.get("interest_rate", 0.0),
                "crude_oil": dyn.get("crude_oil", 0.0),
                "rupee": dyn.get("rupee", 0.0),
                "risk_sentiment": dyn.get("risk_sentiment", 0.0),
                "liquidity": 0.0   # not yet available
            }

    # Fallback to static sensitivities
    if asset_class and subclass:
        key = f"{asset_class}_{subclass}"
        if key in _META_SENSITIVITIES:
            return _META_SENSITIVITIES[key].copy()

    # Default for equity spot
    if asset_class == 'equity' and subclass == 'spot':
        return _META_SENSITIVITIES.get('equity_spot_default', {}).copy()

    # Zero vector if nothing matches
    return {
        "interest_rate": 0.0,
        "crude_oil": 0.0,
        "rupee": 0.0,
        "risk_sentiment": 0.0,
        "liquidity": 0.0
    }
