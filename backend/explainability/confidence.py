"""Module E — Uncertainty communication.
Owner: Recommendation Engineer (or shared with Backend Lead)
"""
from typing import TypedDict
from backend.models.ConfidenceBand import ConfidenceBand
"""
class ConfidenceBand(TypedDict):
    level: str   # "low" | "medium" | "high"
    note: str    # e.g. "based on only 6 days of consumption history"
"""

def confidence_band(forecast_result: dict) -> ConfidenceBand:
    """Takes a StockoutForecast (or similar) dict and derives a confidence
    level + human-readable caveat, e.g. from window size or volatility.
    """
    
    
    days = forecast_result.get("days_remaining", 0)
    low = forecast_result.get("low_estimate", days)
    high = forecast_result.get("high_estimate", days)
    method = forecast_result.get("method", "unknown")

    if days <= 0:
        return {"level": "high", "note": "facility is already at or below reorder point"}

    band_width = high - low
    relative_spread = band_width / days if days else 1.0
    #judging confidence using a relative spread, if the bandwidth is smaller then
    #uncertainty is less, otherwise higher uncertainty.
    if relative_spread <= 0.3:
        level = "high"
        note = f"forecast band is tight ({low:.1f}-{high:.1f} days), based on {method}"
    elif relative_spread <= 0.6:
        level = "medium"
        note = f"moderate uncertainty ({low:.1f}-{high:.1f} days), based on {method}"
    else:
        level = "low"
        note = f"wide uncertainty band ({low:.1f}-{high:.1f} days) — treat as directional only, based on {method}"

    return {"level": level, "note": note}
