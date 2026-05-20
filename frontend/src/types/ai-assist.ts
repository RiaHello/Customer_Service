// AI 辅助相关类型定义

export interface Intent {
  level1: string
  level2: string
  is_ambiguous: boolean
}

export interface UserProfile {
  user_id: number
  query_domains: Record<string, number>
  last_updated: string
}

export interface AIAssistInfo {
  ticket_id: number
  intent: Intent
  user_profile: UserProfile
  suggested_keywords: string[]
}

export interface SuggestReply {
  suggested_reply: string
}
