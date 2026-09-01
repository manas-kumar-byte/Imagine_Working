"""Pydantic response models — must mirror the TypedDicts in the forecasting/
regional/recommendation modules exactly. This is what the frontend codes
against, so treat changes here as breaking changes for Module G.
Owner: Backend/Integration Lead
"""
from pydantic import BaseModel
from typing import List, Optional


class FacilityStatusResponse(BaseModel):
    facility_id: str
    medicine_id: str
    status: str
    risk_score: float
    days_remaining: float
    low_estimate: float
    high_estimate: float
    confidence_level: str


class RegionRiskResponse(BaseModel):
    region_id: str
    medicine_id: str
    facilities_at_risk: int
    total_facilities: int
    pct_at_risk: float
    regional_risk_score: float
    trend_direction: str


class AlertResponse(BaseModel):
    region_id: str
    medicine_id: str
    regional_risk_score: float
    spread_rate: float
    first_detected_at: str


class RecommendationResponse(BaseModel):
    source_facility_id: str
    quantity: float
    distance_km: float
    urgency_score: float
    feasibility_score: float
    rationale: str
