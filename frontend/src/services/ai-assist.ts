import api from './api'
import type { ApiResponse } from '../types/auth'
import type { AIAssistInfo, SuggestReply } from '../types/ai-assist'
import { mockGetAIAssist, mockSuggestReply } from '../mocks/ai-assist'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

// 获取 AI 辅助信息
export async function getAIAssist(ticketId: number): Promise<ApiResponse<AIAssistInfo>> {
  if (USE_MOCK) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockGetAIAssist(ticketId))
      }, 300)
    })
  }

  const response = await api.get<ApiResponse<AIAssistInfo>>(`/tickets/${ticketId}/ai-assist`)
  return response.data
}

// 生成建议回复
export async function suggestReply(ticketId: number): Promise<ApiResponse<SuggestReply>> {
  if (USE_MOCK) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockSuggestReply(ticketId))
      }, 500)
    })
  }

  const response = await api.post<ApiResponse<SuggestReply>>(`/tickets/${ticketId}/suggest-reply`)
  return response.data
}
