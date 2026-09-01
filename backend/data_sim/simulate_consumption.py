"""Module A — Consumption simulation.
Owner: Data/Simulation Lead

IMPORTANT: pattern_params must support seasonal spikes, a slow demand-growth
trend, and random "shock" events. This is what makes the regional contagion
detection (Module C) visible in the demo — plain noise will not show a story.
"""
from typing import List
from backend.models.consumption import ConsumptionRecord


def simulate_consumption(
    facility_id: str,
    medicine_id: str,
    days: int,
    pattern_params: dict,
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
    raise NotImplementedError
