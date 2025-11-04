import { useParams } from 'react-router-dom'
import { RefreshCw, Sparkles } from 'lucide-react'
import { useGoal } from '@/api/goals'
import { useOpportunities } from '@/api/opportunities'
import { useRefreshGoal } from '@/api/goals'
import OpportunityCard from '@/components/OpportunityCard'
import LoadingSpinner from '@/components/LoadingSpinner'

const OpportunitiesView = () => {
  const { goalId } = useParams<{ goalId: string }>()
  const { data: goal, isLoading: goalLoading } = useGoal(goalId || '')
  const { data: opportunities, isLoading: oppsLoading, refetch } = useOpportunities(
    goalId || ''
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
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center p-8">
        <div className="text-center">
          <p className="text-gray-400">Goal not found.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{goal.description}</h1>
              <p className="text-gray-400">
                {opportunities?.length || 0} opportunities found
              </p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={refreshMutation.isPending}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-gray-800 text-gray-300 rounded-lg transition-all disabled:opacity-50"
            >
              <RefreshCw
                className={`w-4 h-4 ${refreshMutation.isPending ? 'animate-spin' : ''}`}
              />
              {refreshMutation.isPending ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* Content */}
        {!opportunities || opportunities.length === 0 ? (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-800/50 rounded-2xl mb-6">
              <Sparkles className="w-10 h-10 text-gray-600" />
            </div>
            <h3 className="text-2xl font-semibold mb-3">No opportunities yet</h3>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              We're still searching for opportunities that match your goal. This usually takes a few minutes.
            </p>
            <button
              onClick={handleRefresh}
              className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white rounded-xl font-medium transition-all"
            >
              <RefreshCw className="w-4 h-4" />
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
    </div>
  )
}

export default OpportunitiesView
