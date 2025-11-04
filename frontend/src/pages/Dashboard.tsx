import { Link } from 'react-router-dom'
import { Plus, Sparkles } from 'lucide-react'
import { useGoals } from '@/api/goals'
import { useAuth } from '@/contexts/AuthContext'
import GoalCard from '@/components/GoalCard'
import LoadingSpinner from '@/components/LoadingSpinner'

const Dashboard = () => {
  const { user } = useAuth()
  const { data: goals, isLoading, error } = useGoals(!!user)

  if (isLoading) return <LoadingSpinner />

  if (error) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center p-8">
        <div className="text-center">
          <p className="text-red-400">Error loading goals. Please try again.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Your Goals</h1>
          <p className="text-gray-400">
            Track and manage your opportunity discovery goals
          </p>
        </div>

        {/* Content */}
        {!goals || goals.length === 0 ? (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-800/50 rounded-2xl mb-6">
              <Sparkles className="w-10 h-10 text-gray-600" />
            </div>
            <h3 className="text-2xl font-semibold mb-3">No goals yet</h3>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              Create your first goal to start discovering relevant opportunities tailored to your needs.
            </p>
            <Link
              to="/goals/new"
              className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white rounded-xl font-medium transition-all duration-200"
            >
              <Plus className="w-5 h-5" />
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
    </div>
  )
}

export default Dashboard
