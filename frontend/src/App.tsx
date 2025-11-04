import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import GoalCreate from './pages/GoalCreate'
import OpportunitiesView from './pages/OpportunitiesView'
import Settings from './pages/Settings'
import ChatView from './pages/ChatView'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './contexts/AuthContext'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/chat/:conversationId"
              element={
                <ProtectedRoute>
                  <ChatView />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/goals/new"
              element={
                <ProtectedRoute>
                  <GoalCreate />
                </ProtectedRoute>
              }
            />
            <Route
              path="/goals/:goalId/opportunities"
              element={
                <ProtectedRoute>
                  <OpportunitiesView />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
