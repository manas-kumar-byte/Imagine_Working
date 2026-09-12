"""ReplenishmentOrder model.
Owner: Data/Simulation Lead (Person 1)
"""
from dataclasses import dataclass, asdict
from typing import Optional


VALID_STATUSES = ("pending", "in_transit", "delivered", "delayed")


@dataclass
class ReplenishmentOrder:
    id: str
    facility_id: str
    medicine_id: str
    order_date: str
    expected_delivery_date: str
    actual_delivery_date: Optional[str]
    quantity: float
    status: str

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid order status: {self.status!r}")

    def to_dict(self) -> dict:
        return asdict(self)
