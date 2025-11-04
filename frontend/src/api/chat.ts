import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import { Conversation, ConversationWithMessages, Message, QuestionAnswer } from '@/types/chat'

export const useCreateConversation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      initialMessage,
    }: {
      initialMessage: string
    }) => {
      const { data } = await apiClient.post<Conversation>('/chat/', 
        { initial_message: initialMessage }
      )
      return data
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
    }: {
      conversationId: string
      answers: QuestionAnswer[]
    }) => {
      const { data } = await apiClient.post(
        `/chat/${conversationId}/answer-questions`,
        { answers }
      )
      return data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', variables.conversationId] })
    },
  })
}

