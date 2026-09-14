import React from "react";
import { useState, useEffect } from "react";
import {getFacilities, getMedicines} from '../api/client.js';
import FacilityDetail from "../components/FacilityDetail";

//function details(facility) {
//  return <FacilityDetail facilityId=facility["id"] medicineId=/>
//}

// Drill-down page for a single facility.
// Owner: Frontend/Product Lead

function facility_detail(med) {
  return <FacilityDetail medicineId={med['id']}/>;
}
export default function FacilityPage() {
  const [medicines, setMedicines] = useState([]);
  useEffect(() => 
      { 
        async function loadMedicines() 
        { try 
          { 
            const data = await getMedicines(); 
            setMedicines(data); 
          } 
          catch (error) 
          { 
            console.error("Failed to load medicines:", error);
           } 
          } 
          loadMedicines(); 
        }, []);
  return (
    <div className="facility-page">
      {/* TODO: render FacilityDetail + RecommendationPanel for this facility */}
      {medicines.map(facility_detail)};
    </div>
  );
}
