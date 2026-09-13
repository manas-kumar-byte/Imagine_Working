"""Module B — Consumption rate computation.
Owner: Forecasting Engineer
"""

from typing import TypedDict

from backend.db import store
from backend.config import DIR_CHOICE


class ConsumptionRateResult(TypedDict):
    avg_daily_use: float
    trend_pct: float     # e.g. +0.05 = usage rising 5% over the window
    volatility: float    # coefficient of variation or similar


def compute_consumption_rate(
    facility_id: str,
    medicine_id: str,
    window_days: int
) -> ConsumptionRateResult:

    """Reads ConsumptionRecords for the given window via backend.db.store,
    returns average daily use, trend, and volatility.
    """

    consumption = store.get_consumption(
        facility_id=facility_id,
        medicine_id=medicine_id,
        window_days=window_days,
        choice=DIR_CHOICE
    )

    if consumption.empty:
        return {
            "avg_daily_use": 0.0,
            "trend_pct": 0.0,
            "volatility": 0.0
        }

    consumption = consumption.sort_values("date")

    quantities = consumption[
        "quantity_dispensed"
    ].astype(float)

    avg_daily_use = float(
        quantities.mean()
    )

    first_value = float(
        quantities.iloc[0]
    )

    last_value = float(
        quantities.iloc[-1]
    )

    if first_value == 0:
        trend_pct = 0.0
    else:
        trend_pct = (
            last_value / first_value
        ) - 1.0

    volatility = (
        float(quantities.std())
        if len(quantities) > 1
        else 0.0
    )

    return {
        "avg_daily_use": avg_daily_use,
        "trend_pct": float(trend_pct),
        "volatility": volatility
    }
