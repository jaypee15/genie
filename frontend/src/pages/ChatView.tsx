import { useParams } from 'react-router-dom'
import { useRef, useEffect } from 'react'
import { Sparkles } from 'lucide-react'
import { useConversation, useAnswerQuestions } from '@/api/chat'
import { useAbly } from '@/hooks/useAbly'
import ChatMessage from '@/components/ChatMessage'
import ChatInput from '@/components/ChatInput'
import LoadingSpinner from '@/components/LoadingSpinner'

const ChatView = () => {
  const { conversationId } = useParams<{ conversationId: string }>()
  const { data: conversation, isLoading } = useConversation(conversationId || '')
  const { messages: wsMessages, isConnected } = useAbly(conversationId || null)
  const answerQuestions = useAnswerQuestions()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const allMessages = [...(conversation?.messages || []), ...wsMessages]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [allMessages])

  const handleAnswerQuestions = async (answers: Array<{ question: string; answer: string }>) => {
    if (!conversationId) return

    try {
      await answerQuestions.mutateAsync({
        conversationId,
        answers,
      })
    } catch (error) {
      console.error('Error answering questions:', error)
    }
  }

  if (isLoading) return <LoadingSpinner />

  if (!conversation) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#0A0A0A]">
        <p className="text-gray-400">Conversation not found</p>
      </div>
    )
  }

  const isProcessing = answerQuestions.isPending || conversation.status === 'processing'

  return (
    <div className="flex flex-col h-full bg-[#0A0A0A]">
      {/* Main Chat Area */}
      <div className="flex-1 overflow-y-auto px-6 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="space-y-6">
            {allMessages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                onAnswerQuestions={handleAnswerQuestions}
                isProcessing={isProcessing}
              />
            ))}
            {isProcessing && (
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-cyan-400" />
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Chat Input - Fixed at bottom */}
      <div className="border-t border-gray-800 bg-[#0A0A0A]">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <ChatInput
            onSend={() => {}}
            disabled={true}
            placeholder="This conversation is complete. Start a new goal to continue."
          />
        </div>
      </div>

      {/* WebSocket Status */}
      {conversationId && (
        <div className="fixed bottom-20 right-4 px-3 py-1 bg-gray-800 rounded-full text-xs">
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      )}
    </div>
  )
}

export default ChatView

