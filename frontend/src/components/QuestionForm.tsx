import { useState } from 'react'
import { Question } from '@/types/chat'
import { Sparkles } from 'lucide-react'

interface QuestionFormProps {
  questions: Question[]
  onSubmit: (answers: Array<{ question: string; answer: string }>) => void
  disabled?: boolean
}

const QuestionForm = ({ questions, onSubmit, disabled }: QuestionFormProps) => {
  const [answers, setAnswers] = useState<Record<number, string>>({})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const formattedAnswers = questions.map((q, index) => ({
      question: q.question,
      answer: answers[index] || '',
    }))

    onSubmit(formattedAnswers)
  }

  const allAnswered = questions.every((_, index) => answers[index]?.trim())

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mt-4 pt-4 border-t border-gray-700">
      {questions.map((question, index) => (
        <div key={index}>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {question.question}
          </label>
          {question.type === 'select' && question.options ? (
            <select
              value={answers[index] || ''}
              onChange={(e) => setAnswers({ ...answers, [index]: e.target.value })}
              className="w-full px-3 py-2 bg-[#0A0A0A] border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
              disabled={disabled}
            >
              <option value="">Select an option</option>
              {question.options.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          ) : question.type === 'number' ? (
            <input
              type="number"
              value={answers[index] || ''}
              onChange={(e) => setAnswers({ ...answers, [index]: e.target.value })}
              className="w-full px-3 py-2 bg-[#0A0A0A] border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
              disabled={disabled}
            />
          ) : (
            <input
              type="text"
              value={answers[index] || ''}
              onChange={(e) => setAnswers({ ...answers, [index]: e.target.value })}
              className="w-full px-3 py-2 bg-[#0A0A0A] border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
              placeholder="Your answer..."
              disabled={disabled}
            />
          )}
        </div>
      ))}

      <button
        type="submit"
        disabled={!allAnswered || disabled}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Sparkles className="w-4 h-4" />
        Submit Answers
      </button>
    </form>
  )
}

export default QuestionForm

