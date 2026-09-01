"""FastAPI app entrypoint. Wires up all route modules.
Owner: Backend/Integration Lead

Run with: uvicorn backend.api.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import facilities, regions, alerts, recommendations

app = FastAPI(title="Shortage Radar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(facilities.router)
app.include_router(regions.router)
app.include_router(alerts.router)
app.include_router(recommendations.router)


@app.get("/health")
def health():
    return {"status": "ok"}
