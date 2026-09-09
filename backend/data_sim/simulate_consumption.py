"""Module A — Consumption simulation.
Owner: Data/Simulation Lead

IMPORTANT: pattern_params must support seasonal spikes, a slow demand-growth
trend, and random "shock" events. This is what makes the regional contagion
detection (Module C) visible in the demo — plain noise will not show a story.
"""
import math
import random
from datetime import date, timedelta
from typing import List

from backend.models.consumption import ConsumptionRecord

_SEASONAL_PERIOD_DAYS = 365.0


def simulate_consumption(
    facility_id: str,
    medicine_id: str,
    days: int,
    pattern_params: dict,
    start_date: date = None,
    seed: int = None,
) -> List[ConsumptionRecord]:
    """
    pattern_params example:
        {
          "base_daily_use": 12,
          "seasonal_amplitude": 0.3,     # +/- 30% seasonal swing
          "trend_pct_per_month": 0.02,   # slow demand growth
          "shock_events": [              # sudden demand spikes (e.g. outbreak)
              {"start_day": 40, "duration_days": 10, "multiplier": 3.0}
          ],
          "noise_std": 0.1
        }

    Returns:
        List[ConsumptionRecord], one per day.
    """
    rng = random.Random(seed)

    base_daily_use = pattern_params.get("base_daily_use", 10.0)
    seasonal_amplitude = pattern_params.get("seasonal_amplitude", 0.0)
    trend_pct_per_month = pattern_params.get("trend_pct_per_month", 0.0)
    shock_events = pattern_params.get("shock_events", [])
    noise_std = pattern_params.get("noise_std", 0.0)

    # Convert a monthly growth rate into an equivalent daily compounding
    # rate: (1 + monthly)^(1/30.4) - 1.
    if trend_pct_per_month:
        daily_trend_rate = (1.0 + trend_pct_per_month) ** (1.0 / 30.4) - 1.0
    else:
        daily_trend_rate = 0.0

    if start_date is None:
        start_date = date.today() - timedelta(days=days)

    # Pre-resolve which day indices fall inside a shock window, and by how
    # much, so overlapping shocks stack multiplicatively rather than one
    # silently overwriting another.
    def shock_multiplier_for_day(day_idx: int) -> float:
        multiplier = 1.0
        for shock in shock_events:
            shock_start = shock["start_day"]
            shock_end = shock_start + shock["duration_days"]
            if shock_start <= day_idx < shock_end:
                multiplier *= shock["multiplier"]
        return multiplier

    records: List[ConsumptionRecord] = []
    for day_idx in range(days):
        current_date = start_date + timedelta(days=day_idx)

        seasonal_factor = 1.0 + seasonal_amplitude * math.sin(
            2 * math.pi * day_idx / _SEASONAL_PERIOD_DAYS
        )
        trend_factor = (1.0 + daily_trend_rate) ** day_idx
        shock_factor = shock_multiplier_for_day(day_idx)
        noise_factor = 1.0 + rng.gauss(0.0, noise_std) if noise_std else 1.0

        quantity = base_daily_use * seasonal_factor * trend_factor * shock_factor * noise_factor
        quantity = max(0.0, quantity)

        records.append(
            ConsumptionRecord(
                facility_id=facility_id,
                medicine_id=medicine_id,
                date=current_date.isoformat(),
                quantity_dispensed=round(quantity, 2),
            )
        )

    return records
