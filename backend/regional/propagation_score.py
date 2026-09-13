"""Module C — Shortage propagation / contagion score.
Owner: Forecasting Engineer
"""

import math
from typing import TypedDict

from backend.db import store
from backend.forecasting.stock_status import classify_stock_status


class PropagationScore(TypedDict):
    score: float                    # 0.0-1.0, likelihood of spreading to neighbors
    contributing_factors: list[str]  # human-readable, e.g. ["shared distributor X", "3 adjacent facilities trending up"]


NEIGHBOR_RADIUS_KM = 100.0


def _haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:

    radius = 6371.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = math.radians(
        lat2 - lat1
    )

    dlon = math.radians(
        math.radians(lon2)
        - math.radians(lon1)
    )

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * radius * math.asin(
        math.sqrt(a)
    )


def shortage_propagation_score(
    region_id: str,
    medicine_id: str
) -> PropagationScore:

    """Simple defensible approach: treat facilities as nodes in a graph
    (edges = shared distributor OR geographic proximity within radius_km);
    score rises with number of at-risk neighbors and shared-supplier overlap.
    """

    facilities = store.get_facilities()

    region_facilities = facilities[
        facilities["region_id"] == region_id
    ]

    if region_facilities.empty:
        return {
            "score": 0.0,
            "contributing_factors": []
        }

    risk_scores = {}

    for _, facility in region_facilities.iterrows():

        status = classify_stock_status(
            facility_id=str(facility["id"]),
            medicine_id=medicine_id
        )

        risk_scores[str(facility["id"])] = float(
            status["risk_score"]
        )

    total_nodes = len(
        region_facilities
    )

    at_risk_nodes = sum(
        1
        for score in risk_scores.values()
        if score >= 0.5
    )

    regional_risk = (
        sum(risk_scores.values())
        / total_nodes
    )

    connected_at_risk_pairs = 0
    total_pairs = 0

    rows = list(
        region_facilities.iterrows()
    )

    for i in range(len(rows)):

        _, first = rows[i]

        for j in range(i + 1, len(rows)):

            _, second = rows[j]

            distance = _haversine_km(
                float(first["lat"]),
                float(first["lon"]),
                float(second["lat"]),
                float(second["lon"])
            )

            if distance <= NEIGHBOR_RADIUS_KM:

                total_pairs += 1

                first_risk = risk_scores[
                    str(first["id"])
                ]

                second_risk = risk_scores[
                    str(second["id"])
                ]

                if (
                    first_risk >= 0.5
                    and second_risk >= 0.5
                ):
                    connected_at_risk_pairs += 1

    if total_pairs > 0:
        neighbor_spread = (
            connected_at_risk_pairs
            / total_pairs
        )
    else:
        neighbor_spread = 0.0

    at_risk_fraction = (
        at_risk_nodes
        / total_nodes
    )

    score = (
        0.4 * regional_risk
        + 0.35 * at_risk_fraction
        + 0.25 * neighbor_spread
    )

    score = max(
        0.0,
        min(1.0, float(score))
    )

    factors: list[str] = []

    if at_risk_nodes > 0:
        factors.append(
            f"{at_risk_nodes} of {total_nodes} facilities are at risk"
        )

    if neighbor_spread > 0:
        factors.append(
            "multiple geographically connected facilities are at risk"
        )

    if regional_risk >= 0.5:
        factors.append(
            "regional risk score is elevated"
        )

    return {
        "score": round(score, 3),
        "contributing_factors": factors
    }