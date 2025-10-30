import { Outlet, Link, useLocation } from 'react-router-dom'
import { Home, Target, Settings as SettingsIcon } from 'lucide-react'

const Layout = () => {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/dashboard" className="flex items-center">
                <span className="text-2xl font-bold text-primary-600">Genie</span>
              </Link>
              <div className="ml-10 flex items-center space-x-4">
                <Link
                  to="/dashboard"
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/dashboard')
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Home className="w-4 h-4 mr-2" />
                  Dashboard
                </Link>
                <Link
                  to="/goals/new"
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/goals/new')
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Target className="w-4 h-4 mr-2" />
                  New Goal
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <Link
                to="/settings"
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/settings')
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <SettingsIcon className="w-4 h-4 mr-2" />
                Settings
              </Link>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout

