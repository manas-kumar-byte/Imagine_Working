"""GET /facilities, GET /facilities/{id}/status?medicine_id=
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

from backend.db.store import get_medicines
from backend.models.medicine import Medicine

router = APIRouter(prefix="/medicines", tags=["medicines"])


@router.get("")
def list_medicines(medicine_id: str | None = None) -> list[Medicine]:

    medicines = get_medicines()
    if medicine_id is not None:
        medicines = medicines[medicines["id"] == medicine_id]

    return [
        Medicine(**row)
        for row in medicines
    ]

