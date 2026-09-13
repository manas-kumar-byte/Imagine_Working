import MapView from "../components/MapView"
import AlertsFeed from "../components/AlertsFeed"
import RecommendationPanel from "../components/RecommendationPanel"

// Top-level dashboard: MapView + AlertsFeed + RecommendationPanel.
// Owner: Frontend/Product Lead
export default function Dashboard() {
  return (
    <div className="dashboard">
      {/* TODO: compose MapView, AlertsFeed, RecommendationPanel */}
      <h1 className="heading-text">Dashboard</h1>
      <MapView/>
      <div className="alert-n-recommendation">
          <AlertsFeed/>
          <RecommendationPanel/>
      </div>
    </div>
  );
}
