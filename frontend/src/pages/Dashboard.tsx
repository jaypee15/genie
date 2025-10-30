import { Link } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { useGoals } from '@/api/goals'
import { useUser } from '@/hooks/useUser'
import GoalCard from '@/components/GoalCard'
import LoadingSpinner from '@/components/LoadingSpinner'

const Dashboard = () => {
  const { userId } = useUser()
  const { data: goals, isLoading, error } = useGoals(userId || '')

  if (isLoading) return <LoadingSpinner />

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error loading goals. Please try again.</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Your Goals</h1>
          <p className="text-gray-600 mt-2">
            Track and manage your opportunity discovery goals
          </p>
        </div>
        <Link
          to="/goals/new"
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          New Goal
        </Link>
      </div>

      {!goals || goals.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-600 mb-4">
            You haven't created any goals yet.
          </p>
          <Link
            to="/goals/new"
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Your First Goal
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {goals.map((goal) => (
            <GoalCard key={goal.id} goal={goal} />
          ))}
        </div>
      )}
    </div>
  )
}

export default Dashboard

