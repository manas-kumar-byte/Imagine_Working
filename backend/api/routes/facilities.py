"""GET /facilities, GET /facilities/{id}/status?medicine_id=
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

router = APIRouter(prefix="/facilities", tags=["facilities"])


@router.get("")
def list_facilities():
    raise NotImplementedError


@router.get("/{facility_id}/status")
def facility_status(facility_id: str, medicine_id: str):
    raise NotImplementedError
