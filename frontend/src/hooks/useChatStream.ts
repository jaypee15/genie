import { useState, useEffect, useCallback, useRef } from 'react'
import { Message } from '@/types/chat'
import { useQueryClient } from '@tanstack/react-query'

export const useChatStream = (conversationId: string | null) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [streamingMessages, setStreamingMessages] = useState<Map<string, { content: string; startedAt: string }>>(
    () => new Map<string, { content: string; startedAt: string }>()
  )
  const [isConnected, setIsConnected] = useState(false)
  const streamingMessagesRef = useRef<Map<string, { content: string; startedAt: string }>>(new Map())
  const seenMessageIdsRef = useRef<Set<string>>(new Set())
  const lastTokenRef = useRef<Map<string, string>>(new Map())
  const queryClient = useQueryClient()

  const handleSSEMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data)
      
      switch (event.type) {
        case 'stream_token': {
          const { message_id, token } = data
          // Deduplicate tokens
          const last = lastTokenRef.current.get(message_id)
          if (last === token) return
          lastTokenRef.current.set(message_id, token)
          
          setStreamingMessages((prev: Map<string, { content: string; startedAt: string }>) => {
            const newMap = new Map<string, { content: string; startedAt: string }>(prev)
            const existing = newMap.get(message_id)
            const startedAt = existing?.startedAt ?? new Date().toISOString()
            const currentContent = existing?.content ?? ''
            
            // Avoid duplicate tokens
            if (token && currentContent.endsWith(token)) {
              return prev
            }
            
            newMap.set(message_id, {
              content: currentContent + (token || ''),
              startedAt,
            })
            streamingMessagesRef.current = newMap
            return newMap
          })
          break
        }
        
        case 'stream_end': {
          const { message_id, content, created_at } = data
          
          // Remove from streaming messages
          setStreamingMessages((prev: Map<string, { content: string; startedAt: string }>) => {
            const newMap = new Map<string, { content: string; startedAt: string }>(prev)
            newMap.delete(message_id)
            streamingMessagesRef.current = newMap
            return newMap
          })
          lastTokenRef.current.delete(message_id)
          
          // Add complete message
          const completeMessage: Message = {
            id: message_id,
            conversation_id: conversationId!,
            role: 'assistant' as any,
            content: content,
            metadata: { type: 'clarifying' },
            created_at: created_at || new Date().toISOString(),
          }
          
          if (!seenMessageIdsRef.current.has(message_id)) {
            seenMessageIdsRef.current.add(message_id)
            setMessages((prev: Message[]) => [...prev, completeMessage])
          }
          break
        }
        
        case 'message': {
          const incoming = data.message as Message
          const incomingId = incoming?.id
          if (incoming && incomingId) {
            if (seenMessageIdsRef.current.has(incomingId)) {
              return
            }
            seenMessageIdsRef.current.add(incomingId)
            setMessages((prev: Message[]) => [...prev, incoming])
          }
          break
        }
        
        case 'status': {
          // Create a temporary status message
          const statusId = `status-${Date.now()}`
          const statusMessage: Message = {
            id: statusId,
            conversation_id: conversationId!,
            role: 'assistant' as any,
            content: data.message || data.status || '',
            metadata: { type: 'status', status: data.status },
            created_at: new Date().toISOString(),
          }
          setMessages((prev: Message[]) => [...prev, statusMessage])
          break
        }
        
        case 'complete': {
          // Invalidate queries to refetch updated data
          queryClient.invalidateQueries({ queryKey: ['goals'] })
          queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] })
          break
        }
        
        case 'conversation_created': {
          // Handle conversation creation event (from POST /chat)
          // This is handled by the LandingPage component
          break
        }
      }
    } catch (error) {
      console.error('Error handling SSE message:', error)
    }
  }, [conversationId, queryClient])

  useEffect(() => {
    streamingMessagesRef.current = streamingMessages
  }, [streamingMessages])

  useEffect(() => {
    // Reset when conversation changes
    setMessages([])
    setStreamingMessages(new Map<string, { content: string; startedAt: string }>())
    streamingMessagesRef.current = new Map<string, { content: string; startedAt: string }>()
    seenMessageIdsRef.current.clear()
    lastTokenRef.current.clear()
    
    // SSE connections are established per-request now, not persistent
    // This hook just manages the state
    setIsConnected(true)
    
    return () => {
      setIsConnected(false)
    }
  }, [conversationId])

  return { messages, streamingMessages, isConnected, handleSSEMessage }
}


