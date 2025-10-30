import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import GoalCreate from './pages/GoalCreate'
import OpportunitiesView from './pages/OpportunitiesView'
import Settings from './pages/Settings'
import Layout from './components/Layout'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/goals/new" element={<GoalCreate />} />
          <Route path="/goals/:goalId/opportunities" element={<OpportunitiesView />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App

