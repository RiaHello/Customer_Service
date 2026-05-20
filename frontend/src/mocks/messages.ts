import type { ApiResponse } from '../types/auth'
import type { Message, SendMessageResponse } from '../types/ticket'
import { mockTicketList, mockTicketDetails } from './tickets'

// Mock API: 发送消息
export function mockSendMessage(
  ticketId: number,
  content: string
): ApiResponse<SendMessageResponse> {
  const ticket = mockTicketList.find((t) => t.id === ticketId)

  if (!ticket) {
    return {
      code: 2001,
      message: '工单不存在',
      data: null
    }
  }

  const newMessageId = Date.now()
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19)

  const newMessage: Message = {
    id: newMessageId,
    role: 'user',
    content,
    timestamp
  }

  // 更新工单最后消息和时间
  ticket.last_message = content
  ticket.message_count += 1
  ticket.updated_at = timestamp

  // 添加到消息列表
  if (mockTicketDetails[ticketId]) {
    mockTicketDetails[ticketId].messages.push(newMessage)
  }

  return {
    code: 200,
    message: 'success',
    data: {
      message_id: newMessageId,
      ticket_id: ticketId,
      role: 'user',
      content,
      timestamp
    }
  }
}

// Mock API: 获取消息历史
export function mockGetMessages(
  ticketId: number,
  params: { page?: number; page_size?: number }
): ApiResponse<{ items: Message[]; total: number; page: number; page_size: number }> {
  const ticket = mockTicketDetails[ticketId]

  if (!ticket) {
    return {
      code: 2001,
      message: '工单不存在',
      data: null
    }
  }

  const { page = 1, page_size = 50 } = params
  const start = (page - 1) * page_size
  const end = start + page_size
  const items = ticket.messages.slice(start, end)

  return {
    code: 200,
    message: 'success',
    data: {
      items,
      total: ticket.messages.length,
      page,
      page_size
    }
  }
}
