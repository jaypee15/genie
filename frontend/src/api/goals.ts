import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import { Goal, GoalCreateInput, GoalStatus } from '@/types'

export const useGoals = (userId: string) => {
  return useQuery({
    queryKey: ['goals', userId],
    queryFn: async () => {
      const { data } = await apiClient.get<Goal[]>('/goals', {
        params: { user_id: userId },
      })
      return data
    },
    enabled: !!userId,
  })
}

export const useGoal = (goalId: string) => {
  return useQuery({
    queryKey: ['goals', goalId],
    queryFn: async () => {
      const { data } = await apiClient.get<Goal>(`/goals/${goalId}`)
      return data
    },
    enabled: !!goalId,
  })
}

export const useCreateGoal = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      goalData,
      userId,
    }: {
      goalData: GoalCreateInput
      userId: string
    }) => {
      const { data } = await apiClient.post<Goal>('/goals', goalData, {
        params: { user_id: userId },
      })
      return data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['goals', variables.userId] })
    },
  })
}

export const useUpdateGoal = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      goalId,
      status,
    }: {
      goalId: string
      status: GoalStatus
    }) => {
      const { data } = await apiClient.patch<Goal>(`/goals/${goalId}`, {
        status,
      })
      return data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      queryClient.setQueryData(['goals', data.id], data)
    },
  })
}

export const useDeleteGoal = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (goalId: string) => {
      await apiClient.delete(`/goals/${goalId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
    },
  })
}

export const useRefreshGoal = () => {
  return useMutation({
    mutationFn: async (goalId: string) => {
      const { data } = await apiClient.post(`/goals/${goalId}/refresh`)
      return data
    },
  })
}

