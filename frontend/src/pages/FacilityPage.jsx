import React from "react";
import { useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import {getMedicines, getRecommendations} from '../api/client.js';
import FacilityDetail from "../components/FacilityDetail";
import RecommendationPanel from "../components/RecommendationPanel.jsx";

//function details(facility) {
//  return <FacilityDetail facilityId=facility["id"] medicineId=/>
//}

// Drill-down page for a single facility.
// Owner: Frontend/Product Lead

function facility_detail(med) {
  return <FacilityDetail medicineId={med['id']}/>;
}
export default function FacilityPage() {
  const { id } = useParams()
  const [medicines, setMedicines] = useState([]);
  const [recommendation, setRecommendations] = useState([]);
  const [rec_loaded, setRecLoaded] = useState(false);
  useEffect(() => 
    { 
      if (medicines.length === 0) { 
        return; 
      } 
      async function loadRecommendations() { 
        try { 
          const requests = []; 
          medicines.forEach((medicine) => { 
            requests.push( getRecommendations( id, medicine.id ) ); 
          }); 
          const results = await Promise.all(requests);
          const data = results.flat(); 
          setRecommendations(data); 
          setRecLoaded(true);
        } 
        catch (error) { 
          console.error( "Failed to load recommendations:", error ); 
        } 
      } 
      loadRecommendations(); 
    }, [id, medicines]);
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
      <div className="facility-details card">
          <h3 className="heading-text">Facility Details</h3>
          {medicines.map(facility_detail)}
      </div>
      <div className="recommendation-panel card">
        <h3 className="heading-text">Recommendation Panel</h3>
        <RecommendationPanel recommendations={recommendation} rec_loaded={rec_loaded}/>
      </div>
    </div>
  );
}
