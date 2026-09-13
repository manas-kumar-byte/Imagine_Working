"""Module B — Stock status classification.
Owner: Forecasting Engineer
"""
from typing import TypedDict
from backend.config import VALID_STATUSES, STATUS_THRESHOLDS
from backend.db import store
from backend.forecasting import consumption_rate


class StockStatus(TypedDict):
    status: str        # one of VALID_STATUSES
    risk_score: float  # 0.0-1.0, higher = worse


def classify_stock_status(facility_id: str, medicine_id: str) -> StockStatus:
    """risk_score definition (do not change without team sign-off):
        risk_score = 1 - (days_remaining / reorder_lead_time), clipped to [0, 1]

    status is derived from risk_score via backend.config.STATUS_THRESHOLDS.
    """
    remaining_stock = store.get_inventory_snapshots(facility_id=facility_id, medicine_id=medicine_id).iloc[0]["stock_on_hand"]
    rate_of_consumption = consumption_rate.compute_consumption_rate(facility_id=facility_id, medicine_id=medicine_id, window_days=7)["avg_daily_use"]
    reorder_lead_time = store.get_replenishment_orders(facility_id=facility_id, medicine_id=medicine_id)["expected_delivery_date"]

    days_remaining = remaining_stock / rate_of_consumption

    risk_score = 1 - (days_remaining / reorder_lead_time)
    risk_score = max(0, min(1, risk_score))


    if risk_score < STATUS_THRESHOLDS["healthy"]:
        status = VALID_STATUSES[0]
    elif (risk_score >= STATUS_THRESHOLDS["healthy"]) & (risk_score < STATUS_THRESHOLDS["watch"]):
        status = VALID_STATUSES[1]
    elif (risk_score >= STATUS_THRESHOLDS["watch"]) & (risk_score < STATUS_THRESHOLDS["critical"]):
        status = VALID_STATUSES[2]
    else:
        status = VALID_STATUSES[3]
    
    return StockStatus(status=status, risk_score=risk_score)
