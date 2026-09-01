"""Module D — Higher-level intervention recommendation (beyond redistribution).
Owner: Recommendation Engineer
"""
from typing import TypedDict
from backend.config import VALID_ACTIONS, VALID_PRIORITIES


class InterventionRecommendation(TypedDict):
    action: str      # one of VALID_ACTIONS
    priority: str    # one of VALID_PRIORITIES
    rationale: str


def recommend_intervention(region_id: str, medicine_id: str) -> InterventionRecommendation:
    """Decides between redistribute / expedite_order / emergency_procurement /
    monitor based on aggregate_region_risk() and shortage_propagation_score()
    outputs from Module C.
    """
    raise NotImplementedError
