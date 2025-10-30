import { useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import { Feedback, FeedbackCreateInput } from '@/types'

export const useCreateFeedback = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      feedbackData,
      userId,
    }: {
      feedbackData: FeedbackCreateInput
      userId: string
    }) => {
      const { data } = await apiClient.post<Feedback>('/feedback', feedbackData, {
        params: { user_id: userId },
      })
      return data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ['opportunities', data.goal_id],
      })
    },
  })
}

