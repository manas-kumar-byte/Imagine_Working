"""Module E — Uncertainty communication.
Owner: Recommendation Engineer (or shared with Backend Lead)
"""
from typing import TypedDict


class ConfidenceBand(TypedDict):
    level: str   # "low" | "medium" | "high"
    note: str    # e.g. "based on only 6 days of consumption history"


def confidence_band(forecast_result: dict) -> ConfidenceBand:
    """Takes a StockoutForecast (or similar) dict and derives a confidence
    level + human-readable caveat, e.g. from window size or volatility.
    """
    raise NotImplementedError
