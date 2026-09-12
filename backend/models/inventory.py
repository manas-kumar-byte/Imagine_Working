"""InventorySnapshot dataclass — point-in-time stock level.
Owner: Backend/Integration Lead (Person 4)

Frozen per the team contract:
    facility_id, medicine_id, timestamp, stock_on_hand, reorder_point, max_capacity
Do not rename or retype without team sign-off — Module B (forecasting) and
Module D (recommendation) both read reorder_point/max_capacity directly.
"""
from dataclasses import dataclass, asdict


@dataclass
class InventorySnapshot:
    facility_id: str
    medicine_id: str
    timestamp: str  # ISO 8601 date
    stock_on_hand: float
    reorder_point: float
    max_capacity: float

    def to_dict(self) -> dict:
        return asdict(self)
