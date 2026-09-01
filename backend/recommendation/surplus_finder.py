"""Module D — Surplus facility finder.
Owner: Recommendation Engineer
"""
from typing import List, TypedDict


class SurplusFacility(TypedDict):
    facility_id: str
    surplus_qty: float
    distance_km: float


def find_surplus_facilities(medicine_id: str, near_facility_id: str, radius_km: float) -> List[SurplusFacility]:
    """Finds facilities within radius_km of near_facility_id that hold stock
    above their own reorder_point + a safety buffer, for the given medicine.
    """
    raise NotImplementedError
