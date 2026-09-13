// Chronological feed from GET /alerts (detect_emerging_shortage output).
// Owner: Frontend/Product Lead
export default function AlertsFeed({ alerts }) {
  return (
    <div className="alerts-feed">
      <h2 className="heading-text">Alerts Feed</h2>
      {/* TODO: render alerts list, sorted by regional_risk_score */}
    </div>
  );
}
