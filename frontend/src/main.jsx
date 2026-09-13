import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/global.css";
import {getFacilities} from '/home/ritwikyadav/Imagine_Working/frontend/src/api/client.js';

const facilities = await(getFacilities());
console.log(facilities)

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
