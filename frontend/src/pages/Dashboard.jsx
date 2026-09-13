import MapView from "../components/MapView"
import AlertsFeed from "../components/AlertsFeed"
import RecommendationPanel from "../components/RecommendationPanel"
import {getFacilities} from "../api/client";
import {getRegionRisk} from "../api/client";
import { useState, useEffect } from "react";

// Top-level dashboard: MapView + AlertsFeed + RecommendationPanel.
// Owner: Frontend/Product Lead
export default function Dashboard() {
   const [facilities, setFacilities] = useState([]);

    useEffect(() => {
        async function loadFacilities() {
            const data = await getFacilities();
            setFacilities(data);
        }

        loadFacilities();
    }, []);
  return (
    <div className="dashboard">
      {/* TODO: compose MapView, AlertsFeed, RecommendationPanel */}
      <h1 className="heading-text">Dashboard</h1>
      <MapView facilities={facilities}/>
      <div className="alert-n-recommendation">
          <AlertsFeed/>
          <RecommendationPanel/>
      </div>
    </div>
  );
}
