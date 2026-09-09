from typing import TypedDict, Literal

class ConfidenceBand(TypedDict):
    level: Literal["low", "medium", "high"]
    note: str
