"""GET /regions/{id}/risk?medicine_id=
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

from backend.regional.region_risk import aggregate_region_risk

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("/{region_id}/risk")
def region_risk(region_id: str, medicine_id: str):
    return aggregate_region_risk(region_id=region_id,medicine_id=medicine_id)
