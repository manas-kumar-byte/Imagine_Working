"""
Data access + integration seams for Modules D & E.

WIRING NOTE (read this first):
Everything in the "STUBS TO REPLACE" section below has the *exact* signature
the real Module A (data) and Module B/C (forecasting/regional) will expose,
per the team contract. Once teammates land their code, swap these stub
bodies for real imports, e.g.:

    from backend.forecasting.engine import forecast_days_to_stockout, classify_stock_status
    from backend.forecasting.regional import aggregate_region_risk, shortage_propagation_score

Nothing in surplus_finder.py / redistribution.py / intervention.py should
need to change — they only call the function names below.
"""
import math
from typing import List, Optional

from backend.models import (
    Facility, InventorySnapshot, StockoutForecast, StockStatus,
    RegionRisk, PropagationScore,
)

# ---------------------------------------------------------------------------
# MOCK DATASET (hand-written, ~Day 1 sample per Section 6 of the design doc)
# Swap for backend.data.loader once Module A is producing real data.
# ---------------------------------------------------------------------------

_FACILITIES = [
    Facility("fac_0001", "Udupi District Hospital", 13.3409, 74.7421, "reg_udupi", "hospital", "large", 250000),
    Facility("fac_0002", "Manipal Clinic", 13.3525, 74.7869, "reg_udupi", "clinic", "small", 40000),
    Facility("fac_0003", "Kundapura PHC", 13.6230, 74.6890, "reg_udupi", "clinic", "small", 60000),
    Facility("fac_0004", "Mangalore Central Warehouse", 12.9141, 74.8560, "reg_mangalore", "warehouse", "large", 0),
    Facility("fac_0005", "Karkala Pharmacy", 13.2010, 74.9930, "reg_udupi", "pharmacy", "small", 15000),
]

_INVENTORY = [
    InventorySnapshot("fac_0001", "med_amoxicillin", "2026-09-08", 40, 200, 1000),
    InventorySnapshot("fac_0002", "med_amoxicillin", "2026-09-08", 30, 60, 300),
    InventorySnapshot("fac_0003", "med_amoxicillin", "2026-09-08", 500, 150, 800),
    InventorySnapshot("fac_0004", "med_amoxicillin", "2026-09-08", 5000, 500, 20000),
    InventorySnapshot("fac_0005", "med_amoxicillin", "2026-09-08", 20, 40, 200),
]

_MEDICINE_META = {
    # category used by feasibility scoring (cold-chain etc.)
    "med_amoxicillin": {"category": "antibiotic", "cold_chain": False, "min_shipment": 10},
    "med_insulin": {"category": "hormone", "cold_chain": True, "min_shipment": 5},
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def get_facility(facility_id: str) -> Optional[Facility]:
    return next((f for f in _FACILITIES if f.id == facility_id), None)


def get_facilities_in_region(region_id: str) -> List[Facility]:
    return [f for f in _FACILITIES if f.region_id == region_id]


def get_facilities_within_radius(lat: float, lon: float, radius_km: float,
                                  exclude_facility_id: Optional[str] = None) -> List[Facility]:
    out = []
    for f in _FACILITIES:
        if f.id == exclude_facility_id:
            continue
        if haversine_km(lat, lon, f.lat, f.lon) <= radius_km:
            out.append(f)
    return out


def get_inventory_snapshot(facility_id: str, medicine_id: str) -> Optional[InventorySnapshot]:
    matches = [s for s in _INVENTORY if s.facility_id == facility_id and s.medicine_id == medicine_id]
    return matches[-1] if matches else None  # latest by insertion order in mock data


def get_medicine_meta(medicine_id: str) -> dict:
    return _MEDICINE_META.get(medicine_id, {"category": "unknown", "cold_chain": False, "min_shipment": 1})


# ---------------------------------------------------------------------------
# STUBS TO REPLACE — Module B (Person 2) and Module C (Person 2/3)
# Signatures match Section 4 exactly. Mock logic below is only good enough
# to make Modules D/E runnable/demoable in isolation.
# ---------------------------------------------------------------------------

def forecast_days_to_stockout(facility_id: str, medicine_id: str) -> StockoutForecast:
    snap = get_inventory_snapshot(facility_id, medicine_id)
    if not snap:
        return {"days_remaining": 999.0, "low_estimate": 999.0, "high_estimate": 999.0, "method": "no_data"}
    # crude placeholder: assume ~10 units/day burn until Module B lands
    assumed_daily_use = max(snap.reorder_point / 20.0, 1.0)
    days = max(snap.stock_on_hand / assumed_daily_use, 0.0)
    return {
        "days_remaining": round(days, 1),
        "low_estimate": round(days * 0.7, 1),
        "high_estimate": round(days * 1.3, 1),
        "method": "mock_linear_burn",
    }


def classify_stock_status(facility_id: str, medicine_id: str) -> StockStatus:
    forecast = forecast_days_to_stockout(facility_id, medicine_id)
    days = forecast["days_remaining"]
    if days <= 0:
        status, risk = "stockout", 1.0
    elif days <= 5:
        status, risk = "critical", 0.85
    elif days <= 14:
        status, risk = "watch", 0.5
    else:
        status, risk = "healthy", 0.15
    return {"status": status, "risk_score": risk}


def aggregate_region_risk(region_id: str, medicine_id: str) -> RegionRisk:
    facilities = get_facilities_in_region(region_id)
    if not facilities:
        return {"facilities_at_risk": 0, "total_facilities": 0, "pct_at_risk": 0.0,
                "regional_risk_score": 0.0, "trend_direction": "stable"}
    statuses = [classify_stock_status(f.id, medicine_id) for f in facilities]
    at_risk = sum(1 for s in statuses if s["status"] in ("critical", "stockout", "watch"))
    avg_risk = sum(s["risk_score"] for s in statuses) / len(statuses)
    return {
        "facilities_at_risk": at_risk,
        "total_facilities": len(facilities),
        "pct_at_risk": round(at_risk / len(facilities), 2),
        "regional_risk_score": round(avg_risk, 2),
        "trend_direction": "rising" if avg_risk > 0.5 else "stable",
    }


def shortage_propagation_score(region_id: str, medicine_id: str) -> PropagationScore:
    risk = aggregate_region_risk(region_id, medicine_id)
    factors = []
    if risk["pct_at_risk"] > 0.4:
        factors.append("multiple facilities trending critical simultaneously")
    if risk["trend_direction"] == "rising":
        factors.append("regional risk score rising")
    return {"score": risk["regional_risk_score"], "contributing_factors": factors}
