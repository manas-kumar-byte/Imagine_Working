
import math

import pandas as pd  # type: ignore

from backend.db.store import (
    get_facilities as _get_facilities_df,
)
from backend.db.store import (
    get_inventory_snapshots as _get_inventory_df,
)
from backend.db.store import (
    get_medicines as _get_medicines_df,
)
from backend.forecasting.stock_status import StockStatus
from backend.forecasting.stockout_forecast import StockoutForecast
from backend.models.facility import Facility
from backend.models.medicine import Medicine
from backend.models.inventory import InventorySnapshot
from backend.regional.propagation_score import PropagationScore
from backend.regional.region_risk import RegionRisk

# ---------------------------------------------------------------------------
# MOCK DATASET (hand-written, ~Day 1 sample per Section 6 of the design doc)
# Swap for backend.data.loader once Module A is producing real data.
# ---------------------------------------------------------------------------
from backend.config import DIR_CHOICE
DATA_CHOICE = DIR_CHOICE


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

def _row_to_medicine(row: "pd.Series") -> Medicine:

    return Medicine(

        id=str(row["id"]),

        name=str(row["name"]),

        category=str(row["category"]),

        unit=str(row["unit"]),

        essential_flag=bool(row["essential_flag"]),

        substitute_ids=[],

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


def get_facility(facility_id: str) -> Facility | None:
    df = _get_facilities_df(DATA_CHOICE)
    matches = df[df["id"] == facility_id]
    if matches.empty:
        return None
    return _row_to_facility(matches.iloc[0])


def get_facilities_in_region(region_id: str) -> list[Facility]:
    df = _get_facilities_df(DATA_CHOICE)
    matches = df[df["region_id"] == region_id]
    return [_row_to_facility(row) for _, row in matches.iterrows()]


def get_facilities_within_radius(lat: float, lon: float, radius_km: float,
                                  exclude_facility_id: str | None = None) -> list[Facility]:
    df = _get_facilities_df(DATA_CHOICE)
    out = []
    for _, row in df.iterrows():
        if exclude_facility_id and str(row["id"]) == exclude_facility_id:
            continue
        if haversine_km(lat, lon, float(row["lat"]), float(row["lon"])) <= radius_km:
            out.append(_row_to_facility(row))
    return out


def get_inventory_snapshot(facility_id: str, medicine_id: str) -> InventorySnapshot | None:
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


from backend.forecasting.stock_status import (
    classify_stock_status as _classify_stock_status,
)
from backend.forecasting.stockout_forecast import (
    forecast_days_to_stockout as _forecast_days_to_stockout,
)
from backend.regional.propagation_score import (
    shortage_propagation_score as _shortage_propagation_score,
)
from backend.regional.region_risk import (
    aggregate_region_risk as _aggregate_region_risk,
)


def forecast_days_to_stockout(
    facility_id: str,
    medicine_id: str
) -> StockoutForecast:

    return _forecast_days_to_stockout(
        facility_id=facility_id,
        medicine_id=medicine_id
    )


def classify_stock_status(
    facility_id: str,
    medicine_id: str
) -> StockStatus:

    return _classify_stock_status(
        facility_id=facility_id,
        medicine_id=medicine_id
    )


def aggregate_region_risk(
    region_id: str,
    medicine_id: str
) -> RegionRisk:

    return _aggregate_region_risk(
        region_id=region_id,
        medicine_id=medicine_id
    )


def shortage_propagation_score(
    region_id: str,
    medicine_id: str
) -> PropagationScore:

    return _shortage_propagation_score(
        region_id=region_id,
        medicine_id=medicine_id
    )

def get_medicine(medicine_id: str) -> Medicine | None:

    df = _get_medicines_df(DATA_CHOICE)

    matches = df[df["id"] == medicine_id]

    if matches.empty:

        return None

    return _row_to_medicine(matches.iloc[0])