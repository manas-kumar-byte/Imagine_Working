# Shortage Radar

### From One Empty Shelf to a Regional Shortage — Hackathon Project

Track stock at every facility → forecast when each one runs dry → detect when
many nearby facilities are trending toward stockout → recommend redistribution
or intervention before it happens → show all of it with honest uncertainty.

## Folder Map

| Folder | Owner | Maps to |
|---|---|---|
| `backend/data_sim/` | Data/Simulation Lead | Module A |
| `backend/forecasting/`, `backend/regional/` | Forecasting Engineer | Module B, C |
| `backend/recommendation/`, `backend/explainability/` | Recommendation Engineer | Module D, E |
| `backend/api/`, `backend/db/` | Backend/Integration Lead | Module F |
| `frontend/` | Frontend/Product Lead | Module G |
| `docs/` | Everyone | Design docs |

## Quickstart

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python -m scripts.seed_data

uvicorn backend.api.main:app --reload --port 8000