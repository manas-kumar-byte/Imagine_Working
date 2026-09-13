"""GET /medicines, GET /medicines?medicine_id=
Owner: Backend/Integration Lead
"""

from fastapi import APIRouter

from backend.db.store import get_medicines
from backend.models.medicine import Medicine

router = APIRouter(
    prefix="/medicines",
    tags=["medicines"]
)


@router.get("")
def list_medicines(
    medicine_id: str | None = None
) -> list[Medicine]:

    medicines = get_medicines()

    if medicine_id is not None:
        medicines = medicines[
            medicines["id"] == medicine_id
        ]

    records = medicines.to_dict("records")

    result = []

    for row in records:

        row["essential_flag"] = (
            str(row["essential_flag"]).lower() == "true"
        )

        row.setdefault(
            "substitute_ids",
            []
        )

        result.append(
            Medicine(**row)
        )

    return result