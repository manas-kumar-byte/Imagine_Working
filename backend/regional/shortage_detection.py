"""Module C — Emerging regional shortage detection.
Owner: Forecasting Engineer

This is the module that answers the core problem statement: how does one
empty shelf become a regional shortage? A shortage is "emerging" when
individual facility risk_scores are rising together across a connected
cluster (shared distributor or geographic proximity) — not just one
isolated facility having a bad week.
"""
from typing import List, TypedDict


class EmergingShortage(TypedDict):
    region_id: str
    regional_risk_score: float
    spread_rate: float          # how fast pct_at_risk is climbing, e.g. per day
    first_detected_at: str      # ISO 8601


def detect_emerging_shortage(medicine_id: str | None = None) -> List[EmergingShortage]:
    """Scans all regions for the given medicine and flags ones showing a
    rising, clustered risk pattern. Sorted by regional_risk_score descending.
    """
    raise NotImplementedError
#In this make it medicine_id = None then it returns for all medicines