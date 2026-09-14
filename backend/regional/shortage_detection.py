"""Module C — Emerging regional shortage detection.
Owner: Forecasting Engineer

This is the module that answers the core problem statement: how does one
empty shelf become a regional shortage? A shortage is "emerging" when
individual facility risk_scores are rising together across a connected
cluster (shared distributor or geographic proximity) — not just one
isolated facility having a bad week.
"""

from datetime import datetime, timezone
from typing import TypedDict

from backend.config import STATUS_THRESHOLDS
from backend.db import store
from backend.regional.propagation_score import shortage_propagation_score
from backend.regional.region_risk import aggregate_region_risk


class EmergingShortage(TypedDict):
    region_id: str
    regional_risk_score: float
    spread_rate: float          # how fast pct_at_risk is climbing, e.g. per day
    first_detected_at: str      # ISO 8601


def detect_emerging_shortage(
    medicine_id: str | None = None
) -> list[EmergingShortage]:

    """Scans all regions for the given medicine and flags ones showing a
    rising, clustered risk pattern. Sorted by regional_risk_score descending.
    """

    facilities = store.get_facilities()
    medicines = store.get_medicines()

    if medicine_id is None:

        medicine_ids = [
            str(value)
            for value in medicines["id"]
        ]

    else:
        medicine_ids = [medicine_id]

    region_ids = [
        str(value)
        for value in facilities["region_id"].dropna().unique()
    ]

    results: list[EmergingShortage] = []

    detected_at = datetime.now(
        timezone.utc
    ).isoformat()

    for med_id in medicine_ids:
        for region_id in region_ids:
            risk = aggregate_region_risk(
                region_id=region_id,
                medicine_id=med_id
            )
            propagation = shortage_propagation_score(
                region_id=region_id,
                medicine_id=med_id
            )
            if (
                risk["regional_risk_score"]
                >= STATUS_THRESHOLDS["watch"]
                or propagation["score"]
                >= STATUS_THRESHOLDS["watch"]
            ):

                results.append({
                    "region_id": region_id,
                    "regional_risk_score": float(
                        risk["regional_risk_score"]
                    ),
                    "spread_rate": float(
                        propagation["score"]
                    ),
                    "first_detected_at": detected_at
                })
    results.sort(
        key=lambda item: item["regional_risk_score"],
        reverse=True
    )

    return results

detect_emerging_shortage()
