"""ConsumptionRecord entity — daily dispensed quantity."""
from dataclasses import dataclass

# Possibly unite InventorySnapshot, ConsumptionRecord and Facility into one file? If not then just ignore
@dataclass
class ConsumptionRecord:
    facility_id: str
    medicine_id: str
    date: str                # ISO 8601
    quantity_dispensed: float
