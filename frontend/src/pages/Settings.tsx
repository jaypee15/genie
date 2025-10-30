import { useUser } from '@/hooks/useUser'

const Settings = () => {
  const { userId } = useUser()

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Account Information</h2>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              User ID
            </label>
            <p className="mt-1 text-sm text-gray-600 font-mono">{userId}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Notification Preferences</h2>
        <p className="text-gray-600">
          Notification settings will be available in a future update.
        </p>
      </div>
    </div>
  )
}

export default Settings

