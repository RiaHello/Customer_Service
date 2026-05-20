<template>
  <div class="employee-page">
    <!-- 左侧工单列表 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>工单列表</h2>
      </div>
      <div class="filter-buttons">
        <button
          :class="['filter-btn', { active: activeFilter === 'all' }]"
          @click="setFilter('all')"
        >
          全部
        </button>
        <button
          :class="['filter-btn', { active: activeFilter === 'in_progress' }]"
          @click="setFilter('in_progress')"
        >
          进行中
        </button>
        <button
          :class="['filter-btn', { active: activeFilter === 'completed' }]"
          @click="setFilter('completed')"
        >
          已完结
        </button>
      </div>
      <div class="ticket-list">
        <div
          v-for="ticket in filteredTickets"
          :key="ticket.id"
          :class="['ticket-card', { active: currentTicketId === ticket.id }]"
          @click="selectTicket(ticket.id)"
        >
          <div class="ticket-title">{{ getTicketTitle(ticket) }}</div>
          <div class="ticket-preview">{{ ticket.last_message }}</div>
          <div class="ticket-footer">
            <span class="ticket-time">{{ formatTime(ticket.created_at) }}</span>
            <span :class="['ticket-status', `status-${ticket.status}`]">
              {{ formatStatus(ticket.status) }}
            </span>
          </div>
        </div>
        <div v-if="filteredTickets.length === 0" class="empty-list">暂无工单</div>
      </div>
    </div>

    <!-- 右侧对话区 -->
    <div class="main-area">
      <!-- 顶部状态栏 -->
      <div class="status-bar">
        <div class="status-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              d="M12 2a9 9 0 0 1 9 9v4.5a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 15.5V11a9 9 0 0 1 9-9Z"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <path
              d="M8 21h8"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
        <div class="status-text">{{ currentStatusText }}</div>
      </div>

      <!-- 对话区域 -->
      <div class="chat-area">
        <div ref="messagesContainer" class="messages-container">
          <!-- 未选择工单时的占位 -->
          <div v-if="!currentTicketId" class="empty-chat-placeholder">
            <div class="empty-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
            <p>输入您的问题开始咨询</p>
          </div>

          <!-- 已选择工单时显示消息 -->
          <div
            v-for="message in currentMessages"
            :key="message.id"
            :class="['message', `message-${message.role}`]"
          >
            <div class="message-avatar">
              <svg
                v-if="message.role === 'assistant' || message.role === 'agent'"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  d="M12 2a9 9 0 0 1 9 9v4.5a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 15.5V11a9 9 0 0 1 9-9Z"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <svg
                v-else
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <circle cx="12" cy="7" r="4" stroke-width="2" />
              </svg>
            </div>
            <div class="message-bubble">
              <div class="message-content">{{ message.content }}</div>
            </div>
          </div>
        </div>

        <!-- 底部输入区 -->
        <div class="input-area">
          <div class="input-wrapper">
            <textarea
              v-model="inputMessage"
              class="message-input"
              placeholder="输入您的问题..."
              :disabled="isTicketCompleted"
              @keydown.enter.prevent="handleSendMessage"
            />
            <div class="input-actions">
              <button
                v-if="canTransferToAgent"
                class="transfer-btn"
                :disabled="loading"
                @click="handleTransferToAgent"
              >
                转人工
              </button>
              <button
                class="send-btn"
                :disabled="!inputMessage.trim() || loading || isTicketCompleted"
                @click="handleSendMessage"
              >
                发送
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ticketsService } from '../services/tickets'
import { messagesService } from '../services/messages'
import { useWebSocket } from '../composables/useWebSocket'
import type { Ticket, TicketStatus, Message } from '../types/ticket'

// 状态
const activeFilter = ref<'all' | 'in_progress' | 'completed'>('all')
const tickets = ref<Ticket[]>([])
const currentTicketId = ref<number | null>(null)
const currentMessages = ref<Message[]>([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

// WebSocket 连接
let wsConnection: ReturnType<typeof useWebSocket> | null = null

// 计算属性
const filteredTickets = computed(() => {
  if (activeFilter.value === 'all') {
    return tickets.value
  }
  if (activeFilter.value === 'in_progress') {
    return tickets.value.filter(
      (t) => t.status === 'ai_answering' || t.status === 'pending' || t.status === 'in_progress'
    )
  }
  if (activeFilter.value === 'completed') {
    return tickets.value.filter((t) => t.status === 'completed')
  }
  return tickets.value
})

const currentTicket = computed(() => {
  return tickets.value.find((t) => t.id === currentTicketId.value)
})

const isTicketCompleted = computed(() => {
  return currentTicket.value?.status === 'completed'
})

const canTransferToAgent = computed(() => {
  return currentTicket.value?.status === 'ai_answering'
})

const currentStatusText = computed(() => {
  if (!currentTicket.value) return 'AI助手'

  switch (currentTicket.value.status) {
    case 'ai_answering':
      return 'AI助手'
    case 'pending':
      return '等待人工客服'
    case 'in_progress':
      return '人工客服处理中'
    case 'completed':
      return '已完结'
    default:
      return 'AI助手'
  }
})

// 方法
function setFilter(filter: 'all' | 'in_progress' | 'completed') {
  activeFilter.value = filter
}

async function loadTickets() {
  try {
    const response = await ticketsService.getTickets({
      page: 1,
      page_size: 50
    })
    if (response.code === 200 && response.data) {
      tickets.value = response.data.items
    }
  } catch (error) {
    console.error('加载工单列表失败:', error)
  }
}

async function selectTicket(ticketId: number) {
  currentTicketId.value = ticketId
  await loadTicketMessages(ticketId)
  connectWebSocket(ticketId)
}

async function loadTicketMessages(ticketId: number) {
  try {
    const response = await ticketsService.getTicketDetail(ticketId)
    if (response.code === 200 && response.data) {
      currentMessages.value = response.data.messages
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('加载工单详情失败:', error)
  }
}

function connectWebSocket(ticketId: number) {
  // 断开旧连接
  if (wsConnection) {
    wsConnection.disconnect()
  }

  // 创建新连接
  wsConnection = useWebSocket(ticketId)

  wsConnection.onMessage((message) => {
    if (message.type === 'new_message') {
      const newMsg: Message = {
        id: message.data.message_id,
        role: message.data.role,
        content: message.data.content,
        timestamp: message.data.timestamp
      }
      currentMessages.value.push(newMsg)
      nextTick(() => scrollToBottom())
    } else if (message.type === 'status_change') {
      // 更新工单状态
      const ticket = tickets.value.find((t) => t.id === ticketId)
      if (ticket) {
        ticket.status = message.data.new_status
      }
    }
  })

  wsConnection.connect()
}

async function handleSendMessage() {
  if (!inputMessage.value.trim() || loading.value) return

  const content = inputMessage.value.trim()
  inputMessage.value = ''
  loading.value = true

  try {
    // 如果是新建工单
    if (!currentTicketId.value) {
      const response = await ticketsService.createTicket(content)
      if (response.code === 200 && response.data) {
        currentTicketId.value = response.data.ticket_id
        currentMessages.value = response.data.messages
        await loadTickets()
        connectWebSocket(response.data.ticket_id)
        await nextTick()
        scrollToBottom()
      }
    } else {
      // 发送消息到现有工单
      const response = await messagesService.sendMessage(currentTicketId.value, content)
      if (response.code === 200 && response.data) {
        currentMessages.value.push({
          id: response.data.message_id,
          role: response.data.role,
          content: response.data.content,
          timestamp: response.data.timestamp
        })

        // Mock AI 自动回复（仅在 Mock 模式下）
        if (import.meta.env.VITE_USE_MOCK === 'true') {
          setTimeout(() => {
            const aiReply: Message = {
              id: Date.now(),
              role: 'assistant',
              content: `我收到您的消息："${content.substring(0, 20)}..."，正在为您处理。`,
              timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19)
            }
            currentMessages.value.push(aiReply)
            nextTick(() => scrollToBottom())
          }, 1000)
        }

        await nextTick()
        scrollToBottom()
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    alert('发送消息失败，请重试')
  } finally {
    loading.value = false
  }
}

async function handleTransferToAgent() {
  if (!currentTicketId.value || loading.value) return

  loading.value = true

  try {
    const response = await ticketsService.transferTicket(currentTicketId.value)
    if (response.code === 200) {
      alert('已转接人工客服，请稍候')
      // 更新工单状态 - 使用 map 创建新数组触发响应式更新
      tickets.value = tickets.value.map((t) =>
        t.id === currentTicketId.value ? { ...t, status: 'pending' as TicketStatus } : t
      )
    } else {
      alert(response.message || '转人工失败')
    }
  } catch (error) {
    console.error('转人工失败:', error)
    alert('转人工失败，请重试')
  } finally {
    loading.value = false
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function getTicketTitle(ticket: Ticket): string {
  // 从第一条消息或最后消息中提取标题
  const preview = ticket.last_message
  if (preview.length > 20) {
    return preview.substring(0, 20) + '...'
  }
  return preview
}

function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const oneDayMs = 24 * 60 * 60 * 1000

  if (diff < oneDayMs && date.getDate() === now.getDate()) {
    // 今天
    return date.toTimeString().substring(0, 5)
  } else if (diff < 2 * oneDayMs && date.getDate() === now.getDate() - 1) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }
}

function formatStatus(status: TicketStatus): string {
  const statusMap: Record<TicketStatus, string> = {
    ai_answering: '进行中',
    pending: '进行中',
    in_progress: '进行中',
    completed: '已完结'
  }
  return statusMap[status] || status
}

// 生命周期
onMounted(() => {
  loadTickets()
})

// 监听筛选变化
watch(activeFilter, () => {
  // 如果当前工单不在筛选结果中，清空选择
  if (
    currentTicketId.value &&
    !filteredTickets.value.some((t) => t.id === currentTicketId.value)
  ) {
    currentTicketId.value = null
    currentMessages.value = []
    if (wsConnection) {
      wsConnection.disconnect()
      wsConnection = null
    }
  }
})
</script>

<style scoped>
.employee-page {
  display: flex;
  height: calc(100vh - 64px);
  background: #fafafa;
}

/* 左侧工单列表 */
.sidebar {
  width: 300px;
  background: #ffffff;
  box-shadow: 1px 0 4px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #18181b;
  margin: 0;
}

.filter-buttons {
  display: flex;
  gap: 8px;
  padding: 16px;
}

.filter-btn {
  flex: 1;
  height: 32px;
  background: #fafafa;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  color: #71717a;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: #f4f4f5;
}

.filter-btn.active {
  background: #18181b;
  color: #ffffff;
}

.ticket-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
}

.ticket-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.ticket-card:hover {
  border-color: #18181b;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.ticket-card.active {
  border-color: #18181b;
  background: #fafafa;
}

.ticket-title {
  font-size: 14px;
  font-weight: 500;
  color: #18181b;
  margin-bottom: 8px;
}

.ticket-preview {
  font-size: 12px;
  color: #a1a1aa;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.ticket-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ticket-time {
  font-size: 11px;
  color: #a1a1aa;
}

.ticket-status {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.status-ai_answering,
.status-pending,
.status-in_progress {
  background: #fff7ed;
  color: #f97316;
}

.status-completed {
  background: #f0fdf4;
  color: #22c55e;
}

.empty-list {
  text-align: center;
  padding: 40px 20px;
  color: #a1a1aa;
  font-size: 14px;
}

/* 右侧对话区 */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.status-bar {
  height: 56px;
  background: #f4f9ff;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 24px;
  border-bottom: 1px solid #e5e7eb;
}

.status-icon {
  width: 20px;
  height: 20px;
  color: #18181b;
}

.status-text {
  font-size: 16px;
  font-weight: 600;
  color: #18181b;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 10px;
}

.message-user {
  justify-content: flex-end;
}

.message-assistant,
.message-agent {
  justify-content: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-assistant .message-avatar,
.message-agent .message-avatar {
  background: #18181b;
  color: #ffffff;
}

.message-user .message-avatar {
  background: #f4f9ff;
  color: #18181b;
  order: 2;
}

.message-bubble {
  max-width: 60%;
}

.message-assistant .message-bubble,
.message-agent .message-bubble {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.message-user .message-bubble {
  background: #18181b;
  border-radius: 12px;
  order: 1;
}

.message-content {
  padding: 14px 18px;
  font-size: 14px;
  line-height: 1.5;
}

.message-assistant .message-content,
.message-agent .message-content {
  color: #18181b;
}

.message-user .message-content {
  color: #ffffff;
}

.input-area {
  padding: 16px 24px;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-input {
  width: 100%;
  min-height: 80px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #18181b;
}

.message-input:disabled {
  background: #fafafa;
  cursor: not-allowed;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.transfer-btn,
.send-btn {
  height: 40px;
  padding: 0 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.transfer-btn {
  background: #ffffff;
  border: 1px solid #18181b;
  color: #18181b;
}

.transfer-btn:hover {
  background: #fafafa;
}

.send-btn {
  background: #18181b;
  color: #ffffff;
}

.send-btn:hover {
  background: #27272a;
}

.send-btn:disabled,
.transfer-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-chat-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #a1a1aa;
  padding: 40px 20px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-chat-placeholder p {
  font-size: 16px;
}
</style>
