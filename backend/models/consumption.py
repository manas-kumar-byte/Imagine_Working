"""ConsumptionRecord model.
Owner: Data/Simulation Lead (Person 1)
"""
from dataclasses import dataclass, asdict


@dataclass
class ConsumptionRecord:
    facility_id: str
    medicine_id: str
    date: str  # ISO 8601, e.g. "2026-08-20"
    quantity_dispensed: float

    def to_dict(self) -> dict:
        return asdict(self)
