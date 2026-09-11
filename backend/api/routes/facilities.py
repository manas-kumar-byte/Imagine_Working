"""GET /facilities, GET /facilities/{id}/status?medicine_id=
Owner: Backend/Integration Lead
"""
from fastapi import APIRouter

from backend.api.schemas import FacilityStatusResponse
from backend.db.store import get_facilities
from backend.explainability.confidence import confidence_band
from backend.forecasting.stock_status import classify_stock_status
from backend.forecasting.stockout_forecast import forecast_days_to_stockout
from backend.models.facility import Facility

router = APIRouter(prefix="/facilities", tags=["facilities"])


@router.get("")
def list_facilities() -> list[Facility]:
    df = get_facilities()
    records: list[dict] = df.to_dict("records")

    return [
        Facility(**rows)
        for rows in records
    ]


@router.get("/{facility_id}/status")
def facility_status(facility_id: str, medicine_id: str) -> FacilityStatusResponse:
    stock_status = classify_stock_status(facility_id=facility_id,medicine_id=medicine_id)
    forecast = forecast_days_to_stockout(facility_id=facility_id,medicine_id=medicine_id)
    confidence = confidence_band(dict(forecast))

    return FacilityStatusResponse(
        facility_id = facility_id,
        medicine_id = medicine_id,
        status = stock_status["status"],
        risk_score = stock_status["risk_score"],
        days_remaining = forecast["days_remaining"],
        low_estimate = forecast["low_estimate"],
        high_estimate = forecast["high_estimate"],
        confidence_level = confidence["level"]
    )

    