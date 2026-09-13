import React from "react";
import {getFacilities} from '../api/client.js';
import FacilityDetail from "../components/FacilityDetail";
const facilities = await(getFacilities());

//function details(facility) {
//  return <FacilityDetail facilityId=facility["id"] medicineId=/>
//}

// Drill-down page for a single facility.
// Owner: Frontend/Product Lead
export default function FacilityPage() {
  return (
    <div className="facility-page">
      {/* TODO: render FacilityDetail + RecommendationPanel for this facility */}
      <FacilityDetail/>
    </div>
  );
}
