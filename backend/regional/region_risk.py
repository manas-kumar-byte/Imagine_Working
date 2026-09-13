"""Module C — Regional risk aggregation.
Owner: Forecasting Engineer (or shared with Recommendation Engineer)
"""

from typing import TypedDict

from backend.config import VALID_STATUSES, VALID_TRENDS
from backend.db import store
from backend.forecasting import consumption_rate
from backend.forecasting.stock_status import classify_stock_status


class RegionRisk(TypedDict):
    facilities_at_risk: int
    total_facilities: int
    pct_at_risk: float
    regional_risk_score: float  # Simply arithmetic mean of all risk scores
    trend_direction: str   # one of VALID_TRENDS


def aggregate_region_risk(
    region_id: str,
    medicine_id: str
) -> RegionRisk:

    """Rolls up classify_stock_status() results across all facilities in the
    region for the given medicine.
    """

    total_facilities = store.get_facilities()

    facilities_in_region = total_facilities.loc[
        total_facilities["region_id"] == region_id
    ]["id"]

    facilities_at_risk: list[str] = []
    risk_scores: list[float] = []
    trend_values: list[float] = []

    # Find all facilities as risk (watch or greater) and all risk scores

    for facility in facilities_in_region:

        stock_status = classify_stock_status(
            facility_id=facility,
            medicine_id=medicine_id
        )

        risk_score = float(
            stock_status["risk_score"]
        )

        risk_scores.append(risk_score)

        if stock_status["status"] == VALID_STATUSES[0]:
            continue

        elif stock_status["status"] in (VALID_STATUSES[1], VALID_STATUSES[2]) or stock_status["status"] != VALID_STATUSES[0]:
            facilities_at_risk.append(facility)

        rate = consumption_rate.compute_consumption_rate(
            facility_id=facility,
            medicine_id=medicine_id,
            window_days=7
        )

        trend_values.append(
            float(rate["trend_pct"])
        )

    num_risky_facilities = len(facilities_at_risk)
    num_total_facilities = len(facilities_in_region)

    if num_total_facilities == 0:
        pct_at_risk = 0.0
        regional_risk_score = 0.0
        trend_direction = VALID_TRENDS[1]

    else:
        pct_at_risk = (
            num_risky_facilities / num_total_facilities
        )

        regional_risk_score = (
            sum(risk_scores) / num_total_facilities
        )

        if trend_values:
            average_trend = (
                sum(trend_values) / len(trend_values)
            )
        else:
            average_trend = 0.0

        if abs(average_trend) <= 0.1:   # Difference close to 0
            trend_direction = VALID_TRENDS[1]

        elif average_trend < -0.1:      # Risk score is falling
            trend_direction = VALID_TRENDS[2]

        else:       # Risk score is rising
            trend_direction = VALID_TRENDS[0]

    return RegionRisk(
        facilities_at_risk=num_risky_facilities,
        total_facilities=num_total_facilities,
        pct_at_risk=float(pct_at_risk),
        regional_risk_score=float(regional_risk_score),
        trend_direction=trend_direction
    )