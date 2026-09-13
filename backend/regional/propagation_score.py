"""
Module C — Shortage propagation / contagion score.

Owner: Forecasting Engineer
"""

import math
from typing import TypedDict

from backend.db import store
from backend.forecasting.stock_status import classify_stock_status


class PropagationScore(TypedDict):
    score: float
    contributing_factors: list[str]


# Facilities within this distance are considered geographically connected.
NEIGHBOR_RADIUS_KM = 100.0

# Risk score at or above this is considered at-risk.
AT_RISK_THRESHOLD = 0.5


def _haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate distance between two latitude/longitude points in km.
    """

    earth_radius_km = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    # Protect against tiny floating-point errors.
    a = max(0.0, min(1.0, a))

    return 2 * earth_radius_km * math.asin(math.sqrt(a))


def shortage_propagation_score(
    region_id: str,
    medicine_id: str,
) -> PropagationScore:
    """
    Estimate how likely a shortage is to propagate through connected
    facilities in a region.

    The score combines:

    1. Overall regional risk.
    2. Fraction of facilities currently at risk.
    3. Fraction of geographically connected facility pairs that are
       simultaneously at risk.

    This is deliberately simple and explainable.
    """

    facilities = store.get_facilities()

    region_facilities = facilities[
        facilities["region_id"].astype(str) == str(region_id)
    ].copy()

    if region_facilities.empty:
        return {
            "score": 0.0,
            "contributing_factors": [],
        }

    # ---------------------------------------------------------------
    # Calculate facility-level risk.
    # ---------------------------------------------------------------

    risk_scores: dict[str, float] = {}

    for _, facility in region_facilities.iterrows():
        facility_id = str(facility["id"])

        stock_status = classify_stock_status(
            facility_id=facility_id,
            medicine_id=medicine_id,
        )

        risk_scores[facility_id] = float(
            stock_status["risk_score"]
        )

    total_nodes = len(region_facilities)

    # ---------------------------------------------------------------
    # Fraction of facilities currently at risk.
    # ---------------------------------------------------------------

    at_risk_nodes = sum(
        1
        for risk in risk_scores.values()
        if risk >= AT_RISK_THRESHOLD
    )

    at_risk_fraction = (
        at_risk_nodes / total_nodes
        if total_nodes > 0
        else 0.0
    )

    # ---------------------------------------------------------------
    # Overall regional risk.
    # ---------------------------------------------------------------

    regional_risk = (
        sum(risk_scores.values()) / total_nodes
        if total_nodes > 0
        else 0.0
    )

    # ---------------------------------------------------------------
    # Geographic connectivity.
    # ---------------------------------------------------------------

    rows = list(region_facilities.iterrows())

    connected_at_risk_pairs = 0
    total_connected_pairs = 0

    for i in range(len(rows)):
        _, first = rows[i]

        for j in range(i + 1, len(rows)):
            _, second = rows[j]

            distance = _haversine_km(
                float(first["lat"]),
                float(first["lon"]),
                float(second["lat"]),
                float(second["lon"]),
            )

            if distance > NEIGHBOR_RADIUS_KM:
                continue

            total_connected_pairs += 1

            first_id = str(first["id"])
            second_id = str(second["id"])

            first_risk = risk_scores[first_id]
            second_risk = risk_scores[second_id]

            if (
                first_risk >= AT_RISK_THRESHOLD
                and second_risk >= AT_RISK_THRESHOLD
            ):
                connected_at_risk_pairs += 1

    if total_connected_pairs > 0:
        neighbor_spread = (
            connected_at_risk_pairs
            / total_connected_pairs
        )
    else:
        neighbor_spread = 0.0

    # ---------------------------------------------------------------
    # Final propagation score.
    #
    # Regional risk          = 40%
    # At-risk facilities     = 35%
    # Connected risky pairs  = 25%
    # ---------------------------------------------------------------

    score = (
        0.40 * regional_risk
        + 0.35 * at_risk_fraction
        + 0.25 * neighbor_spread
    )

    score = max(
        0.0,
        min(1.0, float(score)),
    )

    # ---------------------------------------------------------------
    # Human-readable explanation factors.
    # ---------------------------------------------------------------

    factors: list[str] = []

    if at_risk_nodes > 0:
        factors.append(
            f"{at_risk_nodes} of {total_nodes} "
            "facilities are at risk"
        )

    if neighbor_spread > 0:
        factors.append(
            "multiple geographically connected "
            "facilities are at risk"
        )

    if regional_risk >= 0.5:
        factors.append(
            "regional risk score is elevated"
        )

    if not factors:
        factors.append(
            "no significant propagation pattern detected"
        )

    return {
        "score": round(score, 3),
        "contributing_factors": factors,
    }