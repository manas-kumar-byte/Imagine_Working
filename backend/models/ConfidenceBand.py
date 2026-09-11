from typing import Literal, TypedDict  # noqa: N999


class ConfidenceBand(TypedDict):
    level: Literal["low", "medium", "high"]
    note: str
