import { Message, MessageRole } from '@/types/chat'
import { Sparkles, User } from 'lucide-react'
import QuestionForm from './QuestionForm'

interface ChatMessageProps {
  message: Message
  onAnswerQuestions?: (answers: Array<{ question: string; answer: string }>) => void
  isProcessing?: boolean
}

const ChatMessage = ({ message, onAnswerQuestions, isProcessing }: ChatMessageProps) => {
  const isUser = message.role === MessageRole.USER
  const isStatus = message.metadata?.type === 'status'

  if (isStatus) {
    return (
      <div className="flex justify-center py-2">
        <div className="px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-sm text-cyan-300">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
        isUser ? 'bg-gray-700' : 'bg-cyan-500/10'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-gray-300" />
        ) : (
          <Sparkles className="w-5 h-5 text-cyan-400" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
        <div
          className={`inline-block max-w-[80%] px-4 py-3 rounded-xl ${
            isUser
              ? 'bg-cyan-500 text-white'
              : 'bg-[#1A1A1A] border border-gray-800 text-white'
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>

          {/* Render Questions Form */}
          {message.metadata?.type === 'questions' &&
            message.metadata.questions &&
            onAnswerQuestions && (
              <div className="mt-4">
                <QuestionForm
                  questions={message.metadata.questions}
                  onSubmit={onAnswerQuestions}
                  disabled={isProcessing}
                />
              </div>
            )}

          {/* Completion with Goal Link */}
          {message.metadata?.type === 'completion' && message.metadata.goal_id && (
            <a
              href={`/goals/${message.metadata.goal_id}/opportunities`}
              className="mt-3 inline-flex items-center text-sm text-cyan-300 hover:text-cyan-200 underline"
            >
              View Opportunities →
            </a>
          )}
        </div>

        <div className="text-xs text-gray-500 mt-1 px-1">
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage

