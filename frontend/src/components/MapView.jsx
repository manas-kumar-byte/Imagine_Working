// Facilities colored by status; regions shaded by regional_risk_score.
// This is the demo's money shot — prioritize this component's polish.
// Owner: Frontend/Product Lead
export default function MapView({ facilities, regionRisk }) {
  return (
    <div className="map-view">
      <h2 className="heading-text">Map View</h2>
      {/* TODO: plug in a map lib (e.g. Leaflet/Mapbox) or a simple SVG scatter for the hackathon */}
    </div>
  );
}
