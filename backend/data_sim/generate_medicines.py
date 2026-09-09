"""Module A — Medicine list generation.
Owner: Data/Simulation Lead
"""
import re
from typing import List

from backend.models.medicine import Medicine

# Keyword -> (category, unit). Checked in order; first match wins.
# Covers common WHO Essential Medicines List entries. Anything unmatched
# falls back to a generic category/unit rather than raising, since the
# essential_list passed in may include names outside this table.
_CATEGORY_RULES = [
    (r"amoxicillin|ampicillin|ciprofloxacin|azithromycin|doxycycline|"
     r"metronidazole|penicillin|cephalexin", "antibiotic", "tablets"),
    (r"paracetamol|acetaminophen|ibuprofen|aspirin|diclofenac|morphine|"
     r"tramadol", "analgesic", "tablets"),
    (r"oral rehydration|ors\b", "rehydration", "sachets"),
    (r"insulin", "hormone", "vials"),
    (r"vaccine|immunoglobulin|toxoid", "vaccine", "vials"),
    (r"salbutamol|albuterol|beclometasone", "respiratory", "inhalers"),
    (r"chlorhexidine|povidone|ethanol|isopropyl", "antiseptic", "ml"),
    (r"folic acid|iron|ferrous|multivitamin|vitamin", "supplement", "tablets"),
    (r"artemether|artesunate|quinine|chloroquine", "antimalarial", "tablets"),
    (r"isoniazid|rifampicin|ethambutol|pyrazinamide", "antituberculosis", "tablets"),
    (r"diazepam|phenobarbital|carbamazepine", "anticonvulsant", "tablets"),
    (r"oxytocin|misoprostol", "obstetric", "vials"),
    (r"saline|ringer|dextrose", "iv_fluid", "ml"),
]

_DEFAULT_CATEGORY = "other"
_DEFAULT_UNIT = "units"


def _classify(name: str) -> tuple:
    lowered = name.lower()
    for pattern, category, unit in _CATEGORY_RULES:
        if re.search(pattern, lowered):
            return category, unit
    return _DEFAULT_CATEGORY, _DEFAULT_UNIT


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug


def generate_medicines(essential_list: List[str]) -> List[Medicine]:
    """Build Medicine objects from a list of essential medicine names
    (e.g. WHO Essential Medicines List subset).

    Returns:
        List[Medicine]
    """
    medicines: List[Medicine] = []
    category_to_ids: dict = {}

    # First pass: build medicines and index by category so we can wire up
    # substitute_ids (same category == plausible interchangeable drug).
    seen_ids = set()
    for name in essential_list:
        slug = _slugify(name)
        med_id = f"med_{slug}"
        # Guard against duplicate names producing duplicate ids.
        suffix = 2
        while med_id in seen_ids:
            med_id = f"med_{slug}_{suffix}"
            suffix += 1
        seen_ids.add(med_id)

        category, unit = _classify(name)

        medicine = Medicine(
            id=med_id,
            name=name,
            category=category,
            unit=unit,
            essential_flag=True,
            substitute_ids=[],
        )
        medicines.append(medicine)
        category_to_ids.setdefault(category, []).append(med_id)

    # Second pass: fill in substitute_ids from same-category siblings.
    # Skip the "other" bucket — grouping unclassified drugs as substitutes
    # for each other isn't medically meaningful, just an artifact of the
    # classifier not recognizing the name.
    for medicine in medicines:
        if medicine.category == _DEFAULT_CATEGORY:
            continue
        siblings = category_to_ids.get(medicine.category, [])
        medicine.substitute_ids = [mid for mid in siblings if mid != medicine.id]

    return medicines
