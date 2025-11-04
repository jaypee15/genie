import { useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import { Feedback, FeedbackCreateInput } from '@/types'

export const useCreateFeedback = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      feedbackData,
    }: {
      feedbackData: FeedbackCreateInput
    }) => {
      const { data } = await apiClient.post<Feedback>('/feedback/', feedbackData)
      return data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ['opportunities', data.goal_id],
      })
    },
  })
}

