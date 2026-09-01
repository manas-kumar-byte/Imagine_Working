"""GET /alerts — currently-flagged emerging regional shortages.
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def list_alerts(medicine_id: str = None):
    raise NotImplementedError
