"""Module A — Replenishment order simulation.
Owner: Data/Simulation Lead
"""
import random
from datetime import date, timedelta
from typing import List, Optional

from backend.models.replenishment import ReplenishmentOrder

_DEFAULT_REORDER_CYCLE_DAYS = 21
_DEFAULT_ORDER_QTY_RANGE = (200, 800)


def _draw_lead_time(lead_time_dist: dict, rng: random.Random) -> float:
    distribution = lead_time_dist.get("distribution", "normal")
    if distribution == "normal":
        mean = lead_time_dist.get("mean_days", 7)
        std = lead_time_dist.get("std_days", 2)
        return max(1.0, rng.gauss(mean, std))
    elif distribution == "uniform":
        lo = lead_time_dist.get("min_days", 3)
        hi = lead_time_dist.get("max_days", 14)
        return rng.uniform(lo, hi)
    else:
        # Unknown distribution name: fall back to a flat mean rather than
        # raising, so a typo in config degrades gracefully.
        return lead_time_dist.get("mean_days", 7)


def simulate_replenishment(
    facility_id: str,
    medicine_id: str,
    days: int,
    lead_time_dist: dict,
    reorder_cycle_days: int = _DEFAULT_REORDER_CYCLE_DAYS,
    order_qty_range: tuple = _DEFAULT_ORDER_QTY_RANGE,
    start_date: date = None,
    as_of_day: int = None,
    seed: int = None,
) -> List[ReplenishmentOrder]:
    """
    lead_time_dist example:
        {"distribution": "normal", "mean_days": 7, "std_days": 2, "delay_prob": 0.15}

    delay_prob: probability an order gets flagged "delayed" (actual > expected).
    This is the lever for the "supply-side delay" demo scenario.

    Orders are placed on a fixed reorder cycle (reorder_cycle_days apart)
    over the `days` window — one facility/medicine pair reorders roughly
    every reorder_cycle_days, which is a simplification since actual
    consumption isn't wired into this function's signature.

    Returns:
        List[ReplenishmentOrder]
    """
    rng = random.Random(seed)
    delay_prob = lead_time_dist.get("delay_prob", 0.0)

    if start_date is None:
        start_date = date.today() - timedelta(days=days)
    if as_of_day is None:
        as_of_day = days  # treat "today" as the last day of the window

    orders: List[ReplenishmentOrder] = []
    order_idx = 0
    order_day = 0

    while order_day < days:
        order_date = start_date + timedelta(days=order_day)
        lead_time_days = _draw_lead_time(lead_time_dist, rng)
        expected_delivery_day = order_day + lead_time_days
        expected_delivery_date = start_date + timedelta(days=round(expected_delivery_day))

        is_delayed = rng.random() < delay_prob
        actual_delivery_date: Optional[str]
        actual_delivery_day: Optional[float]

        if is_delayed:
            extra_delay_days = rng.uniform(2, 10)
            actual_delivery_day = expected_delivery_day + extra_delay_days
        else:
            # Small +/- jitter even for "on time" deliveries so not every
            # non-delayed order lands on the exact expected day.
            actual_delivery_day = expected_delivery_day + rng.uniform(-0.5, 0.5)

        if actual_delivery_day <= as_of_day:
            actual_delivery_date = (
                start_date + timedelta(days=round(actual_delivery_day))
            ).isoformat()
            status = "delayed" if is_delayed else "delivered"
        else:
            # Hasn't arrived yet as of the simulation's "now".
            actual_delivery_date = None
            status = "in_transit" if expected_delivery_day <= as_of_day else "pending"

        order_id = f"ord_{facility_id}_{medicine_id}_{order_idx:04d}"
        quantity = float(rng.randint(*order_qty_range))

        orders.append(
            ReplenishmentOrder(
                id=order_id,
                facility_id=facility_id,
                medicine_id=medicine_id,
                order_date=order_date.isoformat(),
                expected_delivery_date=expected_delivery_date.isoformat(),
                actual_delivery_date=actual_delivery_date,
                quantity=quantity,
                status=status,
            )
        )

        order_idx += 1
        order_day += reorder_cycle_days

    return orders
