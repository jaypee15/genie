import { Goal, GoalStatus } from '@/types'
import { Link } from 'react-router-dom'
import { Target, Pause, Play, Trash2 } from 'lucide-react'
import { useUpdateGoal, useDeleteGoal } from '@/api/goals'

interface GoalCardProps {
  goal: Goal
}

const GoalCard = ({ goal }: GoalCardProps) => {
  const updateGoalMutation = useUpdateGoal()
  const deleteGoalMutation = useDeleteGoal()

  const handleToggleStatus = () => {
    const newStatus =
      goal.status === GoalStatus.ACTIVE ? GoalStatus.PAUSED : GoalStatus.ACTIVE
    updateGoalMutation.mutate({ goalId: goal.id, status: newStatus })
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this goal?')) {
      deleteGoalMutation.mutate(goal.id)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <div className="flex-shrink-0">
            <Target className="w-6 h-6 text-primary-600" />
          </div>
          <div className="flex-1">
            <Link
              to={`/goals/${goal.id}/opportunities`}
              className="text-lg font-semibold text-gray-900 hover:text-primary-600"
            >
              {goal.description}
            </Link>
            <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
              <span className="capitalize">{goal.goal_type}</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                {goal.status}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={handleToggleStatus}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
            title={goal.status === GoalStatus.ACTIVE ? 'Pause' : 'Resume'}
          >
            {goal.status === GoalStatus.ACTIVE ? (
              <Pause className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </button>
          <button
            onClick={handleDelete}
            className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded"
            title="Delete"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default GoalCard

