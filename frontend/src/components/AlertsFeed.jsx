// Chronological feed from GET /alerts (detect_emerging_shortage output).
// Owner: Frontend/Product Lead
export default function AlertsFeed({ alerts }) {
  return (
    <div className="alerts-feed card">
      <h2 className="heading-text">Alerts Feed</h2>
      {/* TODO: render alerts list, sorted by regional_risk_score */}
      {alerts.map((alert, index) => (
        <div key="index" className="alert-item">
          <p>Region: {alert.region_id}</p>
          <p>Medicine: {alert.medicine_id}</p>
          <p>Risk: {alert.regional_risk_score}</p>
          <p>Spread: {alert.spread_rate}</p>
        </div>
      ))}
    </div>
  );
}
