import { useParams } from 'react-router-dom'
import { RefreshCw } from 'lucide-react'
import { useGoal } from '@/api/goals'
import { useOpportunities } from '@/api/opportunities'
import { useRefreshGoal } from '@/api/goals'
import { useUser } from '@/hooks/useUser'
import OpportunityCard from '@/components/OpportunityCard'
import LoadingSpinner from '@/components/LoadingSpinner'

const OpportunitiesView = () => {
  const { goalId } = useParams<{ goalId: string }>()
  const { userId } = useUser()
  const { data: goal, isLoading: goalLoading } = useGoal(goalId || '')
  const { data: opportunities, isLoading: oppsLoading, refetch } = useOpportunities(
    goalId || '',
    userId || ''
  )
  const refreshMutation = useRefreshGoal()

  const handleRefresh = () => {
    if (!goalId) return
    refreshMutation.mutate(goalId, {
      onSuccess: () => {
        setTimeout(() => refetch(), 2000)
      },
    })
  }

  if (goalLoading || oppsLoading) return <LoadingSpinner />

  if (!goal) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Goal not found.</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{goal.description}</h1>
            <p className="text-gray-600 mt-2">
              {opportunities?.length || 0} opportunities found
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshMutation.isPending}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw
              className={`w-4 h-4 mr-2 ${refreshMutation.isPending ? 'animate-spin' : ''}`}
            />
            {refreshMutation.isPending ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {!opportunities || opportunities.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-600 mb-4">
            No opportunities found yet. We're still searching...
          </p>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Search Now
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {opportunities.map((opportunity) => (
            <OpportunityCard
              key={opportunity.id}
              opportunity={opportunity}
              goalId={goalId || ''}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default OpportunitiesView

