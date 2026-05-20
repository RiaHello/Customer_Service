import api from './api'
import type { ApiResponse } from '../types/auth'
import type { Message, SendMessageResponse } from '../types/ticket'
import { mockSendMessage, mockGetMessages } from '../mocks/messages'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export const messagesService = {
  // 发送消息
  async sendMessage(
    ticketId: number,
    content: string
  ): Promise<ApiResponse<SendMessageResponse>> {
    if (USE_MOCK) {
      return Promise.resolve(mockSendMessage(ticketId, content))
    }

    const response = await api.post<ApiResponse<SendMessageResponse>>(
      `/tickets/${ticketId}/messages`,
      { content }
    )
    return response.data
  },

  // 获取消息历史
  async getMessages(
    ticketId: number,
    params: { page?: number; page_size?: number }
  ): Promise<
    ApiResponse<{ items: Message[]; total: number; page: number; page_size: number }>
  > {
    if (USE_MOCK) {
      return Promise.resolve(mockGetMessages(ticketId, params))
    }

    const response = await api.get<
      ApiResponse<{ items: Message[]; total: number; page: number; page_size: number }>
    >(`/tickets/${ticketId}/messages`, { params })
    return response.data
  }
}
