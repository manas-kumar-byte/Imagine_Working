"""Region dataclass — supports hierarchy via parent_region_id.
Owner: Backend/Integration Lead (Person 4)
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Region:
    id: str
    name: str
    parent_region_id: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)
