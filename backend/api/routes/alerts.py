"""GET /alerts — currently-flagged emerging regional shortages.
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

from backend.api.schemas import AlertResponse
from backend.db.store import get_medicines
from backend.regional.shortage_detection import detect_emerging_shortage

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def list_alerts(medicine_id: str | None= None) -> list[AlertResponse]:

    if (medicine_id is not None):
        return [
            AlertResponse(
                region_id = med_response["region_id"],
                medicine_id = medicine_id,
                regional_risk_score = med_response["regional_risk_score"],
                spread_rate = med_response["spread_rate"],
                first_detected_at = med_response["first_detected_at"]
            )
            for med_response in detect_emerging_shortage(medicine_id=medicine_id)
        ]

    medicines = get_medicines()

    alerts: list[AlertResponse] = []

    for med_id in medicines["id"]:
        detection_response = detect_emerging_shortage(med_id)

        alerts.extend(
            AlertResponse(
                region_id=alert["region_id"],
                medicine_id=med_id,
                regional_risk_score=alert["regional_risk_score"],
                spread_rate=alert["spread_rate"],
                first_detected_at=alert["first_detected_at"]
            )
            for alert in detection_response
        )

    return alerts




