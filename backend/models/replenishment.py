"""ReplenishmentOrder entity."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class ReplenishmentOrder:
    id: str
    facility_id: str
    medicine_id: str
    order_date: str              # ISO 8601
    expected_delivery_date: str  # ISO 8601
    actual_delivery_date: Optional[str]   # None until delivered
    quantity: float
    status: str                   # "pending" | "in_transit" | "delivered" | "delayed"
