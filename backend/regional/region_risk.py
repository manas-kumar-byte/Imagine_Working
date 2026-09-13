"""Module C — Regional risk aggregation.
Owner: Forecasting Engineer (or shared with Recommendation Engineer)
"""
from typing import TypedDict

from backend.config import VALID_STATUSES, VALID_TRENDS
from backend.db import store
from backend.forecasting.stock_status import classify_stock_status


class RegionRisk(TypedDict):
    facilities_at_risk: int
    total_facilities: int
    pct_at_risk: float
    regional_risk_score: float  # Simply arithmetic mean of all risk scores
    trend_direction: str   # one of VALID_TRENDS


def aggregate_region_risk(region_id: str, medicine_id: str) -> RegionRisk:

    total_facilities = store.get_facilities()
    previous_regional_risk_score = store.get_stockout_details()[store.get_stockout_details()["region_id"] == region_id].iloc[0]["risk_score"]

    facilities_in_region = total_facilities.loc[
        total_facilities["region_id"] == region_id
    ]["id"]

    facilities_at_risk: list[str] = []
    regional_risk_score = 0.0

    # Find all facilities as risk (watch or greater) and all risk scores

    for facility in facilities_in_region:
        stock_status = classify_stock_status(
            facility_id=facility,
            medicine_id=medicine_id
        )

        if stock_status["status"] == VALID_STATUSES[0]:
            continue

        elif stock_status["status"] in (VALID_STATUSES[1], VALID_STATUSES[2], VALID_STATUSES[3]):  # Watch, Critical, or Stockout
            facilities_at_risk.append(facility)
            regional_risk_score += float(stock_status["risk_score"])

    num_risky_facilities = len(facilities_at_risk)
    num_total_facilities = len(facilities_in_region)

    if num_total_facilities == 0:
        pct_at_risk = 0.0
        regional_risk_score = 0.0
    else:
        pct_at_risk = num_risky_facilities / num_total_facilities
        regional_risk_score = regional_risk_score / num_total_facilities

    risk_score_difference = regional_risk_score - previous_regional_risk_score

    if abs(risk_score_difference) <= 0.1:  # Difference close to 0
        trend_direction = VALID_TRENDS[1]

    elif risk_score_difference < -0.1:  # Risk score is falling
        trend_direction = VALID_TRENDS[2]

    else:  # Risk score is rising
        trend_direction = VALID_TRENDS[0]

    return RegionRisk(
        facilities_at_risk=num_risky_facilities,
        total_facilities=num_total_facilities,
        pct_at_risk=pct_at_risk,
        regional_risk_score=regional_risk_score,
        trend_direction=trend_direction
    )