"""
Orchestration script — runs the whole Module A pipeline and writes CSVs.

Run with:

    python -m scripts.seed_data

before starting the FastAPI server.
"""

import csv
import os
import random
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta, timezone

from backend.data_sim.generate_facilities import generate_facilities
from backend.data_sim.generate_medicines import generate_medicines
from backend.data_sim.simulate_consumption import simulate_consumption
from backend.data_sim.simulate_replenishment import simulate_replenishment
from backend.models.inventory import InventorySnapshot

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SEED = 42

N_FACILITIES = 18

SIM_DAYS = 180

OUT_DIR = os.path.join(
    "data",
    "simulated",
)

REGION_CONFIG = {
    "region_ids": [
        "reg_north",
        "reg_south",
        "reg_east",
    ],
    "bounds": {
        "lat_min": 5.0,
        "lat_max": 15.0,
        "lon_min": 30.0,
        "lon_max": 45.0,
    },
}

ESSENTIAL_MEDICINES = [
    "Amoxicillin",
    "Paracetamol",
    "Oral Rehydration Salts",
    "Insulin",
    "Salbutamol",
    "Ciprofloxacin",
    "Diazepam",
    "Folic Acid",
    "Artesunate",
    "Oxytocin",
    "Ringer's Lactate",
    "Isoniazid",
]

DEFAULT_LEAD_TIME_DIST = {
    "distribution": "normal",
    "mean_days": 7,
    "std_days": 2,
    "delay_prob": 0.10,
}

SAFETY_BUFFER_DAYS = 5

MAX_CAPACITY_MULTIPLIER_RANGE = (
    2.5,
    4.0,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_pattern_params(
    facility,
    rng: random.Random,
) -> dict:
    """
    Generate the normal consumption pattern for a facility.
    """

    tier_multiplier = {
        "small": 1.0,
        "medium": 2.5,
        "large": 6.0,
    }.get(
        str(facility.tier).lower(),
        1.0,
    )

    return {
        "base_daily_use": round(
            rng.uniform(3, 10) * tier_multiplier,
            1,
        ),
        "seasonal_amplitude": round(
            rng.uniform(0.05, 0.15),
            2,
        ),
        "trend_pct_per_month": round(
            rng.uniform(-0.005, 0.01),
            4,
        ),
        "shock_events": [],
        "noise_std": 0.08,
    }


def _compute_inventory_snapshots(
    facility_id,
    medicine_id,
    consumption,
    orders,
    initial_stock,
    reorder_point,
    max_capacity,
):
    """
    Build daily inventory snapshots.

    Stock balance:

        stock[t] =
            stock[t-1]
            + deliveries[t]
            - consumption[t]

    Stock is never allowed to become negative.
    """

    deliveries_by_date: dict[str, float] = {}

    for order in orders:
        delivery_date = order.actual_delivery_date

        if not delivery_date:
            continue

        deliveries_by_date[delivery_date] = (
            deliveries_by_date.get(
                delivery_date,
                0.0,
            )
            + float(order.quantity)
        )

    snapshots = []

    stock = float(initial_stock)

    for record in consumption:
        record_date = str(record.date)

        # Add deliveries arriving on this date.
        stock += deliveries_by_date.get(
            record_date,
            0.0,
        )

        # Subtract consumption.
        stock -= float(
            record.quantity_dispensed
        )

        # Inventory cannot go below zero.
        stock = max(
            0.0,
            stock,
        )

        snapshots.append(
            InventorySnapshot(
                facility_id=facility_id,
                medicine_id=medicine_id,
                timestamp=record_date,
                stock_on_hand=round(
                    stock,
                    2,
                ),
                reorder_point=round(
                    float(reorder_point),
                    2,
                ),
                max_capacity=round(
                    float(max_capacity),
                    2,
                ),
            )
        )

    return snapshots


def _generate_regions(
    region_config: dict,
):
    """
    Convert region configuration into the Region model shape.
    """

    return [
        {
            "id": region_id,
            "name": (
                region_id
                .replace("reg_", "")
                .replace("_", " ")
                .title()
            ),
            "parent_region_id": "",
        }
        for region_id in region_config["region_ids"]
    ]


def _write_csv(
    path: str,
    rows,
) -> None:
    """
    Write dataclasses or dictionaries to CSV.
    """

    if not rows:
        print(
            f"  (skipping {path}, no rows)"
        )
        return

    if is_dataclass(rows[0]):
        records = [
            asdict(row)
            for row in rows
        ]
    else:
        records = [
            dict(row)
            for row in rows
        ]

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(
                records[0].keys()
            ),
        )

        writer.writeheader()
        writer.writerows(records)

    print(
        f"  wrote {len(records)} rows -> {path}"
    )


def _stable_pair_seed(
    facility_id: str,
    medicine_id: str,
) -> int:
    """
    Generate a deterministic seed.

    Do NOT use Python's hash() here because hash randomization means
    hash((facility_id, medicine_id)) can change between processes.
    """

    value = (
        f"{SEED}:{facility_id}:{medicine_id}"
    )

    return sum(
        (index + 1) * ord(char)
        for index, char in enumerate(value)
    ) & 0xFFFFFFFF


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:

    os.makedirs(
        OUT_DIR,
        exist_ok=True,
    )

    print(
        "[1/4] Generating regions, facilities, and medicines..."
    )

    # Generate regions once.
    regions = _generate_regions(
        REGION_CONFIG
    )

    facilities = generate_facilities(
        N_FACILITIES,
        REGION_CONFIG,
        seed=SEED,
    )

    medicines = generate_medicines(
        ESSENTIAL_MEDICINES
    )

    print(
        f"  {len(regions)} regions, "
        f"{len(facilities)} facilities, "
        f"{len(medicines)} medicines"
    )

    # ------------------------------------------------------------------
    # Select explicit demo scenarios.
    # ------------------------------------------------------------------

    facilities_by_region: dict[str, list] = {}

    for facility in facilities:
        facilities_by_region.setdefault(
            str(facility.region_id),
            [],
        ).append(facility)

    region_ids = list(
        REGION_CONFIG["region_ids"]
    )

    scenario_region = region_ids[0]

    scenario_facilities = (
        facilities_by_region
        .get(scenario_region, [])[:3]
    )

    scenario_medicine = medicines[0]

    shock_region = region_ids[1]

    shock_facilities = (
        facilities_by_region
        .get(shock_region, [])[:2]
    )

    shock_medicine = medicines[4]

    delay_region = region_ids[2]

    delay_facilities = (
        facilities_by_region
        .get(delay_region, [])
    )

    if not delay_facilities:
        raise RuntimeError(
            f"No facilities generated for {delay_region}"
        )

    delay_facility = delay_facilities[0]

    delay_medicine = medicines[3]

    scenario_pairs = {
        (
            str(facility.id),
            str(scenario_medicine.id),
        )
        for facility in scenario_facilities
    }

    shock_pairs = {
        (
            str(facility.id),
            str(shock_medicine.id),
        )
        for facility in shock_facilities
    }

    delay_pair = (
        str(delay_facility.id),
        str(delay_medicine.id),
    )

    print(
        "[2/4] Injecting 3 demo scenarios:"
    )

    print(
        f"  (a) slow-building regional shortage: "
        f"region={scenario_region}, "
        f"medicine={scenario_medicine.name}, "
        f"facilities="
        f"{[f.id for f in scenario_facilities]}"
    )

    print(
        f"  (b) sudden-shock outbreak shortage: "
        f"region={shock_region}, "
        f"medicine={shock_medicine.name}, "
        f"facilities="
        f"{[f.id for f in shock_facilities]}"
    )

    print(
        f"  (c) pure supply-side delay: "
        f"facility={delay_facility.id}, "
        f"medicine={delay_medicine.name}"
    )

    # ------------------------------------------------------------------
    # Generate all facility × medicine data.
    # ------------------------------------------------------------------

    print(
        "[3/4] Simulating consumption + replenishment "
        "for every facility x medicine pair..."
    )

    all_consumption = []
    all_orders = []
    all_snapshots = []

    simulation_start_date = (
        datetime.now(
            tz=timezone.utc
        ).date()
        - timedelta(days=SIM_DAYS)
    )

    for facility in facilities:

        for medicine in medicines:

            pair = (
                str(facility.id),
                str(medicine.id),
            )

            pair_seed = _stable_pair_seed(
                pair[0],
                pair[1],
            )

            pair_rng = random.Random(
                pair_seed
            )

            lead_time_dist = dict(
                DEFAULT_LEAD_TIME_DIST
            )

            # ----------------------------------------------------------
            # Scenario A:
            # Slow-building regional shortage.
            # ----------------------------------------------------------

            if pair in scenario_pairs:

                pattern_params = (
                    _base_pattern_params(
                        facility,
                        pair_rng,
                    )
                )

                pattern_params[
                    "trend_pct_per_month"
                ] = 0.12

                pattern_params[
                    "seasonal_amplitude"
                ] = 0.10

            # ----------------------------------------------------------
            # Scenario B:
            # Sudden demand shock.
            # ----------------------------------------------------------

            elif pair in shock_pairs:

                pattern_params = (
                    _base_pattern_params(
                        facility,
                        pair_rng,
                    )
                )

                pattern_params[
                    "shock_events"
                ] = [
                    {
                        "start_day": 90,
                        "duration_days": 21,
                        "multiplier": 3.5,
                    }
                ]

            # ----------------------------------------------------------
            # Scenario C:
            # Supply-side delay.
            # ----------------------------------------------------------

            elif pair == delay_pair:

                pattern_params = (
                    _base_pattern_params(
                        facility,
                        pair_rng,
                    )
                )

                pattern_params[
                    "trend_pct_per_month"
                ] = 0.0

                pattern_params[
                    "seasonal_amplitude"
                ] = 0.05

                lead_time_dist[
                    "delay_prob"
                ] = 0.85

                lead_time_dist[
                    "mean_days"
                ] = 10

            # ----------------------------------------------------------
            # Normal pair.
            # ----------------------------------------------------------

            else:

                pattern_params = (
                    _base_pattern_params(
                        facility,
                        pair_rng,
                    )
                )

            # ----------------------------------------------------------
            # Consumption.
            # ----------------------------------------------------------

            consumption = simulate_consumption(
                facility.id,
                medicine.id,
                SIM_DAYS,
                pattern_params,
                start_date=simulation_start_date,
                seed=pair_seed,
            )

            # ----------------------------------------------------------
            # Replenishment.
            # ----------------------------------------------------------

            avg_daily_use = float(
                pattern_params["base_daily_use"]
            )

            orders = simulate_replenishment(
                facility.id,
                medicine.id,
                SIM_DAYS,
                lead_time_dist,
                avg_daily_use=avg_daily_use,
                start_date=simulation_start_date,
                seed=pair_seed + 1,
            )

            # ----------------------------------------------------------
            # Inventory thresholds.
            # ----------------------------------------------------------

            reorder_point = (
                avg_daily_use
                * (
                    float(lead_time_dist.get("mean_days", 7.0) or 7.0) # type: ignore
                    + SAFETY_BUFFER_DAYS
                )
            )

            max_capacity = (
                reorder_point
                * pair_rng.uniform(
                    *MAX_CAPACITY_MULTIPLIER_RANGE
                )
            )

            # Start with approximately two weeks of stock.
            initial_stock = (
                avg_daily_use * 14
            )

            snapshots = (
                _compute_inventory_snapshots(
                    facility.id,
                    medicine.id,
                    consumption,
                    orders,
                    initial_stock,
                    reorder_point,
                    max_capacity,
                )
            )

            all_consumption.extend(
                consumption
            )

            all_orders.extend(
                orders
            )

            all_snapshots.extend(
                snapshots
            )

    print(
        f"  {len(all_consumption)} consumption records, "
        f"{len(all_orders)} orders, "
        f"{len(all_snapshots)} snapshots"
    )

    # ------------------------------------------------------------------
    # Write output.
    # ------------------------------------------------------------------

    print(
        f"[4/4] Writing CSVs to {OUT_DIR}/ ..."
    )

    _write_csv(
        os.path.join(
            OUT_DIR,
            "regions.csv",
        ),
        regions,
    )

    _write_csv(
        os.path.join(
            OUT_DIR,
            "facilities.csv",
        ),
        facilities,
    )

    _write_csv(
        os.path.join(
            OUT_DIR,
            "medicines.csv",
        ),
        medicines,
    )

    _write_csv(
        os.path.join(
            OUT_DIR,
            "inventory_snapshots.csv",
        ),
        all_snapshots,
    )

    _write_csv(
        os.path.join(
            OUT_DIR,
            "consumption.csv",
        ),
        all_consumption,
    )

    _write_csv(
        os.path.join(
            OUT_DIR,
            "replenishment_orders.csv",
        ),
        all_orders,
    )

    print("Done.")


if __name__ == "__main__":
    main()