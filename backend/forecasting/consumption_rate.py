"""Module B — Consumption rate computation.
Owner: Forecasting Engineer
"""
from typing import TypedDict
from backend.db import store
from pandas import DataFrame


class ConsumptionRateResult(TypedDict):
    avg_daily_use: float
    trend_pct: float     # e.g. +0.05 = usage rising 5% over the window
    volatility: float    # coefficient of variation or similar


def compute_consumption_rate(facility_id: str, medicine_id: str, window_days: int) -> ConsumptionRateResult:
    """Reads ConsumptionRecords for the given window via backend.db.store,
    returns average daily use, trend, and volatility.
    """
    consumption = store.get_consumption(facility_id=facility_id, medicine_id=medicine_id, window_days=window_days)

    avg_daily_use = consumption["quantity_dispensed"].mean()
    trend_pct = ((consumption.iloc[-1]["quantity_dispensed"] / consumption.iloc[0]["quantity_dispensed"]) - 1) * 100
    # Volatility is simply standard deviation
    volatility = consumption["quantity_dispensed"].std()

    return ConsumptionRateResult(avg_daily_use=avg_daily_use, trend_pct=trend_pct, volatility=volatility)
