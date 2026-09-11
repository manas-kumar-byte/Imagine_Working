"""ReplenishmentOrder entity."""
from dataclasses import dataclass


@dataclass
class ReplenishmentOrder:
    id: str
    facility_id: str
    medicine_id: str
    order_date: str              # ISO 8601
    expected_delivery_date: str  # ISO 8601
    actual_delivery_date: str | None   # None until delivered
    quantity: float
    status: str                   # "pending" | "in_transit" | "delivered" | "delayed"
