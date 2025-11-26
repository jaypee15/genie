import { useState, useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useCreateConversation, useConversation } from '@/api/chat'
import { useChatStream } from '@/hooks/useChatStream'
import { useAnswerQuestions } from '@/api/chat'
import ChatMessage from '@/components/ChatMessage'
import ChatInput from '@/components/ChatInput'
import AuthModal from '@/components/AuthModal'
import { Message, MessageRole } from '@/types/chat'

const LandingPage = () => {
  const navigate = useNavigate()
  const { conversationId: urlConversationId } = useParams<{ conversationId?: string }>()
  const { user, loading: authLoading } = useAuth()
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(urlConversationId || null)
  const [draftMessage, setDraftMessage] = useState<string | null>(null)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [optimisticMessages, setOptimisticMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [hasStartedConversation, setHasStartedConversation] = useState<boolean>(Boolean(urlConversationId))
  const createConversation = useCreateConversation()
  const answerQuestions = useAnswerQuestions()
  const { data: conversation } = useConversation(currentConversationId || '')
  const { messages: wsMessages, streamingMessages, isConnected, handleSSEMessage } = useChatStream(currentConversationId)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Sync URL conversation ID with state (handles both setting and clearing)
  useEffect(() => {
    if (urlConversationId !== currentConversationId) {
      // URL changed - sync state
      if (urlConversationId) {
        // Navigating to an existing conversation
        setCurrentConversationId(urlConversationId)
        setHasStartedConversation(true)
      } else {
        // Navigating to /chat (new goal) - reset everything
        setCurrentConversationId(null)
        setHasStartedConversation(false)
        setOptimisticMessages([])
        setIsTyping(false)
      }
    }
  }, [urlConversationId])

  // Merge and dedupe messages by id, keep chronological order
  const baseMessages = (() => {
    const byId = new Map<string, typeof wsMessages[number]>()
    const merged = [...(conversation?.messages || []), ...wsMessages]
    for (const m of merged) {
      if (!byId.has(m.id)) byId.set(m.id, m)
    }
    return Array.from(byId.values()).sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  })()

  const streamingEntries: Message[] = (() => {
    const convId = currentConversationId || conversation?.id
    if (!convId) return []
    return Array.from(streamingMessages, ([messageId, data]) => ({
      id: messageId,
      conversation_id: convId,
      role: MessageRole.ASSISTANT,
      content: data.content,
      metadata: { type: 'clarifying', streaming: true },
      created_at: data.startedAt,
    }))
  })()

  // Clear optimistic messages once real messages arrive from the backend
  useEffect(() => {
    if (optimisticMessages.length > 0 && baseMessages.length > 0) {
      // Check if any optimistic message has a matching real message (same role and content)
      const hasMatchingReal = optimisticMessages.some(opt =>
        baseMessages.some(real =>
          real.role === opt.role && real.content.trim() === opt.content.trim()
        )
      )
      if (hasMatchingReal) {
        setOptimisticMessages([])
      }
    }
  }, [baseMessages, optimisticMessages])

  const displayMessages: Message[] = (() => {
    // Merge optimistic, base, and streaming messages with deduplication
    const byId = new Map<string, Message>()
    // Put base messages first (they're the "real" ones), then streaming
    // Optimistic are only shown if no matching real message exists
    const allMessages = [...baseMessages, ...streamingEntries]
    
    for (const msg of allMessages) {
      if (!byId.has(msg.id)) {
        byId.set(msg.id, msg)
      }
    }
    
    // Add optimistic messages only if they don't have a matching real message
    for (const opt of optimisticMessages) {
      const hasReal = baseMessages.some(m => 
        m.role === opt.role && m.content.trim() === opt.content.trim()
      )
      if (!hasReal && !byId.has(opt.id)) {
        byId.set(opt.id, opt)
      }
    }
    
    return Array.from(byId.values()).sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  })()

  // Track if we're in a conversation (prevent flashing back to welcome screen)
  // Use a stable flag and conversationId so transient message states don't flip the layout
  const inConversation = hasStartedConversation || currentConversationId !== null

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [displayMessages])

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

    // Check if we're in clarifying mode - if so, answer questions instead
    const lastMessage = displayMessages[displayMessages.length - 1]
    const isAwaitingClarification = 
      currentConversationId && 
      lastMessage?.role === MessageRole.ASSISTANT && 
      lastMessage?.metadata?.type === 'clarifying' &&
      conversation?.status === 'clarifying'
    
    if (isAwaitingClarification) {
      // User is answering clarifying questions - treat as answer
      setHasStartedConversation(true)
      await handleAnswerQuestions([{ question: 'clarification', answer: message }])
      return
    }

    // Create optimistic user message IMMEDIATELY
    setHasStartedConversation(true)
    const tempId = crypto.randomUUID()
    const optimisticMsg: Message = {
      id: tempId,
      conversation_id: 'pending',
      role: MessageRole.USER,
      content: message,
      created_at: new Date().toISOString(),
    }
    
    setOptimisticMessages([optimisticMsg])
    setIsTyping(true)

    try {
      const result = await createConversation.mutateAsync({
        initialMessage: message,
        onEvent: (event) => {
          handleSSEMessage(event)
          // Hide typing indicator when first token arrives
          if (event.type === 'stream_token') {
            setIsTyping(false)
          }
        },
      })
      setCurrentConversationId(result.id)
      
      // Update URL with conversation ID (ChatGPT style - same view, URL updates)
      navigate(`/chat/${result.id}`, { replace: true })
      
      // Don't clear optimistic messages - let the deduplication logic handle it
      // The displayMessages logic will automatically filter out duplicates when real messages arrive
      // This prevents the flash when clearing optimistic messages before real ones load
    } catch (error) {
      console.error('Error creating conversation:', error)
      setOptimisticMessages([])
      setIsTyping(false)
    }
  }

  const handleAnswerQuestions = async (answers: Array<{ question: string; answer: string }>) => {
    if (!currentConversationId) return

    setHasStartedConversation(true)

    // Create optimistic user message for the answer
    const answerText = answers.map((qa) => qa.answer).join('\n')
    const tempId = crypto.randomUUID()
    const optimisticMsg: Message = {
      id: tempId,
      conversation_id: currentConversationId,
      role: MessageRole.USER,
      content: answerText,
      created_at: new Date().toISOString(),
    }
    
    setOptimisticMessages([optimisticMsg])

    try {
      await answerQuestions.mutateAsync({
        conversationId: currentConversationId,
        answers,
        onEvent: handleSSEMessage,
      })
      
      // Don't clear optimistic messages - deduplication logic handles it
    } catch (error) {
      console.error('Error answering questions:', error)
      setOptimisticMessages([])
    }
  }

  const isProcessing =
    createConversation.isPending ||
    answerQuestions.isPending ||
    conversation?.status === 'processing'

  return (
    <div className="flex flex-col h-full bg-[#0A0A0A]">
      {!inConversation ? (
        // Welcome Screen - Centered with input
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
                {displayMessages.map((message, index) => (
                  <div 
                    key={message.id}
                    className="animate-slideIn"
                    style={{ animationDelay: `${Math.min(index * 50, 200)}ms` }}
                  >
                    <ChatMessage
                      message={message}
                      onAnswerQuestions={handleAnswerQuestions}
                      isProcessing={isProcessing}
                    />
                  </div>
                ))}
                {(isTyping || (isProcessing && streamingEntries.length === 0)) && (
                  <div className="flex gap-4 animate-fadeIn">
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
