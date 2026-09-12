
import math
from typing import List, Optional
import pandas as pd
from backend.models.facility import Facility
from backend.models.inventory import InventorySnapshot
from backend.forecasting.stockout_forecast import StockoutForecast
from backend.forecasting.stock_status import StockStatus
from backend.regional.region_risk import RegionRisk
from backend.regional.propagation_score import PropagationScore


from backend.db.store import (
    get_facilities as _get_facilities_df,
    get_medicines as _get_medicines_df,
    get_inventory_snapshots as _get_inventory_df,
)
# ---------------------------------------------------------------------------
# MOCK DATASET (hand-written, ~Day 1 sample per Section 6 of the design doc)
# Swap for backend.data.loader once Module A is producing real data.
# ---------------------------------------------------------------------------

DATA_CHOICE = 2


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _row_to_facility(row: "pd.Series") -> Facility:
    return Facility(
        id=str(row["id"]),
        name=str(row["name"]),
        lat=float(row["lat"]),
        lon=float(row["lon"]),
        region_id=str(row["region_id"]),
        type=str(row["type"]),
        tier=str(row["tier"]),
        population_served=int(row["population_served"]),
    )


def _row_to_inventory(row: "pd.Series") -> InventorySnapshot:
    return InventorySnapshot(
        facility_id=str(row["facility_id"]),
        medicine_id=str(row["medicine_id"]),
        timestamp=str(row["timestamp"]),
        stock_on_hand=float(row["stock_on_hand"]),
        reorder_point=float(row["reorder_point"]),
        max_capacity=float(row["max_capacity"]),
    )


def get_facility(facility_id: str) -> Optional[Facility]:
    df = _get_facilities_df(DATA_CHOICE)
    matches = df[df["id"] == facility_id]
    if matches.empty:
        return None
    return _row_to_facility(matches.iloc[0])


def get_facilities_in_region(region_id: str) -> List[Facility]:
    df = _get_facilities_df(DATA_CHOICE)
    matches = df[df["region_id"] == region_id]
    return [_row_to_facility(row) for _, row in matches.iterrows()]


def get_facilities_within_radius(lat: float, lon: float, radius_km: float,
                                  exclude_facility_id: Optional[str] = None) -> List[Facility]:
    df = _get_facilities_df(DATA_CHOICE)
    out = []
    for _, row in df.iterrows():
        if exclude_facility_id and str(row["id"]) == exclude_facility_id:
            continue
        if haversine_km(lat, lon, float(row["lat"]), float(row["lon"])) <= radius_km:
            out.append(_row_to_facility(row))
    return out


def get_inventory_snapshot(facility_id: str, medicine_id: str) -> Optional[InventorySnapshot]:
    df = _get_inventory_df(DATA_CHOICE, facility_id=facility_id, medicine_id=medicine_id)
    if df.empty:
        return None
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp")
    return _row_to_inventory(df.iloc[-1])


def get_medicine_meta(medicine_id: str) -> dict:
    """
    cold_chain / min_shipment aren't part of the frozen Medicine schema
    (design-doc section 3 only defines id/name/category/unit/essential_flag/
    substitute_ids) — I added them for feasibility scoring in
    redistribution.py. Falls back to safe defaults if the real medicine
    dataset doesn't have these columns; raise with Owner 1/4 if you'd rather
    add them to the real schema than infer here.
    """
    df = _get_medicines_df(DATA_CHOICE)
    matches = df[df["id"] == medicine_id]
    if matches.empty:
        return {"category": "unknown", "cold_chain": False, "min_shipment": 1.0}
    row = matches.iloc[0]
    return {
        "category": str(row["category"]) if "category" in df.columns else "unknown",
        "cold_chain": bool(row["cold_chain"]) if "cold_chain" in df.columns else False,
        "min_shipment": float(row["min_shipment"]) if "min_shipment" in df.columns else 1.0,
    }


# ---------------------------------------------------------------------------
# STUBS TO REPLACE — Module B (Person 2) and Module C (Person 2/3)
# Same placeholder logic as before; only the facility/inventory lookups now
# hit real (CSV-backed) data via backend.db.store instead of an in-memory list.
# ---------------------------------------------------------------------------

def forecast_days_to_stockout(facility_id: str, medicine_id: str) -> StockoutForecast:
    snap = get_inventory_snapshot(facility_id, medicine_id)
    if not snap:
        return {"days_remaining": 999.0, "low_estimate": 999.0, "high_estimate": 999.0, "method": "no_data"}
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