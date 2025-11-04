import { useQuery } from '@tanstack/react-query'
import apiClient from './client'
import { Opportunity } from '@/types'

export const useOpportunities = (goalId: string) => {
  return useQuery({
    queryKey: ['opportunities', goalId],
    queryFn: async () => {
      const { data } = await apiClient.get<Opportunity[]>('/opportunities/', {
        params: {
          goal_id: goalId,
        },
      })
      return data
    },
    enabled: !!goalId,
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

