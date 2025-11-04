import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from './client'
import { Goal, GoalCreateInput, GoalStatus } from '@/types'

export const useGoals = (enabled: boolean = true) => {
  return useQuery({
    queryKey: ['goals'],
    queryFn: async () => {
      const { data } = await apiClient.get<Goal[]>('/goals/')
      return data
    },
    enabled,
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
    }: {
      goalData: GoalCreateInput
    }) => {
      const { data } = await apiClient.post<Goal>('/goals/', goalData)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
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

