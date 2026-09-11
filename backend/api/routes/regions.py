"""GET /regions/{id}/risk?medicine_id=
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

from backend.api.schemas import RegionRiskResponse

from backend.regional.region_risk import aggregate_region_risk

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("/{region_id}/risk")
def region_risk(region_id: str, medicine_id: str) -> RegionRiskResponse:
    risk = aggregate_region_risk(region_id=region_id,medicine_id=medicine_id)
    
    return RegionRiskResponse(
        region_id = region_id,
        medicine_id = medicine_id,
        facilities_at_risk = risk["facilities_at_risk"],
        total_facilities = risk["total_facilities"],
        pct_at_risk = risk["pct_at_risk"],
        regional_risk_score = risk["regional_risk_score"],
        trend_direction = risk["trend_direction"]
    )