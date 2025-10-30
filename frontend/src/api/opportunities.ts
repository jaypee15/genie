import { useQuery } from '@tanstack/react-query'
import apiClient from './client'
import { Opportunity } from '@/types'

export const useOpportunities = (goalId: string, userId: string) => {
  return useQuery({
    queryKey: ['opportunities', goalId, userId],
    queryFn: async () => {
      const { data } = await apiClient.get<Opportunity[]>('/opportunities', {
        params: {
          goal_id: goalId,
          user_id: userId,
        },
      })
      return data
    },
    enabled: !!goalId && !!userId,
  })
}

export const useOpportunity = (opportunityId: string) => {
  return useQuery({
    queryKey: ['opportunities', opportunityId],
    queryFn: async () => {
      const { data } = await apiClient.get<Opportunity>(
        `/opportunities/${opportunityId}`
      )
      return data
    },
    enabled: !!opportunityId,
  })
}

