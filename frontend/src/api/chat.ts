import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import { Conversation, ConversationWithMessages, Message, QuestionAnswer } from '@/types/chat'
import { supabase } from '@/lib/supabase'

export const useCreateConversation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      initialMessage,
      onEvent,
    }: {
      initialMessage: string
      onEvent?: (event: MessageEvent) => void
    }) => {
      // Use fetch directly for SSE streaming
      const { data: { session } } = await supabase.auth.getSession()
      const authHeader = session?.access_token ? `Bearer ${session.access_token}` : ''
      
      const response = await fetch(`${apiClient.defaults.baseURL}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authHeader,
        },
        body: JSON.stringify({ initial_message: initialMessage }),
      })

      if (!response.ok) {
        throw new Error('Failed to create conversation')
      }

      if (!response.body) {
        throw new Error('No response body')
      }

      // Read SSE stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let conversationId: string | null = null
      let buffer = ''

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          // Append new chunk to buffer
          buffer += decoder.decode(value, { stream: true })
          
          // Process complete events (separated by \n\n)
          const events = buffer.split('\n\n')
          // Keep the last part in buffer (might be incomplete)
          buffer = events.pop() || ''

          for (const eventBlock of events) {
            if (!eventBlock.trim()) continue
            
            const lines = eventBlock.split('\n')
            let eventType = ''
            let eventData = ''
            
            for (const line of lines) {
              if (line.startsWith('event:')) {
                eventType = line.slice(6).trim()
              } else if (line.startsWith('data:')) {
                eventData = line.slice(5).trim()
              }
            }
            
            if (eventData) {
              try {
                const parsed = JSON.parse(eventData)
                
                // Extract conversation_id from conversation_created event
                if (parsed.conversation_id) {
                  conversationId = parsed.conversation_id
                }
                
                // Call event handler if provided
                if (onEvent) {
                  const event = new MessageEvent(eventType || 'message', { data: eventData })
                  onEvent(event)
                }
              } catch (e) {
                console.error('Failed to parse SSE data:', e, eventData)
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }

      if (!conversationId) {
        throw new Error('No conversation ID received')
      }

      return { id: conversationId } as Conversation
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })
}

export const useConversations = (enabled: boolean = true) => {
  return useQuery({
    queryKey: ['conversations'],
    queryFn: async () => {
      const { data } = await apiClient.get<Conversation[]>('/chat/')
      return data
    },
    enabled,
  })
}

export const useConversation = (conversationId: string) => {
  return useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: async () => {
      const { data } = await apiClient.get<ConversationWithMessages>(
        `/chat/${conversationId}`
      )
      return data
    },
    enabled: !!conversationId,
  })
}

export const useSendMessage = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      conversationId,
      content,
    }: {
      conversationId: string
      content: string
    }) => {
      const { data } = await apiClient.post<Message>(
        `/chat/${conversationId}/message`,
        { content }
      )
      return data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', variables.conversationId] })
    },
  })
}

export const useAnswerQuestions = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      conversationId,
      answers,
      onEvent,
    }: {
      conversationId: string
      answers: QuestionAnswer[]
      onEvent?: (event: MessageEvent) => void
    }) => {
      // Use fetch directly for SSE streaming
      const { data: { session } } = await supabase.auth.getSession()
      const authHeader = session?.access_token ? `Bearer ${session.access_token}` : ''
      
      const response = await fetch(`${apiClient.defaults.baseURL}/chat/${conversationId}/answer-questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authHeader,
        },
        body: JSON.stringify({ answers }),
      })

      if (!response.ok) {
        throw new Error('Failed to answer questions')
      }

      if (!response.body) {
        throw new Error('No response body')
      }

      // Read SSE stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          // Append new chunk to buffer
          buffer += decoder.decode(value, { stream: true })
          
          // Process complete events (separated by \n\n)
          const events = buffer.split('\n\n')
          // Keep the last part in buffer (might be incomplete)
          buffer = events.pop() || ''

          for (const eventBlock of events) {
            if (!eventBlock.trim()) continue
            
            const lines = eventBlock.split('\n')
            let eventType = ''
            let eventData = ''
            
            for (const line of lines) {
              if (line.startsWith('event:')) {
                eventType = line.slice(6).trim()
              } else if (line.startsWith('data:')) {
                eventData = line.slice(5).trim()
              }
            }
            
            if (eventData && onEvent) {
              try {
                const event = new MessageEvent(eventType || 'message', { data: eventData })
                onEvent(event)
              } catch (e) {
                console.error('Failed to parse SSE data:', e, eventData)
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }

      return { success: true }
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', variables.conversationId] })
    },
  })
}

