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
from backend.db.store import get_facilities, get_medicines
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

    facilities = get_facilities()
    medicines = get_medicines()

    if medicine_id is None:
        medicine_ids = [
            str(med_id)
            for med_id in medicines["id"]
        ]
    else:
        medicine_ids = [medicine_id]

    results: list[EmergingShortage] = []

    region_ids = facilities["region_id"].dropna().unique()

    detected_at = datetime.now(
        timezone.utc
    ).isoformat()

    for med_id in medicine_ids:

        for region_id in region_ids:

            risk = aggregate_region_risk(
                region_id=str(region_id),
                medicine_id=med_id
            )

            if (
                risk["regional_risk_score"]
                >= STATUS_THRESHOLDS["watch"]
            ):

                results.append({
                    "region_id": str(region_id),
                    "regional_risk_score": float(
                        risk["regional_risk_score"]
                    ),
                    "spread_rate": float(
                        risk["pct_at_risk"]
                    ),
                    "first_detected_at": detected_at
                })

    results.sort(
        key=lambda result: result["regional_risk_score"],
        reverse=True
    )

    return results