export interface User {
  id: string
  email: string
  preferences: Record<string, any>
  created_at: string
  updated_at: string
}

export enum GoalType {
  SPEAKING = 'speaking',
  JOB = 'job',
  GRANT = 'grant',
  EVENT = 'event',
}

export enum GoalStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
}

export interface Goal {
  id: string
  user_id: string
  description: string
  goal_type: GoalType
  filters: Record<string, any>
  status: GoalStatus
  created_at: string
  updated_at: string
}

export enum OpportunityType {
  SPEAKING = 'speaking',
  JOB = 'job',
  GRANT = 'grant',
  EVENT = 'event',
}

export interface Opportunity {
  id: string
  title: string
  description?: string
  source_url: string
  source_name: string
  opportunity_type: OpportunityType
  location?: string
  remote: boolean
  compensation?: Record<string, any>
  tags?: string[]
  scraped_at: string
  created_at: string
  relevance_score?: number
}

export interface Feedback {
  id: string
  user_id: string
  opportunity_id: string
  goal_id: string
  rating: number
  comment?: string
  created_at: string
}

export interface GoalCreateInput {
  description: string
  goal_type?: GoalType
}

export interface FeedbackCreateInput {
  opportunity_id: string
  goal_id: string
  rating: number
  comment?: string
}

// Re-export chat types
export * from './chat'

