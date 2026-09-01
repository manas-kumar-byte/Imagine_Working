"""Module B — Days-to-stockout forecasting.
Owner: Forecasting Engineer
"""
from typing import TypedDict


class StockoutForecast(TypedDict):
    days_remaining: float
    low_estimate: float
    high_estimate: float
    method: str   # e.g. "linear_depletion", "arima", "moving_average"


def forecast_days_to_stockout(facility_id: str, medicine_id: str) -> StockoutForecast:
    """Combines current stock_on_hand with compute_consumption_rate() output
    to estimate days until stock hits zero, with a low/high uncertainty band.

    Keep the method simple and explainable first (e.g. current_stock / avg_daily_use,
    band = +/- volatility-scaled range); only reach for time-series models if
    time allows.
    """
    raise NotImplementedError
