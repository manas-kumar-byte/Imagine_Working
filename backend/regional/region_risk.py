"""Module C — Regional risk aggregation.
Owner: Forecasting Engineer (or shared with Recommendation Engineer)
"""
from typing import TypedDict
from backend.config import VALID_TRENDS


class RegionRisk(TypedDict):
    facilities_at_risk: int
    total_facilities: int
    pct_at_risk: float
    regional_risk_score: float
    trend_direction: str   # one of VALID_TRENDS


def aggregate_region_risk(region_id: str, medicine_id: str) -> RegionRisk:
    """Rolls up classify_stock_status() results across all facilities in the
    region for the given medicine.
    """
    raise NotImplementedError
