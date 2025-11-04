export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
}

export interface Message {
  id: string
  conversation_id: string
  role: MessageRole
  content: string
  metadata?: {
    type?: 'questions' | 'question_answers' | 'status' | 'completion' | 'error'
    questions?: Question[]
    answers?: QuestionAnswer[]
    status?: string
    goal_id?: string
  }
  created_at: string
}

export interface Question {
  question: string
  type: 'text' | 'select' | 'number'
  options?: string[]
}

export interface QuestionAnswer {
  question: string
  answer: string
}

export interface Conversation {
  id: string
  user_id: string
  goal_id?: string
  title?: string
  status: 'active' | 'clarifying' | 'processing' | 'completed'
  created_at: string
  updated_at: string
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[]
}

export interface WebSocketMessage {
  type: 'message' | 'status' | 'complete' | 'error'
  message?: Message
  status?: string
  goal_id?: string
  opportunities_count?: number
  metadata?: Record<string, any>
}

