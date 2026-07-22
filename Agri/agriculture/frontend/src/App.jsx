import { Navigate, Route, Routes } from 'react-router-dom'
import AIChat from './components/AIChat.jsx'
import CropSuggestion from './components/CropSuggestion.jsx'
import Dashboard from './components/Dashboard.jsx'
import HealthUpdates from './components/HealthUpdates.jsx'
import IoTSimulation from './components/IoTSimulation.jsx'
import NDVIAnalysis from './components/NDVIAnalysis.jsx'
import DashboardLayout from './layouts/DashboardLayout.jsx'
import DiseaseDetectionPage from './pages/DiseaseDetectionPage.jsx'
import LandingPage from './LandingPage.jsx'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route element={<DashboardLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/ndvi-analysis" element={<NDVIAnalysis />} />
        <Route path="/crop-suggestion" element={<CropSuggestion />} />
        <Route path="/disease-detection" element={<DiseaseDetectionPage />} />
        <Route path="/ai-chat" element={<AIChat />} />
        <Route path="/health-updates" element={<HealthUpdates />} />
        <Route path="/iot-simulation" element={<IoTSimulation />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
