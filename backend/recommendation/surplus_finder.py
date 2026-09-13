"""Module D — Surplus facility finder.
Owner: Recommendation Engineer
"""


from backend.explainability import data_access as da
from backend.models.SurplusFacility import SurplusFacility

SAFETY_BUFFER_PCT = 0.2

def find_surplus_facilities(medicine_id: str, near_facility_id: str, radius_km: float) -> list[SurplusFacility]:
    """Finds facilities within radius_km of near_facility_id that hold stock
    above their own reorder_point + a safety buffer, for the given medicine.
    """
    origin = da.get_facility(near_facility_id)
    if origin is None:
        return []

    candidates = da.get_facilities_within_radius(
        origin.lat, origin.lon, radius_km, exclude_facility_id=near_facility_id
    )

    results: list[SurplusFacility] = []
    for fac in candidates:
        snap = da.get_inventory_snapshot(fac.id, medicine_id)
        if snap is None:
            continue
        safe_threshold = snap.reorder_point * (1 + SAFETY_BUFFER_PCT)
        surplus_qty = snap.stock_on_hand - safe_threshold
        if surplus_qty <= 0:
            continue
        distance_km = da.haversine_km(origin.lat, origin.lon, fac.lat, fac.lon)
        results.append({
            "facility_id": fac.id,
            "surplus_qty": round(surplus_qty, 1),
            "distance_km": round(distance_km, 1),
        })

    results.sort(key=lambda r: r["distance_km"])
    return results
