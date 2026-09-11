"""Medicine entity."""
from dataclasses import dataclass, field


@dataclass
class Medicine:
    id: str                 # e.g. "med_amoxicillin"
    name: str
    category: str
    unit: str                # "tablets" | "vials" | etc.
    essential_flag: bool
    substitute_ids: list[str] = field(default_factory=list)
