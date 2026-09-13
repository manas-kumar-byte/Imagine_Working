import React from "react";
import { useParams } from 'react-router-dom';
import {getFacilityStatus} from "../api/client";
// Stock trend chart + days_remaining with confidence band.
// Owner: Frontend/Product Lead

export default function FacilityDetail({ facilityId, medicineId }) {
  const { id } = useParams()
  //const status = await(getFacilityStatus(id, "med_paracetamol"))['status'];
  return (
    <div className="facility-detail card">
      <p>
      {/* TODO: fetch getFacilityStatus, render chart + confidence band */}
      
      </p>
    </div>
  );
}
