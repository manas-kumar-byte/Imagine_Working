"""Module B — Consumption rate computation.
Owner: Forecasting Engineer
"""
from typing import TypedDict


class ConsumptionRateResult(TypedDict):
    avg_daily_use: float
    trend_pct: float     # e.g. +0.05 = usage rising 5% over the window
    volatility: float    # coefficient of variation or similar


def compute_consumption_rate(facility_id: str, medicine_id: str, window_days: int) -> ConsumptionRateResult:
    """Reads ConsumptionRecords for the given window via backend.db.store,
    returns average daily use, trend, and volatility.
    """
    raise NotImplementedError
