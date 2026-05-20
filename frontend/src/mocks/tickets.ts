import type { ApiResponse } from '../types/auth'
import type {
  TicketListItem,
  PendingTicketListItem,
  TicketDetail,
  TicketListResponse,
  PendingTicketListResponse,
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
  },
  {
    id: 2001,
    status: 'pending',
    last_message: '我的电脑无法开机，按电源键没有任何反应...',
    created_at: '2026-05-20 11:00:00',
    updated_at: '2026-05-20 11:00:00',
    message_count: 3
  },
  {
    id: 2002,
    status: 'pending',
    last_message: 'Outlook收不到邮件，请帮忙排查...',
    created_at: '2026-05-20 10:58:00',
    updated_at: '2026-05-20 10:58:00',
    message_count: 2
  },
  {
    id: 2003,
    status: 'pending',
    last_message: '打印机无法连接到网络，显示离线状态...',
    created_at: '2026-05-20 10:50:00',
    updated_at: '2026-05-20 10:50:00',
    message_count: 2
  }
]

// Mock 待处理工单列表数据（GET /api/tickets/pending 对应字段）
export const mockPendingTicketList: PendingTicketListItem[] = [
  {
    id: 2001,
    status: 'pending',
    last_message: '我的电脑无法开机，按电源键没有任何反应...',
    created_at: '2026-05-20 11:00:00',
    wait_time_seconds: 120,
    user_id: 5,
    message_count: 3
  },
  {
    id: 2002,
    status: 'pending',
    last_message: 'Outlook收不到邮件，请帮忙排查...',
    created_at: '2026-05-20 10:58:00',
    wait_time_seconds: 240,
    user_id: 6,
    message_count: 2
  },
  {
    id: 2003,
    status: 'pending',
    last_message: '打印机无法连接到网络，显示离线状态...',
    created_at: '2026-05-20 10:50:00',
    wait_time_seconds: 720,
    user_id: 7,
    message_count: 2
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
  2001: {
    id: 2001,
    status: 'pending',
    created_at: '2026-05-20 11:00:00',
    updated_at: '2026-05-20 11:00:00',
    user_id: 5,
    agent_id: null,
    messages: [
      {
        id: 201,
        role: 'user',
        content: '你好，我的电脑突然开不了机了，按电源键完全没有反应，请帮我看看是怎么回事？',
        timestamp: '2026-05-20 11:00:00'
      },
      {
        id: 202,
        role: 'assistant',
        content: '您好！我是智能客服助手。电脑无法开机可能有几种原因：电源问题、硬件故障或系统故障。我正在为您查询相关解决方案，请稍候...',
        timestamp: '2026-05-20 11:00:05'
      },
      {
        id: 203,
        role: 'user',
        content: '我需要转人工客服，这个问题比较紧急',
        timestamp: '2026-05-20 11:00:30'
      }
    ]
  },
  2002: {
    id: 2002,
    status: 'pending',
    created_at: '2026-05-20 10:58:00',
    updated_at: '2026-05-20 10:58:00',
    user_id: 6,
    agent_id: null,
    messages: [
      {
        id: 204,
        role: 'user',
        content: 'Outlook收不到邮件，请帮忙排查一下',
        timestamp: '2026-05-20 10:58:00'
      },
      {
        id: 205,
        role: 'assistant',
        content: '您好！Outlook收不到邮件可能是网络配置、账户设置或服务器问题。我为您转接人工客服协助处理。',
        timestamp: '2026-05-20 10:58:08'
      }
    ]
  },
  2003: {
    id: 2003,
    status: 'pending',
    created_at: '2026-05-20 10:50:00',
    updated_at: '2026-05-20 10:50:00',
    user_id: 7,
    agent_id: null,
    messages: [
      {
        id: 206,
        role: 'user',
        content: '打印机无法连接到网络，显示离线状态',
        timestamp: '2026-05-20 10:50:00'
      },
      {
        id: 207,
        role: 'assistant',
        content: '您好！打印机离线可能是网络连接或驱动问题。我正在为您查询解决方案，请稍等片刻。',
        timestamp: '2026-05-20 10:50:07'
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
  },
  1004: {
    id: 1004,
    status: 'completed',
    created_at: '2026-05-20 09:20:00',
    updated_at: '2026-05-20 09:40:00',
    user_id: 2,
    agent_id: 2,
    messages: [
      {
        id: 14,
        role: 'user',
        content: '希望系统能支持批量导出功能，方便我们整理数据',
        timestamp: '2026-05-20 09:20:00'
      },
      {
        id: 15,
        role: 'assistant',
        content: '感谢您的建议！批量导出功能确实很有用。我帮您转接人工客服记录此需求。',
        timestamp: '2026-05-20 09:20:08'
      },
      {
        id: 16,
        role: 'agent',
        content: '您好，我是人工客服小李。感谢您的宝贵建议！我已经将批量导出功能需求记录下来，并反馈给产品团队。',
        timestamp: '2026-05-20 09:25:00'
      },
      {
        id: 17,
        role: 'user',
        content: '好的，期待这个功能尽快上线',
        timestamp: '2026-05-20 09:30:00'
      },
      {
        id: 18,
        role: 'agent',
        content: '我们会认真考虑您的需求，并在未来版本中优先排期。还有其他问题吗？',
        timestamp: '2026-05-20 09:35:00'
      }
    ]
  },
  1005: {
    id: 1005,
    status: 'completed',
    created_at: '2026-05-19 16:30:00',
    updated_at: '2026-05-19 17:00:00',
    user_id: 3,
    agent_id: 3,
    messages: [
      {
        id: 19,
        role: 'user',
        content: '我们公司需要开具增值税专用发票，请问需要提供哪些资料？',
        timestamp: '2026-05-19 16:30:00'
      },
      {
        id: 20,
        role: 'assistant',
        content: '您好！开具增值税专用发票需要提供企业资质。我帮您转接人工客服详细说明。',
        timestamp: '2026-05-19 16:30:10'
      },
      {
        id: 21,
        role: 'agent',
        content: '您好，我是人工客服小王。开具增值税专用发票需要提供：1. 企业营业执照副本；2. 税务登记证；3. 开户许可证；4. 一般纳税人资格证明。',
        timestamp: '2026-05-19 16:35:00'
      },
      {
        id: 22,
        role: 'user',
        content: '明白了，我准备好资料后发给你们',
        timestamp: '2026-05-19 16:40:00'
      },
      {
        id: 23,
        role: 'agent',
        content: '好的，您可以将资料发送到我们的企业邮箱 finance@company.com，我们会在 3 个工作日内为您开具发票。',
        timestamp: '2026-05-19 16:45:00'
      },
      {
        id: 24,
        role: 'user',
        content: '收到，谢谢！',
        timestamp: '2026-05-19 16:50:00'
      },
      {
        id: 25,
        role: 'agent',
        content: '不客气！如有其他问题，随时联系我们。',
        timestamp: '2026-05-19 16:55:00'
      },
      {
        id: 26,
        role: 'user',
        content: '好的',
        timestamp: '2026-05-19 17:00:00'
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

// Mock API: 获取待处理工单列表（坐席端专用）
export function mockGetPendingTickets(params: {
  page?: number
  page_size?: number
}): ApiResponse<PendingTicketListResponse> {
  const { page = 1, page_size = 20 } = params

  const start = (page - 1) * page_size
  const end = start + page_size
  const items = mockPendingTicketList.slice(start, end)

  return {
    code: 200,
    message: 'success',
    data: {
      items,
      total: mockPendingTicketList.length,
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

// Mock API: 坐席接单
export function mockPickTicket(ticketId: number): ApiResponse<{
  ticket_id: number
  status: 'in_progress'
  agent_id: number
  picked_at: string
}> {
  const ticket = mockTicketList.find((t) => t.id === ticketId)

  if (!ticket) {
    return {
      code: 2001,
      message: '工单不存在',
      data: null
    }
  }

  if (ticket.status !== 'pending') {
    return {
      code: 2002,
      message: '当前工单状态不允许接单',
      data: null
    }
  }

  const pickedAt = new Date().toISOString().replace('T', ' ').substring(0, 19)

  // 更新工单状态
  ticket.status = 'in_progress'
  ticket.updated_at = pickedAt

  if (mockTicketDetails[ticketId]) {
    mockTicketDetails[ticketId].status = 'in_progress'
    mockTicketDetails[ticketId].agent_id = 2 // 假设当前坐席 ID 为 2
  }

  return {
    code: 200,
    message: 'success',
    data: {
      ticket_id: ticketId,
      status: 'in_progress',
      agent_id: 2,
      picked_at: pickedAt
    }
  }
}

// Mock API: 结束工单
export function mockCompleteTicket(ticketId: number): ApiResponse<{
  ticket_id: number
  status: 'completed'
  completed_at: string
}> {
  const ticket = mockTicketList.find((t) => t.id === ticketId)

  if (!ticket) {
    return {
      code: 2001,
      message: '工单不存在',
      data: null
    }
  }

  if (ticket.status !== 'in_progress') {
    return {
      code: 2002,
      message: '当前工单状态不允许结束',
      data: null
    }
  }

  const completedAt = new Date().toISOString().replace('T', ' ').substring(0, 19)

  // 更新工单状态
  ticket.status = 'completed'
  ticket.updated_at = completedAt

  if (mockTicketDetails[ticketId]) {
    mockTicketDetails[ticketId].status = 'completed'
  }

  return {
    code: 200,
    message: 'success',
    data: {
      ticket_id: ticketId,
      status: 'completed',
      completed_at: completedAt
    }
  }
}
