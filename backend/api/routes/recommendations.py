"""GET /recommendations/{facility_id}?medicine_id=
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

from backend.api.schemas import RecommendationResponse
from backend.explainability.explain import explain_recommendation
from backend.recommendation.redistribution import recommend_redistribution

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{facility_id}")
def recommendations(facility_id: str, medicine_id: str) -> list[RecommendationResponse]:
    recommendations = recommend_redistribution(
        facility_id,
        medicine_id
    )

    return [
        RecommendationResponse(
            source_facility_id=rec["source_facility_id"],
            quantity=round(rec["quantity"]),
            distance_km=rec["distance_km"],
            urgency_score=rec["urgency_score"],
            feasibility_score=rec["feasibility_score"],
            rationale=explain_recommendation(dict(rec))
        )
        for rec in recommendations
    ]