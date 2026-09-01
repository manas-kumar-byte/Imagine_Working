"""GET /regions/{id}/risk?medicine_id=
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("/{region_id}/risk")
def region_risk(region_id: str, medicine_id: str):
    raise NotImplementedError
