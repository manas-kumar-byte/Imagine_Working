import React from "react";
import {getFacilityStatus} from "../api/client";
// Stock trend chart + days_remaining with confidence band.
// Owner: Frontend/Product Lead
export default function FacilityDetail({ facilityId, medicineId }) {
  return (
    <div className="facility-detail">
      <p>
      {/* TODO: fetch getFacilityStatus, render chart + confidence band */
      getFacilityStatus(facilityId, medicineId)["status"]}
      </p>
    </div>
  );
}
