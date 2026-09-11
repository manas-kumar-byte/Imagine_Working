from dataclasses import dataclass
from typing import List, Optional, TypedDict, Literal

class RedistributionRecommendation(TypedDict):
    source_facility_id: str
    quantity: float
    distance_km: float
    urgency_score: float  # 0.0-1.0
    feasibility_score: float  # 0.0-1.0