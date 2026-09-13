"""Module B — Days-to-stockout forecasting.
Owner: Forecasting Engineer
"""
from typing import TypedDict
from backend.forecasting import consumption_rate
from backend.db import store


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

def forecast_days_to_stockout(facility_id: str, medicine_id: str) -> StockoutForecast:
    """Combines current stock_on_hand with compute_consumption_rate() output
    to estimate days until stock hits zero, with a low/high uncertainty band.

    Keep the method simple and explainable first (e.g. current_stock / avg_daily_use,
    band = +/- volatility-scaled range); only reach for time-series models if
    time allows.
    """
    current_stock = store.get_inventory_snapshots(facility_id=facility_id, medicine_id=medicine_id).iloc[0]["stock_on_hand"]

    rate = consumption_rate.compute_consumption_rate(facility_id=facility_id, medicine_id=medicine_id, window_days=7)

    avg_daily_use = rate["avg_daily_use"]
    trend = rate["trend_pct"] / 100
    volatility = rate["volatility"]

    # Critical value from t-table at 95% certainty, 2-tail and 6 DoF (7 values in window)
    k = 1.943

    estimate_bound = k * volatility

    rate_estimate_lower_bound = trend - estimate_bound
    rate_estimate_higher_bound = trend + estimate_bound

    # Estimate = avg_daily_use +/- estimate_bound
    estimate = avg_daily_use * (1 + trend)
    estimate_lower_bound = avg_daily_use * (1 + rate_estimate_lower_bound)
    estimate_higher_bound = avg_daily_use * (1 + rate_estimate_higher_bound)
    days_remaining = current_stock / estimate

    return StockoutForecast(days_remaining=days_remaining, low_estimate=estimate_lower_bound, high_estimate=estimate_higher_bound, method="Confidence interval")
