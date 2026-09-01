# API Contract (frozen — see design-doc.md Module F)

| Endpoint | Returns |
|---|---|
| `GET /facilities` | `List[Facility]` |
| `GET /facilities/{id}/status?medicine_id=` | `FacilityStatusResponse` |
| `GET /regions/{id}/risk?medicine_id=` | `RegionRiskResponse` |
| `GET /alerts?medicine_id=` (optional) | `List[AlertResponse]` |
| `GET /recommendations/{facility_id}?medicine_id=` | `List[RecommendationResponse]` |

Response shapes are defined in `backend/api/schemas.py`. Any change there is a breaking change for the frontend — flag it in the team channel before merging.
