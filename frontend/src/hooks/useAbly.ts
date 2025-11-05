import { useState, useEffect, useCallback, useRef } from 'react'
import Ably from 'ably'
import { Message } from '@/types/chat'
import { useQueryClient } from '@tanstack/react-query'
import apiClient from '@/api/client'

export const useAbly = (conversationId: string | null) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const clientRef = useRef<Ably.Realtime | null>(null)
  const channelRef = useRef<Ably.RealtimeChannel | null>(null)
  const connectedForChannelRef = useRef<string | null>(null)
  const seenMessageIdsRef = useRef<Set<string>>(new Set())
  const queryClient = useQueryClient()

  const connect = useCallback(async () => {
    if (!conversationId) return

    try {
      // Initialize Ably client with auth callback
      if (clientRef.current && connectedForChannelRef.current === conversationId && channelRef.current) {
        // Already connected and subscribed for this conversation
        setIsConnected(true)
        return
      }

      const client = new Ably.Realtime({
        authCallback: async (_tokenParams: Ably.TokenParams, callback: (error: Ably.ErrorInfo | string | null, tokenRequestOrDetails: Ably.TokenRequest | Ably.TokenDetails | string | null) => void) => {
          try {
            const { data } = await apiClient.get('/chat/realtime/token')
            callback(null, data)
          } catch (error) {
            console.error('Error fetching Ably token:', error)
            callback(error as Ably.ErrorInfo, null)
          }
        }
      })

      // Wait for connection
      return new Promise<void>((resolve, reject) => {
        client.connection.once('connected', () => {
          setIsConnected(true)
          console.log('Ably connected')

          // Subscribe to conversation channel
          const channel = client.channels.get(`conversation:${conversationId}`)
          console.log('Subscribing to Ably channel:', `conversation:${conversationId}`)

          // Listen for messages
          channel.subscribe('message', (message: Ably.Message) => {
            console.log('Ably event: message', message.data)
            const incoming = message.data?.message as Message | undefined
            const incomingId = (incoming as any)?.id
            if (incoming && incomingId) {
              if (seenMessageIdsRef.current.has(incomingId)) {
                return
              }
              seenMessageIdsRef.current.add(incomingId)
              console.log('Adding message to state:', incoming)
              setMessages((prev) => [...prev, incoming])
              // Don't invalidate queries - causes re-render that clears Ably messages
              // The merge logic in ChatView/LandingPage handles deduplication
            } else {
              console.warn('Message data missing "message" field:', message.data)
            }
          })

          // Listen for status updates
          channel.subscribe('status', (message: Ably.Message) => {
            console.log('Ably event: status', message.data)
            const statusMessage: Message = {
              id: `status-${Date.now()}`,
              conversation_id: conversationId,
              role: 'assistant' as any,
              content: message.data?.message || message.data?.status || '',
              metadata: { type: 'status', status: message.data?.status },
              created_at: new Date().toISOString(),
            }
            setMessages((prev) => [...prev, statusMessage])
          })

          // Listen for completion
          channel.subscribe('complete', (message: Ably.Message) => {
            console.log('Ably event: complete', message.data)
            queryClient.invalidateQueries({ queryKey: ['goals'] })
            queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] })
          })

          clientRef.current = client
          channelRef.current = channel
          connectedForChannelRef.current = conversationId
          resolve()
        })

        client.connection.once('failed', (error) => {
          console.error('Ably connection failed:', error)
          setIsConnected(false)
          reject(error)
        })
      })

    } catch (error) {
      console.error('Ably connection error:', error)
      setIsConnected(false)
    }
  }, [conversationId, queryClient])

  const disconnect = useCallback(() => {
    if (channelRef.current) {
      channelRef.current.unsubscribe()
      channelRef.current = null
    }
    if (clientRef.current) {
      clientRef.current.close()
      clientRef.current = null
    }
    setIsConnected(false)
    connectedForChannelRef.current = null
    // Don't clear messages here - they're managed by conversationId change
  }, [])

  useEffect(() => {
    // Reset when conversation changes
    setMessages([])
    seenMessageIdsRef.current.clear()
    
    connect()
    return () => {
      // Don't disconnect on unmount, only when conversation changes
      // This prevents clearing messages when component re-renders
    }
  }, [conversationId, connect])

  return { messages, isConnected, reconnect: connect }
}

