"""InventorySnapshot entity — point-in-time stock level for one facility+medicine."""
from dataclasses import dataclass

# Possibly unite InventorySnapshot, ConsumptionRecord and Facility into one file? If not then just ignore
@dataclass
class InventorySnapshot:
    facility_id: str
    medicine_id: str
    timestamp: str           # ISO 8601 date
    stock_on_hand: float
    reorder_point: float
    max_capacity: float
