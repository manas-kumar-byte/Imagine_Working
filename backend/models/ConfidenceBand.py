class ConfidenceBand(TypedDict):
    level: Literal["low", "medium", "high"]
    note: str