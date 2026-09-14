// Ranked redistribution suggestions with one-line rationale (explain_recommendation).
// Owner: Frontend/Product Lead

export default function RecommendationPanel({ recommendations, rec_loaded }) {

  return (
    <div className="recommendation-panel card">
      <h2 className="heading-text">Recommendation Panel</h2>
      

      {rec_loaded===true? (recommendations.length === 0 ? (
        <p>No recommendations</p>
      ) : (
        <div className="recommendation-list">
          {recommendations.map((recommendation, index) => (

            <div
              className="recommendation-item card"
              key={recommendation.id ?? index}
            >

              <h3>
                Recommendation #{index + 1}
              </h3>


              <p>
                {recommendation.rationale}
              </p>

              {recommendation.score !== undefined && (
                <p>
                  Score: {recommendation.score}
                </p>
              )}

            </div>

          ))}

        </div>
      )):(
        <p>Loading...</p>
      )}

    </div>
  );
}
