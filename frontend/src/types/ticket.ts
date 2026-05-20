export type TicketStatus = 'ai_answering' | 'pending' | 'in_progress' | 'completed'

// 工单列表项（GET /api/tickets 返回的列表项字段）
export interface TicketListItem {
  id: number
  status: TicketStatus
  last_message: string
  created_at: string
  updated_at: string
  message_count: number
}

// 待处理工单列表项（GET /api/tickets/pending 返回的列表项字段）
export interface PendingTicketListItem {
  id: number
  status: 'pending'
  last_message: string
  created_at: string
  wait_time_seconds: number
  user_id: number
  message_count: number
}

// 工单（兼容列表和详情，保留可选的详情字段）
export interface Ticket extends TicketListItem {
  user_id?: number
  agent_id?: number | null
}

// 工单详情（GET /api/tickets/{id} 返回的完整字段）
export interface TicketDetail {
  id: number
  status: TicketStatus
  created_at: string
  updated_at: string
  user_id: number
  agent_id: number | null
  messages: Message[]
}

export interface Message {
  id: number
  role: 'user' | 'assistant' | 'agent'
  content: string
  timestamp: string
}

export interface TicketListResponse {
  items: TicketListItem[]
  total: number
  page: number
  page_size: number
}

export interface PendingTicketListResponse {
  items: PendingTicketListItem[]
  total: number
  page: number
  page_size: number
}

export interface CreateTicketResponse {
  ticket_id: number
  status: TicketStatus
  created_at: string
  messages: Message[]
}

export interface TransferTicketResponse {
  ticket_id: number
  status: TicketStatus
  updated_at: string
}

export interface SendMessageResponse {
  message_id: number
  ticket_id: number
  role: 'user' | 'assistant' | 'agent'
  content: string
  timestamp: string
}
