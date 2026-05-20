import type { ApiResponse } from '../types/auth'
import type {
  TicketListItem,
  TicketDetail,
  TicketListResponse,
  CreateTicketResponse,
  TransferTicketResponse
} from '../types/ticket'

// Mock 工单列表数据（只包含 GET /api/tickets 定义的字段）
export const mockTicketList: TicketListItem[] = [
  {
    id: 1000,
    status: 'ai_answering',
    last_message: '您好！我是智能客服助手，请问如何修改我的个人资料？',
    created_at: '2026-05-20 10:45:00',
    updated_at: '2026-05-20 10:45:00',
    message_count: 2
  },
  {
    id: 1001,
    status: 'in_progress',
    last_message: '客户反馈无法查看历史订单详情，需要协助解决...',
    created_at: '2026-05-20 10:30:00',
    updated_at: '2026-05-20 10:35:00',
    message_count: 4
  },
  {
    id: 1002,
    status: 'in_progress',
    last_message: '用户询问退款流程和预计到账时间...',
    created_at: '2026-05-20 10:15:00',
    updated_at: '2026-05-20 10:20:00',
    message_count: 3
  },
  {
    id: 1003,
    status: 'completed',
    last_message: '多次输入错误密码导致账户被锁定，请求解锁...',
    created_at: '2026-05-20 09:45:00',
    updated_at: '2026-05-20 10:00:00',
    message_count: 6
  },
  {
    id: 1004,
    status: 'completed',
    last_message: '客户建议增加批量导出功能，已记录并反馈...',
    created_at: '2026-05-20 09:20:00',
    updated_at: '2026-05-20 09:40:00',
    message_count: 5
  },
  {
    id: 1005,
    status: 'completed',
    last_message: '企业用户申请开具增值税专用发票...',
    created_at: '2026-05-19 16:30:00',
    updated_at: '2026-05-19 17:00:00',
    message_count: 8
  }
]

// Mock 工单详情数据
export const mockTicketDetails: Record<number, TicketDetail> = {
  1000: {
    id: 1000,
    status: 'ai_answering',
    created_at: '2026-05-20 10:45:00',
    updated_at: '2026-05-20 10:45:00',
    user_id: 1,
    agent_id: null,
    messages: [
      {
        id: 1,
        role: 'user',
        content: '请问如何修改我的个人资料？',
        timestamp: '2026-05-20 10:45:00'
      },
      {
        id: 2,
        role: 'assistant',
        content: '您好！我是智能客服助手。修改个人资料很简单：1. 登录您的账户；2. 进入"个人中心"；3. 点击"编辑资料"；4. 修改后保存即可。请问还有其他问题吗？',
        timestamp: '2026-05-20 10:45:05'
      }
    ]
  },
  1001: {
    id: 1001,
    status: 'in_progress',
    created_at: '2026-05-20 10:30:00',
    updated_at: '2026-05-20 10:35:00',
    user_id: 1,
    agent_id: 2,
    messages: [
      {
        id: 1,
        role: 'user',
        content: '我的订单列表页面显示空白，无法查看历史订单',
        timestamp: '2026-05-20 10:30:00'
      },
      {
        id: 2,
        role: 'assistant',
        content: '您好！感谢您的反馈。请问您是在哪个页面遇到这个问题的？能否提供一下您的账号或订单号？',
        timestamp: '2026-05-20 10:30:05'
      },
      {
        id: 3,
        role: 'user',
        content: '在"我的订单"页面，账号是 user001',
        timestamp: '2026-05-20 10:32:00'
      },
      {
        id: 4,
        role: 'agent',
        content: '我是人工客服小李，我来帮您处理。我看到您的账号数据正常，可能是缓存问题，建议您清除浏览器缓存后重试。',
        timestamp: '2026-05-20 10:35:00'
      }
    ]
  },
  1002: {
    id: 1002,
    status: 'in_progress',
    created_at: '2026-05-20 10:15:00',
    updated_at: '2026-05-20 10:20:00',
    user_id: 1,
    agent_id: null,
    messages: [
      {
        id: 5,
        role: 'user',
        content: '我想申请退款，请问需要多久能到账？',
        timestamp: '2026-05-20 10:15:00'
      },
      {
        id: 6,
        role: 'assistant',
        content: '您好！退款申请提交后，审核通过一般需要1-3个工作日，到账时间根据您的支付方式而定：支付宝/微信一般1-3个工作日，银行卡3-7个工作日。',
        timestamp: '2026-05-20 10:15:08'
      },
      {
        id: 7,
        role: 'user',
        content: '我用的是支付宝支付，那我大概什么时候能收到退款？',
        timestamp: '2026-05-20 10:20:00'
      }
    ]
  },
  1003: {
    id: 1003,
    status: 'completed',
    created_at: '2026-05-20 09:45:00',
    updated_at: '2026-05-20 10:00:00',
    user_id: 1,
    agent_id: 3,
    messages: [
      {
        id: 8,
        role: 'user',
        content: '我的账户被锁定了，显示密码错误次数过多',
        timestamp: '2026-05-20 09:45:00'
      },
      {
        id: 9,
        role: 'assistant',
        content: '抱歉给您带来不便。账户锁定是为了保护您的账户安全。请您稍等，我帮您转接人工客服处理。',
        timestamp: '2026-05-20 09:45:06'
      },
      {
        id: 10,
        role: 'agent',
        content: '您好，我是人工客服小王。我已经帮您解锁账户，请您使用手机验证码登录后重新设置密码。',
        timestamp: '2026-05-20 09:50:00'
      },
      {
        id: 11,
        role: 'user',
        content: '好的，谢谢！我重新登录成功了',
        timestamp: '2026-05-20 09:55:00'
      },
      {
        id: 12,
        role: 'agent',
        content: '不客气！建议您设置一个较强的密码，并开启双因素认证以提高安全性。还有其他问题吗？',
        timestamp: '2026-05-20 09:56:00'
      },
      {
        id: 13,
        role: 'user',
        content: '没有了，非常感谢！',
        timestamp: '2026-05-20 10:00:00'
      }
    ]
  }
}

// Mock API: 获取工单列表
export function mockGetTickets(params: {
  page?: number
  page_size?: number
  status?: string
}): ApiResponse<TicketListResponse> {
  const { page = 1, page_size = 20, status } = params

  let filteredTickets = [...mockTicketList]

  if (status) {
    filteredTickets = filteredTickets.filter((ticket) => ticket.status === status)
  }

  const start = (page - 1) * page_size
  const end = start + page_size
  const items = filteredTickets.slice(start, end)

  return {
    code: 200,
    message: 'success',
    data: {
      items,
      total: filteredTickets.length,
      page,
      page_size
    }
  }
}

// Mock API: 获取工单详情
export function mockGetTicketDetail(ticketId: number): ApiResponse<TicketDetail> {
  const ticket = mockTicketDetails[ticketId]

  if (!ticket) {
    return {
      code: 2001,
      message: '工单不存在',
      data: null
    }
  }

  return {
    code: 200,
    message: 'success',
    data: ticket
  }
}

// Mock API: 创建工单（发起咨询）
export function mockCreateTicket(message: string): ApiResponse<CreateTicketResponse> {
  const newTicketId = Math.max(...mockTicketList.map((t) => t.id)) + 1

  // 模拟 AI 回复
  const aiReply = `您好！我是智能客服助手。关于您提到的"${message.substring(0, 20)}..."，我正在为您查询相关信息。请稍候片刻。`

  const newTicket: CreateTicketResponse = {
    ticket_id: newTicketId,
    status: 'ai_answering',
    created_at: new Date().toISOString().replace('T', ' ').substring(0, 19),
    messages: [
      {
        id: Date.now(),
        role: 'user',
        content: message,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19)
      },
      {
        id: Date.now() + 1,
        role: 'assistant',
        content: aiReply,
        timestamp: new Date(Date.now() + 3000).toISOString().replace('T', ' ').substring(0, 19)
      }
    ]
  }

  // 添加到 Mock 列表数据中
  mockTicketList.unshift({
    id: newTicketId,
    status: 'ai_answering',
    last_message: aiReply,
    created_at: newTicket.created_at,
    updated_at: newTicket.created_at,
    message_count: 2
  })

  mockTicketDetails[newTicketId] = {
    id: newTicketId,
    status: 'ai_answering',
    created_at: newTicket.created_at,
    updated_at: newTicket.created_at,
    user_id: 1,
    agent_id: null,
    messages: newTicket.messages
  }

  return {
    code: 200,
    message: 'success',
    data: newTicket
  }
}

// Mock API: 转人工
export function mockTransferTicket(ticketId: number): ApiResponse<TransferTicketResponse> {
  const ticket = mockTicketList.find((t) => t.id === ticketId)

  if (!ticket) {
    return {
      code: 2001,
      message: '工单不存在',
      data: null
    }
  }

  if (ticket.status !== 'ai_answering') {
    return {
      code: 2002,
      message: '当前工单状态不允许转人工',
      data: null
    }
  }

  // 更新工单状态
  ticket.status = 'pending'
  ticket.updated_at = new Date().toISOString().replace('T', ' ').substring(0, 19)

  if (mockTicketDetails[ticketId]) {
    mockTicketDetails[ticketId].status = 'pending'
  }

  return {
    code: 200,
    message: 'success',
    data: {
      ticket_id: ticketId,
      status: 'pending',
      updated_at: ticket.updated_at
    }
  }
}
