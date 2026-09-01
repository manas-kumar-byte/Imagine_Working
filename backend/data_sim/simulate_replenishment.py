"""Module A — Replenishment order simulation.
Owner: Data/Simulation Lead
"""
from typing import List
from backend.models.replenishment import ReplenishmentOrder


def simulate_replenishment(
    facility_id: str,
    medicine_id: str,
    days: int,
    lead_time_dist: dict,
) -> List[ReplenishmentOrder]:
    """
    lead_time_dist example:
        {"distribution": "normal", "mean_days": 7, "std_days": 2, "delay_prob": 0.15}

    delay_prob: probability an order gets flagged "delayed" (actual > expected).
    This is the lever for the "supply-side delay" demo scenario.

    Returns:
        List[ReplenishmentOrder]
    """
    raise NotImplementedError
