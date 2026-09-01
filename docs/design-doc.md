# From One Empty Shelf to a Regional Shortage
## System Design & Team Standard (v1.0)

This is the shared contract for the team. Everyone builds against the data model and function signatures below so the pieces snap together on Day 9 instead of Day 10.

---

## 1. Core Idea in One Sentence

**Track stock at every facility → forecast when each one runs dry → detect when many nearby facilities are trending toward stockout at once (that's the "regional shortage" signal) → recommend redistribution or intervention before it happens → show all of it with honest uncertainty, not false confidence.**

---

## 2. System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  A. Data Layer   │────▶│ B. Forecasting    │────▶│ C. Regional Signal │
│ (sim + public    │     │    Engine         │     │    Aggregator      │
│  datasets)       │     │ (per facility-med)│     │ (contagion/spread) │
└─────────────────┘     └──────────────────┘     └─────────┬──────────┘
                                                              │
                          ┌───────────────────────────────────┘
                          ▼
                 ┌──────────────────────┐     ┌─────────────────────┐
                 │ D. Recommendation /   │────▶│ E. Explainability /  │
                 │    Redistribution      │     │    Uncertainty Layer│
                 │    Engine              │     │                      │
                 └──────────┬────────────┘     └─────────┬───────────┘
                            │                              │
                            ▼                              ▼
                 ┌─────────────────────────────────────────────────┐
                 │      F. API Layer (REST, one contract for all)   │
                 └─────────────────────┬─────────────────────────┘
                                        ▼
                 ┌─────────────────────────────────────────────────┐
                 │   G. Dashboard (map, drilldown, alerts, recs)     │
                 └─────────────────────────────────────────────────┘
```

Each box below is one module. Each module owner only needs to know their **inputs and outputs** — not anyone else's internals. That's the point of fixing this now.

---

## 3. Data Model (fix this on Day 1, do not change it after Day 2)

| Entity | Fields |
|---|---|
| **Facility** | `id, name, lat, lon, region_id, type (hospital/clinic/pharmacy/warehouse), tier (capacity size), population_served` |
| **Region** | `id, name, parent_region_id` (lets you roll up clinic → district → state) |
| **Medicine** | `id, name, category, unit (tablets/vials/etc), essential_flag (bool), substitute_ids[]` |
| **InventorySnapshot** | `facility_id, medicine_id, timestamp, stock_on_hand, reorder_point, max_capacity` |
| **ConsumptionRecord** | `facility_id, medicine_id, date, quantity_dispensed` |
| **ReplenishmentOrder** | `id, facility_id, medicine_id, order_date, expected_delivery_date, actual_delivery_date (nullable), quantity, status (pending/in_transit/delivered/delayed)` |

Keep it in flat CSV/JSON tables or SQLite — don't over-engineer the DB for a 10-day hackathon. Optimize for "everyone can `pd.read_csv` this."

---

## 4. Module Contracts

Treat every function below as an interface. Implementation details (ARIMA vs. linear regression vs. a rule-of-thumb) are up to the owner — the **signature is the standard**.

### Module A — Data Simulation / Ingestion (Owner 1)

```
generate_facilities(n, region_config) -> List[Facility]
generate_medicines(essential_list: List[str]) -> List[Medicine]
simulate_consumption(facility_id, medicine_id, days, pattern_params) -> List[ConsumptionRecord]
simulate_replenishment(facility_id, medicine_id, days, lead_time_dist) -> List[ReplenishmentOrder]
load_public_dataset(source_name) -> normalized {facilities, medicines, snapshots, consumption, orders}
```
- `pattern_params` should support: seasonal spikes (e.g. flu season), a slow demand-growth trend, and random "shock" events (e.g. one facility gets a sudden outbreak) — this is what makes the demo's "spreading shortage" visible instead of just noisy static data.
- Deliberately inject 2–3 "shortage scenarios" into the simulated data (one slow-building, one sudden-shock, one supply-side delay) so the demo has a clear story to walk through.

### Module B — Forecasting Engine (Owner 2)

```
compute_consumption_rate(facility_id, medicine_id, window_days) 
  -> { avg_daily_use: float, trend_pct: float, volatility: float }

forecast_days_to_stockout(facility_id, medicine_id) 
  -> { days_remaining: float, low_estimate: float, high_estimate: float, method: str }

classify_stock_status(facility_id, medicine_id) 
  -> { status: "healthy"|"watch"|"critical"|"stockout", risk_score: float (0-1) }
```
- `risk_score` is the number every downstream module keys off — define its meaning once (e.g. `1 - days_remaining/reorder_lead_time`, clipped 0–1) and don't let it silently change.
- `low_estimate`/`high_estimate` is your uncertainty band — this alone can be a judging highlight if you show it honestly instead of a single confident number.

### Module C — Regional Aggregation / Contagion Detection (Owner 2 or 3)

```
aggregate_region_risk(region_id, medicine_id) 
  -> { facilities_at_risk: int, total_facilities: int, pct_at_risk: float, 
       regional_risk_score: float, trend_direction: "rising"|"stable"|"falling" }

detect_emerging_shortage(medicine_id) 
  -> List[{ region_id, regional_risk_score, spread_rate, first_detected_at }]

shortage_propagation_score(region_id, medicine_id) 
  -> { score: float, contributing_factors: List[str] }
```
- This is the module that actually answers the problem statement's core ask ("how does one empty shelf become a regional shortage"). Frame it as: multiple facilities' individual `risk_score` trending up together + shared upstream supplier/warehouse = early regional signal, distinct from one facility just having a bad week.
- Simple but defensible approach: treat facilities as nodes in a graph (edges = shared distributor, or geographic proximity within X km); a shortage is "spreading" if risk_score is rising across a connected cluster, not just one isolated node.

### Module D — Redistribution / Recommendation Engine (Owner 3)

```
find_surplus_facilities(medicine_id, near_facility_id, radius_km) 
  -> List[{ facility_id, surplus_qty, distance_km }]

recommend_redistribution(deficit_facility_id, medicine_id) 
  -> List[{ source_facility_id, quantity, distance_km, urgency_score, feasibility_score }]
  # ranked, highest priority first

recommend_intervention(region_id, medicine_id) 
  -> { action: "redistribute"|"expedite_order"|"emergency_procurement"|"monitor", 
       priority: "low"|"medium"|"high"|"critical", rationale: str }
```
- `urgency_score` should weigh: recipient's `days_remaining`, distance, source's own risk trend (don't recommend draining a facility that's about to need that stock itself).
- `feasibility_score` is where you can add nuance for bonus points: cold-chain requirements, road access, minimum shipment quantities.

### Module E — Explainability / Uncertainty (Owner 3 or 4)

```
confidence_band(forecast_result) -> { level: "low"|"medium"|"high", note: str }
explain_recommendation(recommendation) -> str  # 1-2 sentence plain-language rationale
```
- Judges will remember a system that says *"Facility X is likely to stock out in 6–9 days (medium confidence, based on 14 days of consumption data); nearest facility Y has 40% surplus and is 12km away"* far more than one that just shows a red dot.

### Module F — API Layer (Owner 4)

One thin REST layer wrapping B–E so the frontend never touches raw data:
```
GET /facilities
GET /facilities/{id}/status?medicine_id=
GET /regions/{id}/risk?medicine_id=
GET /alerts                          # currently-flagged emerging shortages
GET /recommendations/{facility_id}
```
Return JSON matching the shapes above exactly — this is the seam that lets frontend and backend work in parallel from Day 2.

### Module G — Dashboard (Owner 5)

- **Map view**: facilities colored by `status`, region shaded by `regional_risk_score` (this is your money shot for the demo).
- **Alerts feed**: chronological list from `detect_emerging_shortage`.
- **Facility drill-down**: stock trend chart + `days_remaining` with confidence band.
- **Recommendation panel**: ranked redistribution suggestions with one-line rationale.

---

## 5. Team Split (5 people)

| Role | Owns | Also does |
|---|---|---|
| **1. Data/Simulation Lead** | Module A, defines the 2–3 demo scenarios | Sources any public dataset (WHO essential medicines list, DHIS2 sample data) |
| **2. Forecasting Engineer** | Module B, C | Picks the "how shortages are forecast" method — keep it simple and explainable over fancy |
| **3. Recommendation Engineer** | Module D, E | Owns the "so what do we do about it" story — this is often the most memorable part in judging |
| **4. Backend/Integration Lead** | Module F, glues A–E together | Owns the data model, resolves schema disputes |
| **5. Frontend/Product Lead** | Module G | Also leads deck + demo video, since they'll know the UI story best |

Two people (2 & 3) can prototype on static CSVs before Module A is even finished — hand them a small hand-written sample dataset on Day 1 so nobody blocks on nobody.

---

## 6. 10-Day Roadmap

| Days | Milestone |
|---|---|
| **1** | Lock data model + function contracts (this doc). Write 20-row sample CSVs by hand so everyone can start immediately. |
| **2–3** | Module A produces full simulated dataset with 3 scenarios. Module B/C/D built against sample data in parallel. |
| **4–5** | Integrate B→C→D pipeline end-to-end on real simulated data. API skeleton (F) up. |
| **6–7** | Frontend (G) wired to API. First full click-through demo. Start deck outline. |
| **8** | Polish: uncertainty displays, explanations, one standout "innovation" feature (see §7). Record raw demo footage. |
| **9** | Finalize deck (format-compliant!), edit demo video, rehearse pitch, monetization/marketing slides. |
| **10** | Buffer day: fix bugs, rehearse timing, submit. |

---

## 7. Mapping to the 6 Judging Pillars

**1. Innovation beyond requirements** — pick 1–2, don't scatter effort:
- Contagion-graph model (shared-supplier or proximity network) for detecting spread, framed like epidemic modeling — a strong, explainable hook.
- Equity-weighted prioritization: don't let recommendation logic silently favor high-volume urban facilities over low-volume rural ones serving vulnerable populations.
- Lightweight "crowd report" channel (SMS/WhatsApp-style mock) for facilities without digital inventory systems — addresses a real low-resource-setting gap.
- Natural-language plain explanations for every alert (Module E) — cheap to build, very demo-able.

**2. Feasibility** — show a real phased rollout: Phase 1 pilot with one district and manual/CSV data entry → Phase 2 integrate with existing systems (DHIS2, mSupply, District Health Information APIs) → Phase 3 state-level → Phase 4 multi-region. Explicitly name who'd need to say yes (district health officer, procurement agency) and what data they'd need to share.

**3. Marketing/Media** — target audience is B2G/B2NGO, not consumers: state/national health departments, NGOs (MSF, Red Cross), UNICEF/WHO supply chain teams, and pharma distributors. Outreach: pilot partnerships with an existing DHIS2-implementing NGO, presence at health-supply-chain conferences, published pilot case study with real (or realistic simulated) impact numbers.

**4. Monetisation** — SaaS licensing to health ministries/NGOs, tiered by number of facilities/regions monitored; grant/donor funding (Gates Foundation, WHO, USAID) for initial deployment since end beneficiaries can't pay; secondary revenue from anonymized demand-signal insights sold to manufacturers/distributors for production planning.

**5. Format adherence** — assign one person (Frontend/Product lead) as format owner: check the mandatory template and video guidelines against the submission spec *before* Day 9, not on Day 10.

**6. Prototype bonus** — make sure the deployed demo (even if simulated data) is actually clickable by a judge, not just a video — host the dashboard somewhere reachable (Vercel/Render/similar) with the API live.

---

## 8. Naming Conventions (so PRs don't fight)

- IDs: lowercase snake_case strings, e.g. `fac_0012`, `med_amoxicillin`.
- Dates: ISO 8601 (`YYYY-MM-DD`).
- Risk scores: always 0.0–1.0 float, never raw counts.
- Status enums: exactly the strings listed above — no synonyms (`"critical"` not `"crit"`/`"severe"`).
