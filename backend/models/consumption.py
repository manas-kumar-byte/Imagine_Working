"""ConsumptionRecord entity — daily dispensed quantity."""
from dataclasses import dataclass

@dataclass
class ConsumptionRecord:
    facility_id: str
    medicine_id: str
    date: str                # ISO 8601
    quantity_dispensed: float
