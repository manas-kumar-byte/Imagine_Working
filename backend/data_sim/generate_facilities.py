"""Module A — Facility generation.
Owner: Data/Simulation Lead
"""
from typing import List
from backend.models.facility import Facility


def generate_facilities(n: int, region_config: dict) -> List[Facility]:
    """Generate n synthetic facilities spread across the regions in region_config.

    Args:
        n: number of facilities to generate.
        region_config: e.g. {"region_ids": ["reg_north", "reg_south"],
                              "bounds": {"lat_min":..,"lat_max":..,"lon_min":..,"lon_max":..}}

    Returns:
        List[Facility]
    """
    raise NotImplementedError
