from dataclasses import dataclass
from typing import List, Optional, TypedDict, Literal

class InterventionRecommendation(TypedDict):
    action: Literal["redistribute", "expedite_order", "emergency_procurement", "monitor"]
    priority: Literal["low", "medium", "high", "critical"]
    rationale: str