"""Module B — Days-to-stockout forecasting.
Owner: Forecasting Engineer
"""
from typing import TypedDict

from backend.db import store
from backend.forecasting import consumption_rate


class StockoutForecast(TypedDict):
    days_remaining: float
    low_estimate: float
    high_estimate: float
    method: str   # e.g. "linear_depletion", "arima", "moving_average"

class StockoutDetails(TypedDict):
    region_id: str
    distributor: str
    medicine_id: str
    num_stockout: int
    num_critical: int
    num_watch: int
    num_healthy: int
    risk_score: float


def forecast_days_to_stockout(
    facility_id: str,
    medicine_id: str
) -> StockoutForecast:

    """Combines current stock_on_hand with compute_consumption_rate() output
    to estimate days until stock hits zero, with a low/high uncertainty band.
    Keep the method simple and explainable first (e.g. current_stock / avg_daily_use,
    band = +/- volatility-scaled range); only reach for time-series models if
    time allows.
    """

    inventory = store.get_inventory_snapshots(
        facility_id=facility_id,
        medicine_id=medicine_id
    )

    if inventory.empty:
        return StockoutForecast(
            days_remaining=0.0,
            low_estimate=0.0,
            high_estimate=0.0,
            method="no_data"
        )

    inventory = inventory.sort_values("timestamp")

    current_stock = float(
        inventory.iloc[-1]["stock_on_hand"]
    )

    rate = consumption_rate.compute_consumption_rate(
        facility_id=facility_id,
        medicine_id=medicine_id,
        window_days=7
    )

    avg_daily_use = float(rate["avg_daily_use"])
    trend = float(rate["trend_pct"])
    volatility = float(rate["volatility"])

    if avg_daily_use <= 0:
        return StockoutForecast(
            days_remaining=9999.0,
            low_estimate=9999.0,
            high_estimate=9999.0,
            method="no_consumption"
        )

    adjusted_daily_use = avg_daily_use * (1 + trend)

    adjusted_daily_use = max(
        adjusted_daily_use,
        0.1
    )

    k = 1.943

    uncertainty = k * volatility

    low_daily_use = max(
        adjusted_daily_use - uncertainty,
        0.1
    )

    high_daily_use = max(
        adjusted_daily_use + uncertainty,
        0.1
    )

    days_remaining = current_stock / adjusted_daily_use

    low_estimate = current_stock / high_daily_use
    high_estimate = current_stock / low_daily_use

    return StockoutForecast(
        days_remaining=round(float(days_remaining), 2),
        low_estimate=round(float(low_estimate), 2),
        high_estimate=round(float(high_estimate), 2),
        method="Confidence interval"
    )