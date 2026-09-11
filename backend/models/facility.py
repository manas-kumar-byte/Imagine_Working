"""Facility entity — see docs/design-doc.md section 3 for the frozen schema."""
from dataclasses import dataclass


# Possibly unite InventorySnapshot, ConsumptionRecord and Facility into one file? If not then just ignore
@dataclass
class Facility:
    id: str                # e.g. "fac_0012"
    name: str
    lat: float
    lon: float
    region_id: str
    type: str               # "hospital" | "clinic" | "pharmacy" | "warehouse"
    tier: str               # capacity size, e.g. "small" | "medium" | "large"
    population_served: int
