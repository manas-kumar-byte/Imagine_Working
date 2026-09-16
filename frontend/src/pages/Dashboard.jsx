import MapView from "../components/MapView"
import AlertsFeed from "../components/AlertsFeed"
import RecommendationPanel from "../components/RecommendationPanel"
import {getFacilities} from "../api/client";
import { getRecommendations, getMedicines, getAlerts, getAllRecommendations } from "../api/client";
import { useState, useEffect } from "react";

// Top-level dashboard: MapView + AlertsFeed + RecommendationPanel.
// Owner: Frontend/Product Lead
export default function Dashboard() {
   const [facilities, setFacilities] = useState([]);
   const [recommendations, setRecomendations] = useState([]);
   const [medicines, setMedicines] = useState([]);
   const [alerts, setAlerts] = useState([]);
   const [rec_loaded, setRecLoaded] = useState(false);
   const [alert_loaded, setAlertLoaded] = useState(false);
  useEffect(() => {
  async function loadDashboardData() {
    try {
      // Start alerts
      getAlerts()
        .then(data => {
          setAlerts(data);
          setAlertLoaded(true);
        })
        .catch(error => {
          console.error("Failed to load alerts:", error);
        });

      // Start recommendations
      getAllRecommendations()
        .then(data => {
          setRecomendations(data);
          setRecLoaded(true);
        })
        .catch(error => {
          console.error("Failed to load recommendations:", error);
        });

      // Start facilities
      getFacilities()
        .then(data => {
          setFacilities(data);
        })
        .catch(error => {
          console.error("Failed to load facilities:", error);
        });

      // Start medicines
      getMedicines()
        .then(data => {
          setMedicines(data);
        })
        .catch(error => {
          console.error("Failed to load medicines:", error);
        });

    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    }
  }

  loadDashboardData();
}, []);
    useEffect(() => {
        async function loadFacilities() {
            const data = await getFacilities();
            setFacilities(data);
        }

        loadFacilities();
    }, []);
    
        
  const sortedRecommendations = [...recommendations]
  .sort((a, b) => b.urgency_score - a.urgency_score);
  return (
    <div className="dashboard">
      {/* TODO: compose MapView, AlertsFeed, RecommendationPanel */}
      <h1 className="heading-text">Dashboard</h1>
      <MapView facilities={facilities}/>
      <div className="alert-n-recommendation">
          <AlertsFeed alerts={alerts} alert_loaded={alert_loaded}/>
          <RecommendationPanel recommendations={sortedRecommendations} rec_loaded={rec_loaded} from="Dashboard"/>
      
      </div>
    </div>
  );
}
