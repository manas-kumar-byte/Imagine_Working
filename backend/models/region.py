"""Region entity — supports hierarchy via parent_region_id (clinic -> district -> state)."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Region:
    id: str
    name: str
    parent_region_id: Optional[str] = None
