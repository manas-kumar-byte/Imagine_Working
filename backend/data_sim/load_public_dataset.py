"""Module A — Optional: load and normalize a public dataset (e.g. WHO, DHIS2
sample exports) into the same shape as the simulated data, so downstream
modules can't tell the difference.
Owner: Data/Simulation Lead

This does NOT fetch anything from the network. It expects a pre-downloaded
sample export dropped at data/public/<source_name>.json (the hackathon
timeline doesn't leave room to write a real WHO/DHIS2 API client, and this
module is explicitly marked "nice-to-have" in the spec). The json file's
top-level shape should already loosely resemble the target shape; this
function's job is field mapping/renaming/type coercion into the exact
dataclasses everyone else consumes.
"""
import json
import os

from backend.models.consumption import ConsumptionRecord
from backend.models.facility import Facility
from backend.models.inventory import InventorySnapshot
from backend.models.medicine import Medicine
from backend.models.replenishment import ReplenishmentOrder

_PUBLIC_DATA_DIR = os.path.join("data", "public")


def _normalize_facilities(raw: list[dict]) -> list[Facility]:
    return [
        Facility(
            id=r["id"],
            name=r.get("name", r["id"]),
            lat=float(r["lat"]),
            lon=float(r["lon"]),
            region_id=r["region_id"],
            type=r.get("type", "clinic"),
            tier=r.get("tier", "medium"),
            population_served=int(r.get("population_served", 0)),
        )
        for r in raw
    ]


def _normalize_medicines(raw: list[dict]) -> list[Medicine]:
    return [
        Medicine(
            id=r["id"],
            name=r.get("name", r["id"]),
            category=r.get("category", "other"),
            unit=r.get("unit", "units"),
            essential_flag=bool(r.get("essential_flag", True)),
            substitute_ids=list(r.get("substitute_ids", [])),
        )
        for r in raw
    ]


def _normalize_snapshots(
    raw: list[dict]
) -> list[InventorySnapshot]:

    return [
        InventorySnapshot(
            facility_id=r["facility_id"],
            medicine_id=r["medicine_id"],
            timestamp=r.get(
                "timestamp",
                r.get("date", "")
            ),
            stock_on_hand=float(
                r["stock_on_hand"]
            ),
            reorder_point=float(
                r.get("reorder_point", 0.0)
            ),
            max_capacity=float(
                r.get(
                    "max_capacity",
                    r["stock_on_hand"]
                )
            ),
        )
        for r in raw
    ]


def _normalize_consumption(raw: list[dict]) -> list[ConsumptionRecord]:
    return [
        ConsumptionRecord(
            facility_id=r["facility_id"],
            medicine_id=r["medicine_id"],
            date=r["date"],
            quantity_dispensed=float(r["quantity_dispensed"]),
        )
        for r in raw
    ]


def _normalize_orders(raw: list[dict]) -> list[ReplenishmentOrder]:
    return [
        ReplenishmentOrder(
            id=r["id"],
            facility_id=r["facility_id"],
            medicine_id=r["medicine_id"],
            order_date=r["order_date"],
            expected_delivery_date=r["expected_delivery_date"],
            actual_delivery_date=r.get("actual_delivery_date"),
            quantity=float(r["quantity"]),
            status=r.get("status", "delivered"),
        )
        for r in raw
    ]


def load_public_dataset(source_name: str) -> dict[str, list]:
    """
    Returns a dict with the same keys/shapes as the simulator output:
        {
          "facilities": List[Facility],
          "medicines": List[Medicine],
          "snapshots": List[InventorySnapshot],
          "consumption": List[ConsumptionRecord],
          "orders": List[ReplenishmentOrder],
        }

    Raises:
        FileNotFoundError: if data/public/<source_name>.json doesn't exist.
            Drop a sample export there first — see the module docstring.
        KeyError: if the fixture is missing an expected top-level key.
    """
    path = os.path.join(_PUBLIC_DATA_DIR, f"{source_name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No public dataset fixture at {path}. This function normalizes "
            f"a pre-downloaded sample export — it does not hit the network. "
            f"Place a WHO/DHIS2 sample export there as '{source_name}.json' "
            f"first (see load_public_dataset.py docstring for the expected "
            f"raw shape)."
        )

    with open(path, "r") as f:
        raw = json.load(f)

    return {
        "facilities": _normalize_facilities(raw.get("facilities", [])),
        "medicines": _normalize_medicines(raw.get("medicines", [])),
        "snapshots": _normalize_snapshots(raw.get("snapshots", [])),
        "consumption": _normalize_consumption(raw.get("consumption", [])),
        "orders": _normalize_orders(raw.get("orders", [])),
    }
