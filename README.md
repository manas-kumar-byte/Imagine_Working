<<<<<<< HEAD
# Shortage Radar
### From One Empty Shelf to a Regional Shortage — Hackathon Project

## Folder Map

| Folder | Owner | Maps to |
|---|---|---|
| `backend/data_sim/` | Data/Simulation Lead | Module A |
| `backend/forecasting/`, `backend/regional/` | Forecasting Engineer | Module B, C |
| `backend/recommendation/`, `backend/explainability/` | Recommendation Engineer | Module D, E |
| `backend/api/`, `backend/db/` | Backend/Integration Lead | Module F |
| `frontend/` | Frontend/Product Lead | Module G |
| `docs/` | Everyone | Design doc, API contract, deck outline |

## Quickstart

```bash
# backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r ../requirements.txt
python -m scripts.seed_data          # generates data/simulated/*.csv
uvicorn api.main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev
```

## Rules of the Road
1. Don't change a function's return shape without pinging the whole team — see `docs/design-doc.md` for the frozen contracts.
2. All cross-module data flows through `backend/db/store.py`. No module reaches into another module's files directly.
3. IDs are snake_case strings (`fac_0012`), dates are ISO 8601, risk scores are floats 0.0–1.0, status enums are exactly `healthy|watch|critical|stockout`.
=======
# APP-AF
>>>>>>> 83ba08b6d3514778cc37d8006ce300bc3d740151
