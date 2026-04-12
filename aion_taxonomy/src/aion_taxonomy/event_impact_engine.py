# aion_taxonomy/src/aion_taxonomy/event_impact_engine.py

from .instrument_classifier import classify_instrument, get_meta_factors

# Pre-defined event impacts on the 5 meta-factors.
# Values range from -1 (strong negative) to +1 (strong positive).
EVENT_IMPACTS = {
    "RBI_RATE_HIKE": {
        "interest_rate": 0.6,
        "crude_oil": 0.0,
        "rupee": 0.2,
        "risk_sentiment": -0.3,
        "liquidity": -0.2
    },
    "RBI_RATE_CUT": {
        "interest_rate": -0.6,
        "crude_oil": 0.0,
        "rupee": -0.2,
        "risk_sentiment": 0.3,
        "liquidity": 0.2
    },
    "CRUDE_OIL_SPIKE": {
        "interest_rate": 0.2,   # inflation expectation
        "crude_oil": 1.0,
        "rupee": -0.5,
        "risk_sentiment": -0.4,
        "liquidity": -0.1
    },
    "RUPEE_DEPRECIATION": {
        "interest_rate": 0.1,
        "crude_oil": 0.3,
        "rupee": -0.8,
        "risk_sentiment": -0.2,
        "liquidity": 0.0
    },
    "GLOBAL_RISK_OFF": {
        "interest_rate": -0.2,
        "crude_oil": -0.3,
        "rupee": -0.4,
        "risk_sentiment": -0.9,
        "liquidity": -0.5
    }
}

def calculate_impact(event_name, instrument_info):
    """
    Calculate net impact of an event on a single instrument.
    Returns a float between -1 and +1 (positive = bullish, negative = bearish).
    """
    if event_name not in EVENT_IMPACTS:
        return 0.0
    event_vector = EVENT_IMPACTS[event_name]
    instrument_sensitivities = get_meta_factors(instrument_info)
    
    # Dot product
    impact = 0.0
    for factor in ["interest_rate", "crude_oil", "rupee", "risk_sentiment", "liquidity"]:
        impact += event_vector.get(factor, 0.0) * instrument_sensitivities.get(factor, 0.0)
    
    # Clamp to [-1, 1]
    return max(-1.0, min(1.0, impact))

def rank_instruments_by_impact(event_name, instrument_list):
    """
    Given a list of instrument descriptors (each is a dict with tradingsymbol, segment, exchange, underlying),
    return a list sorted by impact (most positive first).
    """
    results = []
    for inst in instrument_list:
        info = classify_instrument(
            inst["tradingsymbol"],
            inst["segment"],
            inst["exchange"],
            inst.get("underlying")
        )
        impact = calculate_impact(event_name, info)
        results.append({
            "instrument": inst["tradingsymbol"],
            "asset_class": info["asset_class"],
            "sector": info["sector"],
            "impact": impact
        })
    results.sort(key=lambda x: x["impact"], reverse=True)
    return results