import { ref, onUnmounted } from 'vue'
import type { TicketStatus } from '../types/ticket'

// WebSocket 消息类型定义（按 api-contracts.md 定义）

// 新消息
interface NewMessageData {
  message_id: number
  ticket_id: number
  role: 'user' | 'assistant' | 'agent'
  content: string
  timestamp: string
}

// 工单状态变更
interface StatusChangeData {
  ticket_id: number
  old_status: TicketStatus
  new_status: TicketStatus
  agent_id?: number
  timestamp: string
}

// 连接确认
interface ConnectedData {
  ticket_id: number
  message: string
  timestamp: string
}

// 错误消息
interface ErrorData {
  code: number
  message: string
}

// WebSocket 消息联合类型
type WebSocketMessage =
  | { type: 'new_message'; data: NewMessageData }
  | { type: 'status_change'; data: StatusChangeData }
  | { type: 'connected'; data: ConnectedData }
  | { type: 'error'; data: ErrorData }
  | { type: 'pong'; timestamp: string }

// 客户端发送的心跳包
interface PingMessage {
  type: 'ping'
  timestamp: string
}

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export function useWebSocket(ticketId: number) {
  const connected = ref(false)
  const error = ref<string | null>(null)
  const ws = ref<WebSocket | null>(null)
  const mockInterval = ref<number | null>(null)

  const messageHandlers: ((message: WebSocketMessage) => void)[] = []

  function onMessage(handler: (message: WebSocketMessage) => void) {
    messageHandlers.push(handler)
  }

  function connect() {
    if (USE_MOCK) {
      // Mock WebSocket 连接
      setTimeout(() => {
        connected.value = true
        const connectedMsg: WebSocketMessage = {
          type: 'connected',
          data: {
            ticket_id: ticketId,
            message: 'WebSocket连接成功',
            timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19)
          }
        }
        messageHandlers.forEach((handler) => handler(connectedMsg))
      }, 100)

      // Mock 心跳
      mockInterval.value = window.setInterval(() => {
        if (connected.value) {
          const pongMsg: WebSocketMessage = {
            type: 'pong',
            timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19)
          }
          messageHandlers.forEach((handler) => handler(pongMsg))
        }
      }, 30000)
    } else {
      // 真实 WebSocket 连接
      const token = localStorage.getItem('token')
      if (!token) {
        error.value = 'Token不存在，无法建立WebSocket连接'
        return
      }

      const wsUrl = `ws://localhost:8000/ws/tickets/${ticketId}?token=${token}`
      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = () => {
        connected.value = true
        error.value = null
      }

      ws.value.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          messageHandlers.forEach((handler) => handler(message))
        } catch (err) {
          console.error('WebSocket消息解析失败:', err)
        }
      }

      ws.value.onerror = () => {
        error.value = 'WebSocket连接错误'
        connected.value = false
      }

      ws.value.onclose = () => {
        connected.value = false
      }

      // 心跳
      mockInterval.value = window.setInterval(() => {
        if (ws.value && ws.value.readyState === WebSocket.OPEN) {
          const pingMsg: PingMessage = {
            type: 'ping',
            timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19)
          }
          ws.value.send(JSON.stringify(pingMsg))
        }
      }, 30000)
    }
  }

  function disconnect() {
    connected.value = false
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    if (mockInterval.value !== null) {
      clearInterval(mockInterval.value)
      mockInterval.value = null
    }
  }

  // Mock 推送新消息（用于测试）
  function mockPushMessage(message: WebSocketMessage) {
    if (USE_MOCK && connected.value) {
      messageHandlers.forEach((handler) => handler(message))
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    error,
    connect,
    disconnect,
    onMessage,
    mockPushMessage
  }
}
