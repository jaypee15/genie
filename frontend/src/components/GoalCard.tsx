import { Goal, GoalStatus } from '@/types'
import { Link } from 'react-router-dom'
import { Sparkles, Pause, Play, Trash2, ArrowRight } from 'lucide-react'
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
    <div className="bg-[#1A1A1A] border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all group">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <div className="w-10 h-10 bg-cyan-500/10 rounded-lg flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="flex-1 min-w-0">
            <Link
              to={`/goals/${goal.id}/opportunities`}
              className="text-lg font-semibold text-white hover:text-cyan-400 transition-colors line-clamp-2 flex items-center gap-2 group"
            >
              <span>{goal.description}</span>
              <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>
            <div className="mt-3 flex items-center gap-3 text-sm">
              <span className="px-3 py-1 bg-gray-800 text-gray-300 rounded-full capitalize">
                {goal.goal_type}
              </span>
              <span
                className={`px-3 py-1 rounded-full font-medium ${
                  goal.status === GoalStatus.ACTIVE
                    ? 'bg-green-500/10 text-green-400'
                    : 'bg-gray-800 text-gray-400'
                }`}
              >
                {goal.status === GoalStatus.ACTIVE ? '● Active' : '○ Paused'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2 ml-4 flex-shrink-0">
          <button
            onClick={handleToggleStatus}
            className="p-2.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all"
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
            className="p-2.5 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
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
