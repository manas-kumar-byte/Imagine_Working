"""Module B — Stock status classification.
Owner: Forecasting Engineer
"""

from typing import TypedDict

import pandas as pd  # type: ignore

from backend.config import STATUS_THRESHOLDS, VALID_STATUSES
from backend.db import store
from backend.forecasting import consumption_rate


class StockStatus(TypedDict):
    status: str        # one of VALID_STATUSES
    risk_score: float  # 0.0-1.0, higher = worse


def classify_stock_status(
    facility_id: str,
    medicine_id: str
) -> StockStatus:

    """risk_score definition (do not change without team sign-off):
        risk_score = 1 - (days_remaining / reorder_lead_time), clipped to [0, 1]
    status is derived from risk_score via backend.config.STATUS_THRESHOLDS.
    """

    inventory = store.get_inventory_snapshots(
        facility_id=facility_id,
        medicine_id=medicine_id
    )

    if inventory.empty:
        return StockStatus(
            status=VALID_STATUSES[3],
            risk_score=1.0
        )

    inventory["timestamp"] = inventory["timestamp"].astype(str)
    inventory = inventory.sort_values("timestamp")

    remaining_stock = float(
        inventory.iloc[-1]["stock_on_hand"]
    )

    rate = consumption_rate.compute_consumption_rate(
        facility_id=facility_id,
        medicine_id=medicine_id,
        window_days=7
    )

    rate_of_consumption = float(rate["avg_daily_use"])

    if rate_of_consumption <= 0:
        return StockStatus(
            status=VALID_STATUSES[0],
            risk_score=0.0
        )

    days_remaining = remaining_stock / rate_of_consumption

    replenishment = store.get_replenishment_orders(
        facility_id=facility_id,
        medicine_id=medicine_id
    )

    reorder_lead_time = 7.0

    if not replenishment.empty:
        replenishment["order_date"] = pd.to_datetime(
            replenishment["order_date"],
            errors="coerce"
        )

        replenishment["expected_delivery_date"] = pd.to_datetime(
            replenishment["expected_delivery_date"],
            errors="coerce"
        )

        valid_orders = replenishment.dropna(
            subset=["order_date", "expected_delivery_date"]
        ).copy()

        if not valid_orders.empty:
            lead_times = (
                valid_orders["expected_delivery_date"]
                - valid_orders["order_date"]
            ).dt.days

            valid_lead_times = lead_times[lead_times > 0]

            if not valid_lead_times.empty:
                reorder_lead_time = float(
                    valid_lead_times.mean()
                )

    risk_score = 1 - (
        days_remaining / reorder_lead_time
    )

    risk_score = max(
        0.0,
        min(1.0, float(risk_score))
    )

    """
    These values must be tuned
    """

    if risk_score < STATUS_THRESHOLDS["healthy"]:
        status = VALID_STATUSES[0]

    elif (
        risk_score >= STATUS_THRESHOLDS["healthy"]
        and risk_score < STATUS_THRESHOLDS["watch"]
    ):
        status = VALID_STATUSES[1]

    elif (
        risk_score >= STATUS_THRESHOLDS["watch"]
        and risk_score < STATUS_THRESHOLDS["critical"]
    ):
        status = VALID_STATUSES[2]

    else:
        status = VALID_STATUSES[3]

    return StockStatus(
        status=status,
        risk_score=risk_score
    )