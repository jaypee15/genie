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
  const queryClient = useQueryClient()

  const connect = useCallback(async () => {
    if (!conversationId) return

    try {
      // Initialize Ably client with auth callback
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

          // Listen for messages
          channel.subscribe('message', (message: Ably.Message) => {
            if (message.data?.message) {
              setMessages((prev) => [...prev, message.data.message])
              queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] })
            }
          })

          // Listen for status updates
          channel.subscribe('status', (message: Ably.Message) => {
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
          channel.subscribe('complete', (_message: Ably.Message) => {
            queryClient.invalidateQueries({ queryKey: ['goals'] })
            queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] })
          })

          clientRef.current = client
          channelRef.current = channel
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
    }
    if (clientRef.current) {
      clientRef.current.close()
      clientRef.current = null
    }
    setIsConnected(false)
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return { messages, isConnected, reconnect: connect }
}

