import { useParams } from 'react-router-dom'
import { useRef, useEffect, useState } from 'react'
import { Sparkles } from 'lucide-react'
import { useConversation, useAnswerQuestions } from '@/api/chat'
import { useChatStream } from '@/hooks/useChatStream'
import ChatMessage from '@/components/ChatMessage'
import ChatInput from '@/components/ChatInput'
import LoadingSpinner from '@/components/LoadingSpinner'
import { Message, MessageRole } from '@/types/chat'

const ChatView = () => {
  const { conversationId } = useParams<{ conversationId: string }>()
  const { data: conversation, isLoading } = useConversation(conversationId || '')
  const { messages: wsMessages, streamingMessages, isConnected, handleSSEMessage } = useChatStream(conversationId || null)
  const answerQuestions = useAnswerQuestions()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [optimistic, setOptimistic] = useState<Message[]>([])

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
    if (!conversationId) return []
    return Array.from(streamingMessages, ([messageId, data]) => ({
      id: messageId,
      conversation_id: conversationId,
      role: MessageRole.ASSISTANT,
      content: data.content,
      metadata: { type: 'clarifying', streaming: true },
      created_at: data.startedAt,
    }))
  })()

  const displayMessages: Message[] = (() => {
    // Merge all messages and deduplicate by ID and content
    const byId = new Map<string, Message>()
    const allMessages = [...optimistic, ...baseMessages, ...streamingEntries]
    
    for (const msg of allMessages) {
      // Skip optimistic if we have the real message from backend
      const isOptimistic = optimistic.some(o => o.id === msg.id)
      const hasReal = baseMessages.some(m => 
        m.role === msg.role && 
        m.content === msg.content && 
        Math.abs(new Date(m.created_at).getTime() - new Date(msg.created_at).getTime()) < 5000
      )
      
      if (isOptimistic && hasReal) {
        continue // Skip optimistic, use real message
      }
      
      if (!byId.has(msg.id)) {
        byId.set(msg.id, msg)
      }
    }
    
    return Array.from(byId.values()).sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    )
  })()

  const lastAssistant = displayMessages
    .filter((m) => m.role === MessageRole.ASSISTANT && !m.metadata?.streaming)
    .slice(-1)[0]
  const awaitingAnswers = lastAssistant?.metadata?.type === 'clarifying' && conversation?.status === 'clarifying'

  const handleSend = async (text: string) => {
    if (!conversationId) return
    try {
      if (awaitingAnswers) {
        // Send free-form answer as a single response to the clarifying message
        const qa = [{ question: "clarification", answer: text }]
        // optimistic user message
        const tempId = crypto.randomUUID()
        const tempMsg: Message = {
          id: tempId,
          conversation_id: conversationId,
          role: MessageRole.USER,
          content: text,
          created_at: new Date().toISOString(),
        }
        setOptimistic((prev) => [...prev, tempMsg])
        
        try {
          await answerQuestions.mutateAsync({ 
            conversationId, 
            answers: qa,
            onEvent: handleSSEMessage,
          })
          // Clear optimistic message after SSE message arrives
          setTimeout(() => {
            setOptimistic((prev) => prev.filter((m) => m.id !== tempId))
          }, 2000)
        } catch (error) {
          // If error, remove optimistic immediately
          setOptimistic((prev) => prev.filter((m) => m.id !== tempId))
          throw error
        }
      } else {
        // No-op for now; only answering clarifying questions is supported in ChatView
        console.warn('No pending clarifying message')
      }
    } catch (e) {
      console.error('Error sending answer:', e)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [displayMessages])

  const handleAnswerQuestions = async (answers: Array<{ question: string; answer: string }>) => {
    if (!conversationId) return

    try {
      await answerQuestions.mutateAsync({
        conversationId,
        answers,
        onEvent: handleSSEMessage,
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
            {isProcessing && streamingEntries.length === 0 && (
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
            onSend={handleSend}
            disabled={isProcessing || conversation.status === 'completed'}
            placeholder={
              conversation.status === 'completed'
                ? 'This conversation is complete. Start a new goal to continue.'
                : isProcessing
                ? 'Processing...'
                : awaitingAnswers
                ? 'Type your answers here...'
                : 'Type your message...'
            }
          />
        </div>
      </div>

      {/* WebSocket Status */}
      {conversationId && (
        <div className="fixed top-20 right-4 px-3 py-1 bg-gray-800 rounded-full text-xs z-10">
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      )}
    </div>
  )
}

export default ChatView

