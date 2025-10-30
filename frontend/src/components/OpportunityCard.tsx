import { Opportunity } from '@/types'
import { ExternalLink, MapPin, DollarSign, ThumbsUp, ThumbsDown } from 'lucide-react'
import { useState } from 'react'
import { useCreateFeedback } from '@/api/feedback'
import { useUser } from '@/hooks/useUser'

interface OpportunityCardProps {
  opportunity: Opportunity
  goalId: string
}

const OpportunityCard = ({ opportunity, goalId }: OpportunityCardProps) => {
  const { userId } = useUser()
  const [feedbackGiven, setFeedbackGiven] = useState(false)
  const createFeedbackMutation = useCreateFeedback()

  const handleFeedback = (rating: number) => {
    if (!userId) return

    createFeedbackMutation.mutate(
      {
        feedbackData: {
          opportunity_id: opportunity.id,
          goal_id: goalId,
          rating,
        },
        userId,
      },
      {
        onSuccess: () => setFeedbackGiven(true),
      }
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              {opportunity.title}
            </h3>
            {opportunity.relevance_score && (
              <span className="ml-2 px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                {Math.round(opportunity.relevance_score * 100)}% match
              </span>
            )}
          </div>

          {opportunity.description && (
            <p className="mt-2 text-sm text-gray-600 line-clamp-3">
              {opportunity.description}
            </p>
          )}

          <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-gray-500">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {opportunity.source_name}
            </span>

            {opportunity.location && (
              <span className="flex items-center">
                <MapPin className="w-4 h-4 mr-1" />
                {opportunity.location}
              </span>
            )}

            {opportunity.remote && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                Remote
              </span>
            )}

            {opportunity.compensation && (
              <span className="flex items-center">
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
                  className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between pt-4 border-t">
        <a
          href={opportunity.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-700"
        >
          View Original
          <ExternalLink className="w-4 h-4 ml-1" />
        </a>

        {!feedbackGiven ? (
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleFeedback(5)}
              className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
              title="Relevant"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleFeedback(1)}
              className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
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

