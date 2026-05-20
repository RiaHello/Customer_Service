import api from './api'
import type { ApiResponse } from '../types/auth'
import type {
  TicketListResponse,
  PendingTicketListResponse,
  TicketDetail,
  CreateTicketResponse,
  TransferTicketResponse
} from '../types/ticket'
import {
  mockGetTickets,
  mockGetPendingTickets,
  mockGetTicketDetail,
  mockCreateTicket,
  mockTransferTicket,
  mockPickTicket,
  mockCompleteTicket
} from '../mocks/tickets'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export const ticketsService = {
  // 获取工单列表
  async getTickets(params: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<ApiResponse<TicketListResponse>> {
    if (USE_MOCK) {
      return Promise.resolve(mockGetTickets(params))
    }

    const response = await api.get<ApiResponse<TicketListResponse>>('/tickets', { params })
    return response.data
  },

  // 获取待处理工单列表（坐席端专用）
  async getPendingTickets(params: {
    page?: number
    page_size?: number
  }): Promise<ApiResponse<PendingTicketListResponse>> {
    if (USE_MOCK) {
      return Promise.resolve(mockGetPendingTickets(params))
    }

    const response = await api.get<ApiResponse<PendingTicketListResponse>>('/tickets/pending', {
      params
    })
    return response.data
  },

  // 获取工单详情
  async getTicketDetail(ticketId: number): Promise<ApiResponse<TicketDetail>> {
    if (USE_MOCK) {
      return Promise.resolve(mockGetTicketDetail(ticketId))
    }

    const response = await api.get<ApiResponse<TicketDetail>>(`/tickets/${ticketId}`)
    return response.data
  },

  // 创建工单（发起咨询）
  async createTicket(message: string): Promise<ApiResponse<CreateTicketResponse>> {
    if (USE_MOCK) {
      return Promise.resolve(mockCreateTicket(message))
    }

    const response = await api.post<ApiResponse<CreateTicketResponse>>('/tickets', { message })
    return response.data
  },

  // 转人工
  async transferTicket(ticketId: number): Promise<ApiResponse<TransferTicketResponse>> {
    if (USE_MOCK) {
      return Promise.resolve(mockTransferTicket(ticketId))
    }

    const response = await api.put<ApiResponse<TransferTicketResponse>>(
      `/tickets/${ticketId}/transfer`,
      {}
    )
    return response.data
  },

  // 坐席接单
  async pickTicket(
    ticketId: number
  ): Promise<
    ApiResponse<{ ticket_id: number; status: 'in_progress'; agent_id: number; picked_at: string }>
  > {
    if (USE_MOCK) {
      return Promise.resolve(mockPickTicket(ticketId))
    }

    const response = await api.put<
      ApiResponse<{ ticket_id: number; status: 'in_progress'; agent_id: number; picked_at: string }>
    >(`/tickets/${ticketId}/pick`, {})
    return response.data
  },

  // 结束工单
  async completeTicket(
    ticketId: number
  ): Promise<ApiResponse<{ ticket_id: number; status: 'completed'; completed_at: string }>> {
    if (USE_MOCK) {
      return Promise.resolve(mockCompleteTicket(ticketId))
    }

    const response = await api.put<
      ApiResponse<{ ticket_id: number; status: 'completed'; completed_at: string }>
    >(`/tickets/${ticketId}/complete`, {})
    return response.data
  }
}
