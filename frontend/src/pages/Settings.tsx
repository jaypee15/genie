import { useAuth } from '@/contexts/AuthContext'
import { User, Bell, Mail } from 'lucide-react'

const Settings = () => {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <div className="space-y-6">
          <div className="bg-[#1A1A1A] border border-gray-800 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-cyan-500/10 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-cyan-400" />
              </div>
              <h2 className="text-xl font-semibold">Account Information</h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  <Mail className="w-4 h-4 inline mr-2" />
                  Email
                </label>
                <p className="text-sm text-gray-300 bg-[#0A0A0A] px-4 py-3 rounded-lg border border-gray-800">
                  {user?.email || 'Not available'}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  User ID
                </label>
                <p className="text-sm text-gray-300 font-mono bg-[#0A0A0A] px-4 py-3 rounded-lg border border-gray-800">
                  {user?.id || 'Not available'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#1A1A1A] border border-gray-800 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
                <Bell className="w-5 h-5 text-purple-400" />
              </div>
              <h2 className="text-xl font-semibold">Notification Preferences</h2>
            </div>
            <p className="text-gray-400">
              Notification settings will be available in a future update.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
