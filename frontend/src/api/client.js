// Thin wrapper around the backend API contract (see docs/api-contract.md).
// Owner: Frontend/Product Lead
const BASE_URL = "/api";

export async function getFacilities() {
  const res = await fetch(`${BASE_URL}/facilities`);
  return res.json();
}

export async function getFacilityStatus(facilityId, medicineId) {
  const res = await fetch(`${BASE_URL}/facilities/${facilityId}/status?medicine_id=${medicineId}`);
  return res.json();
}

export async function getRegionRisk(regionId, medicineId) {
  const res = await fetch(`${BASE_URL}/regions/${regionId}/risk?medicine_id=${medicineId}`);
  return res.json();
}

export async function getAlerts(medicineId) {
  const url = medicineId ? `${BASE_URL}/alerts?medicine_id=${medicineId}` : `${BASE_URL}/alerts`;
  const res = await fetch(url);
  return res.json();
}

export async function getRecommendations(facilityId, medicineId) {
  const res = await fetch(`${BASE_URL}/recommendations/${facilityId}?medicine_id=${medicineId}`);
  return res.json();
}
