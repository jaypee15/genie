import { Opportunity } from '@/types'
import { ExternalLink, MapPin, DollarSign, ThumbsUp, ThumbsDown } from 'lucide-react'
import { useState } from 'react'
import { useCreateFeedback } from '@/api/feedback'
import { useAuth } from '@/contexts/AuthContext'

interface OpportunityCardProps {
  opportunity: Opportunity
  goalId: string
}

const OpportunityCard = ({ opportunity, goalId }: OpportunityCardProps) => {
  const { user } = useAuth()
  const [feedbackGiven, setFeedbackGiven] = useState(false)
  const createFeedbackMutation = useCreateFeedback()

  const handleFeedback = (rating: number) => {
    if (!user) return

    createFeedbackMutation.mutate(
      {
        feedbackData: {
          opportunity_id: opportunity.id,
          goal_id: goalId,
          rating,
        },
      },
      {
        onSuccess: () => setFeedbackGiven(true),
      }
    )
  }

  return (
    <div className="bg-[#1A1A1A] border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <h3 className="text-lg font-semibold text-white">
              {opportunity.title}
            </h3>
            {opportunity.relevance_score && (
              <span className="ml-2 px-3 py-1 text-xs font-medium bg-green-500/10 text-green-400 rounded-full">
                {Math.round(opportunity.relevance_score * 100)}% match
              </span>
            )}
          </div>

          {opportunity.description && (
            <p className="mt-2 text-sm text-gray-400 line-clamp-3">
              {opportunity.description}
            </p>
          )}

          <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
            <span className="px-3 py-1 bg-cyan-500/10 text-cyan-400 rounded-full text-xs font-medium">
              {opportunity.source_name}
            </span>

            {opportunity.location && (
              <span className="flex items-center text-gray-400">
                <MapPin className="w-4 h-4 mr-1.5" />
                {opportunity.location}
              </span>
            )}

            {opportunity.remote && (
              <span className="px-3 py-1 bg-purple-500/10 text-purple-400 rounded-full text-xs font-medium">
                Remote
              </span>
            )}

            {opportunity.compensation && (
              <span className="flex items-center text-gray-400">
                <DollarSign className="w-4 h-4 mr-1" />
                Paid
              </span>
            )}
          </div>

          {opportunity.tags && opportunity.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {opportunity.tags.slice(0, 5).map((tag, index) => (
                <span
                  key={index}
                  className="text-xs px-3 py-1 bg-gray-800 text-gray-300 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 flex items-center justify-between pt-4 border-t border-gray-800">
        <a
          href={opportunity.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm font-medium text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          View Original
          <ExternalLink className="w-4 h-4" />
        </a>

        {!feedbackGiven ? (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 mr-2">Was this helpful?</span>
            <button
              onClick={() => handleFeedback(5)}
              className="p-2 text-gray-400 hover:text-green-400 hover:bg-green-500/10 rounded-lg transition-all"
              title="Relevant"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleFeedback(1)}
              className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
              title="Not relevant"
            >
              <ThumbsDown className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <span className="text-sm text-gray-500">Thanks for your feedback!</span>
        )}
      </div>
    </div>
  )
}

export default OpportunityCard
