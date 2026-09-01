"""Module E — Plain-language explanation generator.
Owner: Recommendation Engineer

Judges remember "Facility X is likely to stock out in 6-9 days (medium
confidence); nearest facility Y has 40% surplus and is 12km away" far more
than a red dot with no reasoning. Keep this cheap and demo-able.
"""


def explain_recommendation(recommendation: dict) -> str:
    """Returns a 1-2 sentence plain-language rationale string for any
    recommendation dict (redistribution or intervention).
    """
    raise NotImplementedError
