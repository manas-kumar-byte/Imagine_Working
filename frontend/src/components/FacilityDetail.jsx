import React, { useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import {getFacilityStatus} from "../api/client";
// Stock trend chart + days_remaining with confidence band.
// Owner: Frontend/Product Lead

export default function FacilityDetail({ facilityId, medicineId }) {
  const { id } = useParams()
  const [status, setStatus] = useState([])
  useEffect(() => {
          async function loadStatus() {
              const data = await getFacilityStatus(id, medicineId);
              setStatus(data);
          }
  
          loadStatus();
      }, []);

  //const status = await(getFacilityStatus(id, "med_paracetamol"))['status'];
  return (
    <div className="facility-detail card">
      <p>
      {/* TODO: fetch getFacilityStatus, render chart + confidence band */}
      medicine_id: {status['medicine_id']}
      </p>
      <p>
        Status: {status['status']}
      </p>
      <p>
        Confidence Band: {status['confidence_level']}
      </p>
    </div>
  );
}
