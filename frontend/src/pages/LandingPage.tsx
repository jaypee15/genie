import { useState, useEffect, useRef } from 'react'
import { Sparkles } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useCreateConversation, useConversation } from '@/api/chat'
import { useAbly } from '@/hooks/useAbly'
import { useAnswerQuestions } from '@/api/chat'
import ChatMessage from '@/components/ChatMessage'
import ChatInput from '@/components/ChatInput'
import AuthModal from '@/components/AuthModal'
import { useNavigate } from 'react-router-dom'

const LandingPage = () => {
  const { user, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [draftMessage, setDraftMessage] = useState<string | null>(null)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const createConversation = useCreateConversation()
  const answerQuestions = useAnswerQuestions()
  const { data: conversation } = useConversation(currentConversationId || '')
  const { messages: wsMessages, isConnected } = useAbly(currentConversationId)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Merge and dedupe messages by id, keep chronological order
  const allMessages = (() => {
    const byId = new Map<string, typeof wsMessages[number]>()
    const merged = [...(conversation?.messages || []), ...wsMessages]
    for (const m of merged) {
      if (!byId.has(m.id)) byId.set(m.id, m)
    }
    return Array.from(byId.values()).sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  })()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [allMessages])

  // Auto-send draft message after successful login
  useEffect(() => {
    if (user && draftMessage && !authLoading) {
      const messageCopy = draftMessage
      setDraftMessage(null)
      setShowAuthModal(false)
      handleSendMessage(messageCopy)
    }
  }, [user, draftMessage, authLoading])

  const handleSendMessage = async (message: string) => {
    // Check if user is authenticated
    if (!user) {
      // Save draft and show auth modal
      setDraftMessage(message)
      setShowAuthModal(true)
      return
    }

    try {
      const result = await createConversation.mutateAsync({
        initialMessage: message,
      })
      setCurrentConversationId(result.id)
      navigate(`/chat/${result.id}`)
    } catch (error) {
      console.error('Error creating conversation:', error)
    }
  }

  const handleAnswerQuestions = async (answers: Array<{ question: string; answer: string }>) => {
    if (!currentConversationId) return

    try {
      await answerQuestions.mutateAsync({
        conversationId: currentConversationId,
        answers,
      })
    } catch (error) {
      console.error('Error answering questions:', error)
    }
  }

  const isProcessing =
    createConversation.isPending ||
    answerQuestions.isPending ||
    conversation?.status === 'processing'

  return (
    <div className="flex flex-col h-full bg-[#0A0A0A]">
      {allMessages.length === 0 ? (
        // Welcome Screen - Centered
        <div className="flex-1 flex flex-col items-center justify-center px-6">
          <div className="w-full max-w-5xl">
            <div className="text-center mb-12">
              <div className="inline-flex items-center gap-3 mb-6">
                <Sparkles className="w-16 h-16 text-cyan-400" />
                <h1 className="text-6xl font-bold tracking-tight text-white">genie</h1>
              </div>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Your AI-powered opportunity scout. Discover jobs, speaking engagements, and growth opportunities tailored to your goals.
              </p>
            </div>

            {/* Centered Input */}
            <div className="mb-8">
              <ChatInput
                onSend={handleSendMessage}
                disabled={isProcessing}
                placeholder="What opportunities are you looking for?"
              />
            </div>

            {/* Example prompts */}
            <div className="flex flex-wrap gap-3 justify-center">
              {[
                'Find remote software engineering jobs in AI',
                'Speaking opportunities at tech conferences',
                'Freelance web development projects',
                'ML research positions at startups'
              ].map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => handleSendMessage(prompt)}
                  className="px-4 py-2 bg-[#1A1A1A] hover:bg-[#252525] border border-gray-800 rounded-full text-sm text-gray-300 transition-all duration-200"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-6 py-8">
            <div className="max-w-5xl mx-auto">
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
            <div className="max-w-5xl mx-auto px-6 py-4">
              <ChatInput
                onSend={handleSendMessage}
                disabled={isProcessing}
                placeholder="Type your message..."
              />
            </div>
          </div>
        </>
      )}

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => {
          setShowAuthModal(false)
          setDraftMessage(null)
        }}
        onSuccess={() => {
          // Draft will be sent automatically via useEffect
        }}
      />

      {/* WebSocket Status (for debugging) */}
      {currentConversationId && (
        <div className="fixed top-20 right-4 px-3 py-1 bg-gray-800 rounded-full text-xs z-10">
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      )}
    </div>
  )
}

export default LandingPage
