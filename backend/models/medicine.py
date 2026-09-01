"""Medicine entity."""
from dataclasses import dataclass, field
from typing import List

@dataclass
class Medicine:
    id: str                 # e.g. "med_amoxicillin"
    name: str
    category: str
    unit: str                # "tablets" | "vials" | etc.
    essential_flag: bool
    substitute_ids: List[str] = field(default_factory=list)
