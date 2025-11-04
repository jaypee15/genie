import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import { useCreateGoal } from '@/api/goals'
import { useAuth } from '@/contexts/AuthContext'

const GoalCreate = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth()
  const [description, setDescription] = useState('')
  const createGoalMutation = useCreateGoal()

  useEffect(() => {
    const initialGoal = location.state?.initialGoal
    if (initialGoal) {
      setDescription(initialGoal)
    }
  }, [location])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!user || !description.trim()) return

    createGoalMutation.mutate(
      {
        goalData: { description },
      },
      {
        onSuccess: (goal) => {
          navigate(`/goals/${goal.id}/opportunities`)
        },
      }
    )
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-cyan-500/10 rounded-xl flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-cyan-400" />
            </div>
            <h1 className="text-3xl font-bold">Create a New Goal</h1>
          </div>
          <p className="text-gray-400 text-lg">
            Describe what kind of opportunities you're looking for. Be as specific as
            possible - Genie will help clarify and find the best matches.
          </p>
        </div>

        {/* Form */}
        <div className="bg-[#1A1A1A] border border-gray-800 rounded-2xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="description"
                className="block text-sm font-medium text-gray-300 mb-3"
              >
                What are you looking for?
              </label>
              <textarea
                id="description"
                rows={8}
                className="w-full px-6 py-4 bg-[#0A0A0A] border border-gray-800 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all resize-none"
                placeholder="e.g., I want to find remote software engineering positions at early-stage startups working on AI/ML products..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                autoFocus
                required
              />
            </div>

            <div className="bg-cyan-500/5 border border-cyan-500/20 rounded-xl p-6">
              <p className="text-sm text-cyan-300 font-medium mb-3">
                💡 Pro tip: Include details like
              </p>
              <ul className="text-sm text-gray-400 space-y-2 ml-4">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Type of opportunity (job, speaking, event, grant)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Your area of expertise or interest</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Location preferences or remote work</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Compensation requirements</span>
                </li>
              </ul>
            </div>

            <div className="flex justify-end gap-4 pt-4">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-gray-800 text-gray-300 rounded-xl font-medium transition-all duration-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createGoalMutation.isPending || !description.trim()}
                className="px-8 py-3 bg-cyan-500 hover:bg-cyan-600 text-white rounded-xl font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {createGoalMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Create Goal
                  </>
                )}
              </button>
            </div>
          </form>

          {createGoalMutation.isError && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
              <p className="text-sm text-red-400">
                Failed to create goal. Please try again.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default GoalCreate
