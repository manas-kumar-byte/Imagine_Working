"""Medicine model.
Owner: Data/Simulation Lead (Person 1)
"""
from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class Medicine:
    id: str
    name: str
    category: str
    unit: str
    essential_flag: bool
    substitute_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
