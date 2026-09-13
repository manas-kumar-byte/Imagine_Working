import React from 'react';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Scatter } from 'react-chartjs-2';

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

export const options = {
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};

export const data = {
  datasets: [
    {
      label: 'Dataset 1',
      data: [
        { x: -10, y: 0 },
        { x: 0, y: 10 },
        { x: 10, y: 5 },
        { x: 20, y: 15 },
      ],
      backgroundColor: 'rgba(255, 99, 132, 1)',
      pointRadius: 10,       // Sets the normal dot size (default is 3)
      pointHoverRadius: 15
    },
  ],
};

// Facilities colored by status; regions shaded by regional_risk_score.
// This is the demo's money shot — prioritize this component's polish.
// Owner: Frontend/Product Lead
export default function MapView({ facilities, regionRisk }) {
  return (
    <div className="map-view card">
      <h2 className="heading-text">Map View</h2>
      <Scatter options={options} data={data} />;
      {/* TODO: plug in a map lib (e.g. Leaflet/Mapbox) or a simple SVG scatter for the hackathon */}
    </div>
  );
}
