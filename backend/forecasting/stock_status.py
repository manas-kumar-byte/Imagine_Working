"""Module B — Stock status classification.
Owner: Forecasting Engineer
"""
from typing import TypedDict
from backend.config import VALID_STATUSES, STATUS_THRESHOLDS


class StockStatus(TypedDict):
    status: str        # one of VALID_STATUSES
    risk_score: float  # 0.0-1.0, higher = worse


def classify_stock_status(facility_id: str, medicine_id: str) -> StockStatus:
    """risk_score definition (do not change without team sign-off):
        risk_score = 1 - (days_remaining / reorder_lead_time), clipped to [0, 1]

    status is derived from risk_score via backend.config.STATUS_THRESHOLDS.
    """
    raise NotImplementedError
