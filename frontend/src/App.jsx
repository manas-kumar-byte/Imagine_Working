import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import FacilityPage from "./pages/FacilityPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/facility/:id" element={<FacilityPage />} />
      </Routes>
    </BrowserRouter>
  );
}
