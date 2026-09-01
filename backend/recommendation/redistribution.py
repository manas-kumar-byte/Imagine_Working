"""Module D — Redistribution recommendation.
Owner: Recommendation Engineer
"""
from typing import List, TypedDict


class RedistributionRecommendation(TypedDict):
    source_facility_id: str
    quantity: float
    distance_km: float
    urgency_score: float      # 0.0-1.0
    feasibility_score: float  # 0.0-1.0


def recommend_redistribution(deficit_facility_id: str, medicine_id: str) -> List[RedistributionRecommendation]:
    """Ranked list, highest priority first.

    urgency_score should weigh: recipient's days_remaining, distance, and the
    SOURCE facility's own risk trend (never recommend draining a facility
    that is itself about to need that stock).

    feasibility_score can incorporate cold-chain requirements, road access,
    and minimum shipment quantities for bonus "innovation" points.
    """
    raise NotImplementedError
