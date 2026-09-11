"""GET /recommendations/{facility_id}?medicine_id=
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

from backend.explainability.explain import explain_recommendation
from 
router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{facility_id}")
def recommendations(facility_id: str, medicine_id: str) -> R:
    raise NotImplementedError
