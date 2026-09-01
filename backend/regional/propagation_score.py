"""Module C — Shortage propagation / contagion score.
Owner: Forecasting Engineer
"""
from typing import List, TypedDict


class PropagationScore(TypedDict):
    score: float                    # 0.0-1.0, likelihood of spreading to neighbors
    contributing_factors: List[str]  # human-readable, e.g. ["shared distributor X", "3 adjacent facilities trending up"]


def shortage_propagation_score(region_id: str, medicine_id: str) -> PropagationScore:
    """Simple defensible approach: treat facilities as nodes in a graph
    (edges = shared distributor OR geographic proximity within radius_km);
    score rises with number of at-risk neighbors and shared-supplier overlap.
    """
    raise NotImplementedError
