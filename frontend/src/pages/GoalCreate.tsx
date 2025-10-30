import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Target } from 'lucide-react'
import { useCreateGoal } from '@/api/goals'
import { useUser } from '@/hooks/useUser'

const GoalCreate = () => {
  const navigate = useNavigate()
  const { userId } = useUser()
  const [description, setDescription] = useState('')
  const createGoalMutation = useCreateGoal()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!userId || !description.trim()) return

    createGoalMutation.mutate(
      {
        goalData: { description },
        userId,
      },
      {
        onSuccess: (goal) => {
          navigate(`/goals/${goal.id}/opportunities`)
        },
      }
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow p-8">
        <div className="flex items-center mb-6">
          <Target className="w-8 h-8 text-primary-600 mr-3" />
          <h1 className="text-2xl font-bold text-gray-900">Create a New Goal</h1>
        </div>

        <p className="text-gray-600 mb-6">
          Describe what kind of opportunities you're looking for. Be as specific as
          possible - Genie will help clarify and find the best matches.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              What are you looking for?
            </label>
            <textarea
              id="description"
              rows={6}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="e.g., I want to become a public speaker on sustainability and green technology..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              <strong>Pro tip:</strong> Include details like:
            </p>
            <ul className="mt-2 text-sm text-blue-700 list-disc list-inside space-y-1">
              <li>Type of opportunity (job, speaking, event, grant)</li>
              <li>Your area of expertise or interest</li>
              <li>Location preferences or remote work</li>
              <li>Compensation requirements</li>
            </ul>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createGoalMutation.isPending || !description.trim()}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createGoalMutation.isPending ? 'Creating...' : 'Create Goal'}
            </button>
          </div>
        </form>

        {createGoalMutation.isError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">
              Failed to create goal. Please try again.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default GoalCreate

