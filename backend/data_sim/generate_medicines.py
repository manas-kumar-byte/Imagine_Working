"""Module A — Medicine list generation.
Owner: Data/Simulation Lead
"""
from typing import List
from backend.models.medicine import Medicine


def generate_medicines(essential_list: List[str]) -> List[Medicine]:
    """Build Medicine objects from a list of essential medicine names
    (e.g. WHO Essential Medicines List subset).

    Returns:
        List[Medicine]
    """
    raise NotImplementedError
