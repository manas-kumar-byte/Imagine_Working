from dataclasses import dataclass
from typing import List, Optional, TypedDict, Literal

class SurplusFacility(TypedDict):
    facility_id: str
    surplus_qty: float
    distance_km: float