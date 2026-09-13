import MapView from "../components/MapView"
import AlertsFeed from "../components/AlertsFeed"
import RecommendationPanel from "../components/RecommendationPanel"
import {getFacilities} from "../api/client";
import {getRegionRisk} from "../api/client";
import { getRecommendations } from "../api/client";
import { getMedicines } from "../api/client";
import { useState, useEffect } from "react";

// Top-level dashboard: MapView + AlertsFeed + RecommendationPanel.
// Owner: Frontend/Product Lead
export default function Dashboard() {
   const [facilities, setFacilities] = useState([]);
   const [recommendations, setRecomendations] = useState([]);
   const [medicines, setMedicines] = useState([]);
    useEffect(() => {
        async function loadFacilities() {
            const data = await getFacilities();
            setFacilities(data);
        }

        loadFacilities();
    }, []);
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
         // Load recommendations after facilities and medicines are available
        useEffect(() => { 
          async function loadRecommendations() {
             if (facilities.length === 0 || medicines.length === 0) 
              { return; } 
             try { 
              const requests = []; 
              facilities.forEach((facility) => 
                { 
                  medicines.forEach((medicine) => 
                    { 
                      requests.push( getRecommendations( facility.id, medicine.id ) );
                     }); 
                    }); 
                    const results = await Promise.all(requests); 
                    const data = results.flat(); 
                    setRecomendations(data); 
                  } 
                  catch (error) { 
                    console.error( "Failed to load recommendations:", error ); 
                  } 
                } 
                loadRecommendations(); 
              }, [facilities, medicines]);
  const sortedRecommendations = [...recommendations]
  .sort((a, b) => b.urgency_score - a.urgency_score);
    console.log(recommendations);
  return (
    <div className="dashboard">
      {/* TODO: compose MapView, AlertsFeed, RecommendationPanel */}
      <h1 className="heading-text">Dashboard</h1>
      <MapView facilities={facilities}/>
      <div className="alert-n-recommendation">
          <AlertsFeed/>
          <RecommendationPanel recommendations={sortedRecommendations}/>
      </div>
    </div>
  );
}
