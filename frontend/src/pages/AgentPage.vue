<template>
  <div class="agent-page">
    <!-- 左侧工单列表 -->
    <div class="left-panel">
      <div class="panel-header">
        <h2 class="panel-title">工单列表</h2>
      </div>

      <!-- 状态筛选按钮 -->
      <div class="filter-tabs">
        <button
          v-for="tab in statusTabs"
          :key="tab.status"
          :class="['tab-button', { active: currentTab === tab.status }]"
          @click="currentTab = tab.status"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 工单卡片列表 -->
      <div class="ticket-list">
        <div
          v-for="ticket in filteredTickets"
          :key="ticket.id"
          :class="['ticket-card', { active: currentTicketId === ticket.id }]"
          @click="selectTicket(ticket.id)"
        >
          <div class="ticket-card-header">
            <span class="ticket-number">
              #{{ ticket.id }}
              {{
                'user_id' in ticket ? userDisplayNames[ticket.user_id] || '员工' : '员工'
              }}
            </span>
            <span :class="['status-dot', ticket.status]"></span>
          </div>
          <p class="ticket-preview">
            {{
              'last_message' in ticket
                ? ticket.last_message.substring(0, 20)
                : '暂无消息'
            }}...
          </p>
          <div class="ticket-meta">
            <span v-if="'wait_time_seconds' in ticket" class="wait-time">
              等待 {{ formatWaitTime(ticket.wait_time_seconds) }}
            </span>
            <span v-else class="wait-time">
              等待 {{ getWaitTime(ticket.created_at) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 中间对话区 -->
    <div class="center-panel">
      <template v-if="currentTicketId && currentTicket">
        <!-- 对话头部 -->
        <div class="chat-header">
          <div class="user-info">
            <div class="user-avatar">
              <i class="icon-user"></i>
            </div>
            <div class="user-details">
              <h3 class="user-name">
                {{ userDisplayNames[currentTicket.user_id] || '员工' }}
              </h3>
              <div class="ticket-status-info">
                <span class="ticket-id">#{{ currentTicketId }}</span>
                <span :class="['status-badge', currentTicket.status]">
                  {{ getStatusText(currentTicket.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 对话消息区 -->
        <div ref="chatBodyRef" class="chat-body">
          <div v-for="msg in currentTicket.messages" :key="msg.id" :class="['message', msg.role]">
            <div v-if="msg.role !== 'user'" class="message-avatar">
              <i :class="msg.role === 'assistant' ? 'icon-bot' : 'icon-headset'"></i>
            </div>
            <div class="message-content">
              <div class="message-bubble">
                <p>{{ msg.content }}</p>
                <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
              </div>
            </div>
            <div v-if="msg.role === 'user'" class="message-avatar">
              <i class="icon-user"></i>
            </div>
          </div>
        </div>

        <!-- 输入框区域 -->
        <div class="chat-input-bar">
          <div class="input-group">
            <input
              v-model="messageInput"
              type="text"
              class="message-input"
              placeholder="输入回复内容..."
              :disabled="isTicketCompleted || isSending"
              @keypress.enter="handleSendMessage"
            />
            <button
              class="send-button"
              :disabled="!messageInput.trim() || isTicketCompleted || isSending"
              @click="handleSendMessage"
            >
              发送
            </button>
          </div>
          <div class="action-buttons">
            <button
              v-if="currentTicket.status === 'in_progress'"
              class="complete-button"
              @click="handleCompleteTicket"
            >
              结束工单
            </button>
            <button
              v-if="currentTicket.status === 'in_progress'"
              class="resolved-button"
              @click="handleCompleteTicket"
            >
              已解决
            </button>
            <button
              v-if="currentTicket.status === 'in_progress'"
              class="suggest-button"
              :disabled="isLoadingSuggestion"
              @click="handleGetSuggestion"
            >
              {{ isLoadingSuggestion ? '生成中...' : '智能回答' }}
            </button>
          </div>
        </div>
      </template>

      <!-- 空状态提示 -->
      <div v-else class="empty-state">
        <i class="icon-inbox"></i>
        <p>AI 正在处理中...</p>
      </div>
    </div>

    <!-- 右侧 AI 辅助面板 -->
    <div class="right-panel">
      <div class="panel-header">
        <i class="icon-sparkles-header"></i>
        <h2 class="panel-title">AI 辅助</h2>
      </div>

      <template v-if="currentTicketId && aiAssistInfo">
        <div class="assist-section">
          <h3 class="section-title">意图识别</h3>
          <div class="intent-card">
            <div class="intent-item">
              <span class="label">一级意图：</span>
              <span class="value">{{ aiAssistInfo.intent.level1 }}</span>
            </div>
            <div class="intent-item">
              <span class="label">二级意图：</span>
              <span class="value">{{ aiAssistInfo.intent.level2 }}</span>
            </div>
            <div v-if="aiAssistInfo.intent.is_ambiguous" class="intent-warning">
              意图不明确，建议进一步询问
            </div>
          </div>
        </div>

        <div class="assist-section">
          <h3 class="section-title">用户画像</h3>
          <div class="profile-card">
            <div class="profile-item">
              <span class="label">常问领域：</span>
            </div>
            <div class="domain-list">
              <div
                v-for="(count, domain) in aiAssistInfo.user_profile.query_domains"
                :key="domain"
                class="domain-tag"
              >
                {{ domain }} ({{ count }})
              </div>
            </div>
          </div>
        </div>

        <div v-if="suggestedReply" class="assist-section">
          <h3 class="section-title">智能建议回复</h3>
          <div class="suggestion-card">
            <p class="suggestion-text">{{ suggestedReply }}</p>
            <div class="suggestion-actions">
              <button class="adopt-button" @click="adoptSuggestion">采用建议</button>
              <button class="regenerate-button" @click="handleGetSuggestion">重新生成</button>
            </div>
          </div>
        </div>

        <div class="assist-section">
          <h3 class="section-title">关联知识</h3>
          <div class="knowledge-card">
            <div class="knowledge-item">
              <i class="icon-file"></i>
              <span class="knowledge-name">硬件故障排查指南.md</span>
            </div>
          </div>
        </div>
      </template>

      <div v-else class="empty-state-panel">
        <i class="icon-sparkles"></i>
        <p>请从左侧选择工单</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { TicketDetail, PendingTicketListItem, TicketStatus } from '../types/ticket'
import type { AIAssistInfo } from '../types/ai-assist'
import { ticketsService } from '../services/tickets'
import { getAIAssist, suggestReply } from '../services/ai-assist'
import { useWebSocket } from '../composables/useWebSocket'

// 用户昵称映射（根据 user_id 获取 display_name）
const userDisplayNames: Record<number, string> = {
  1: '张三',
  2: '李四',
  3: '王五',
  5: '赵六',
  6: '孙七',
  7: '周八'
}

// 状态筛选
const statusTabs = [
  { status: 'pending', label: '待处理' },
  { status: 'in_progress', label: '处理中' },
  { status: 'completed', label: '已完成' }
] as const

const currentTab = ref<'pending' | 'in_progress' | 'completed'>('pending')

// 工单数据
const pendingTickets = ref<PendingTicketListItem[]>([])
const inProgressTickets = ref<TicketDetail[]>([])
const completedTickets = ref<TicketDetail[]>([])
const currentTicketId = ref<number | null>(null)
const currentTicket = ref<TicketDetail | null>(null)

// AI 辅助数据
const aiAssistInfo = ref<AIAssistInfo | null>(null)
const suggestedReply = ref<string | null>(null)
const isLoadingSuggestion = ref(false)

// 消息输入
const messageInput = ref('')
const isSending = ref(false)
const chatBodyRef = ref<HTMLElement | null>(null)

// WebSocket 连接
let wsConnection: ReturnType<typeof useWebSocket> | null = null

// 筛选后的工单列表
const filteredTickets = computed(() => {
  if (currentTab.value === 'pending') {
    return pendingTickets.value
  } else if (currentTab.value === 'in_progress') {
    return inProgressTickets.value
  } else {
    return completedTickets.value
  }
})

// 当前工单是否已完成
const isTicketCompleted = computed(() => {
  return currentTicket.value?.status === 'completed'
})

// 加载工单列表
async function loadTickets() {
  try {
    if (currentTab.value === 'pending') {
      // 加载待处理工单（使用专用接口）
      const response = await ticketsService.getPendingTickets({
        page: 1,
        page_size: 50
      })
      if (response.code === 200 && response.data) {
        pendingTickets.value = response.data.items
      }
    } else {
      // 加载处理中和已完成工单（使用通用接口）
      const response = await ticketsService.getTickets({
        page: 1,
        page_size: 50,
        status: currentTab.value
      })
      if (response.code === 200 && response.data) {
        // 需要同时加载详情以获取 user_id
        const detailsPromises = response.data.items.map((item) =>
          ticketsService.getTicketDetail(item.id)
        )
        const detailsResponses = await Promise.all(detailsPromises)

        const ticketsWithDetails = response.data.items.map((item, index) => {
          const detailResponse = detailsResponses[index]
          const detail =
            detailResponse && detailResponse.code === 200 && detailResponse.data
              ? detailResponse.data
              : null
          return {
            ...item,
            user_id: detail?.user_id || 0,
            agent_id: detail?.agent_id || null,
            messages: detail?.messages || []
          } as TicketDetail
        })

        if (currentTab.value === 'in_progress') {
          inProgressTickets.value = ticketsWithDetails
        } else {
          completedTickets.value = ticketsWithDetails
        }
      }
    }
  } catch (error) {
    console.error('加载工单列表失败:', error)
  }
}

// 选择工单
async function selectTicket(ticketId: number) {
  // 如果已经是当前工单，不重复加载
  if (currentTicketId.value === ticketId) return

  // 断开之前的 WebSocket 连接
  if (wsConnection) {
    wsConnection.disconnect()
    wsConnection = null
  }

  currentTicketId.value = ticketId

  // 加载工单详情
  try {
    const response = await ticketsService.getTicketDetail(ticketId)
    if (response.code === 200 && response.data) {
      currentTicket.value = response.data

      // 如果是待处理工单，自动接单
      if (currentTicket.value.status === 'pending') {
        await handlePickTicket(ticketId)
      }

      // 建立 WebSocket 连接
      wsConnection = useWebSocket(ticketId)
      wsConnection.onMessage((message) => {
        if (message.type === 'new_message') {
          currentTicket.value?.messages.push({
            id: message.data.message_id,
            role: message.data.role,
            content: message.data.content,
            timestamp: message.data.timestamp
          })
          nextTick(() => scrollToBottom())
        }
      })
      wsConnection.connect()

      // 加载 AI 辅助信息
      await loadAIAssist(ticketId)

      // 滚动到底部
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('加载工单详情失败:', error)
  }
}

// 接单
async function handlePickTicket(ticketId: number) {
  try {
    const response = await ticketsService.pickTicket(ticketId)
    if (response.code === 200) {
      // 更新工单状态
      if (currentTicket.value) {
        currentTicket.value.status = 'in_progress'
      }
      // 刷新工单列表
      await loadTickets()
    }
  } catch (error) {
    console.error('接单失败:', error)
  }
}

// 发送消息
async function handleSendMessage() {
  if (!messageInput.value.trim() || !currentTicketId.value || isSending.value) return

  const content = messageInput.value.trim()
  isSending.value = true

  try {
    // 在 Mock 模式下，通过 WebSocket 推送消息
    if (import.meta.env.VITE_USE_MOCK === 'true' && wsConnection) {
      const tempMessage = {
        id: Date.now(),
        role: 'agent' as const,
        content,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19)
      }

      wsConnection.mockPushMessage({
        type: 'new_message',
        data: {
          message_id: tempMessage.id,
          ticket_id: currentTicketId.value,
          role: 'agent',
          content,
          timestamp: tempMessage.timestamp
        }
      })

      messageInput.value = ''
    }
  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
    isSending.value = false
  }
}

// 结束工单
async function handleCompleteTicket() {
  if (!currentTicketId.value) return

  try {
    const response = await ticketsService.completeTicket(currentTicketId.value)
    if (response.code === 200) {
      if (currentTicket.value) {
        currentTicket.value.status = 'completed'
      }
      // 刷新工单列表
      await loadTickets()
    }
  } catch (error) {
    console.error('结束工单失败:', error)
  }
}

// 加载 AI 辅助信息
async function loadAIAssist(ticketId: number) {
  try {
    const response = await getAIAssist(ticketId)
    if (response.code === 200 && response.data) {
      aiAssistInfo.value = response.data
    }
  } catch (error) {
    console.error('加载 AI 辅助信息失败:', error)
  }
}

// 获取智能回答建议
async function handleGetSuggestion() {
  if (!currentTicketId.value || isLoadingSuggestion.value) return

  isLoadingSuggestion.value = true

  try {
    const response = await suggestReply(currentTicketId.value)
    if (response.code === 200 && response.data) {
      suggestedReply.value = response.data.suggested_reply
    }
  } catch (error) {
    console.error('获取智能回答建议失败:', error)
  } finally {
    isLoadingSuggestion.value = false
  }
}

// 采用建议回复
function adoptSuggestion() {
  if (suggestedReply.value) {
    messageInput.value = suggestedReply.value
  }
}

// 滚动到底部
function scrollToBottom() {
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}

// 获取等待时长
function getWaitTime(createdAt: string): string {
  const created = new Date(createdAt)
  const now = new Date()
  const diffMinutes = Math.floor((now.getTime() - created.getTime()) / 60000)

  if (diffMinutes < 60) {
    return `${diffMinutes} 分钟`
  } else {
    const hours = Math.floor(diffMinutes / 60)
    return `${hours} 小时`
  }
}

// 格式化等待时长（从秒转换）
function formatWaitTime(seconds: number): string {
  if (seconds < 60) {
    return `${seconds} 秒`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    return `${minutes} 分钟`
  } else {
    const hours = Math.floor(seconds / 3600)
    return `${hours} 小时`
  }
}

// 获取状态文本
function getStatusText(status: TicketStatus): string {
  const statusMap: Record<TicketStatus, string> = {
    ai_answering: 'AI回答中',
    pending: '待处理',
    in_progress: '处理中',
    completed: '已完成'
  }
  return statusMap[status]
}

// 格式化时间
function formatTime(timestamp: string): string {
  return timestamp.substring(11, 16)
}

// 监听筛选切换
watch(currentTab, () => {
  loadTickets()
  // 切换筛选时清空当前选中工单
  currentTicketId.value = null
  currentTicket.value = null
  aiAssistInfo.value = null
  suggestedReply.value = null
  if (wsConnection) {
    wsConnection.disconnect()
    wsConnection = null
  }
})

// 初始加载
loadTickets()
</script>

<style scoped>
.agent-page {
  display: flex;
  height: calc(100vh - 64px);
  background: #fafafa;
}

/* 左侧工单列表 */
.left-panel {
  width: 300px;
  background: #f4f4f5;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #18181b;
  margin: 0;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.tab-button {
  flex: 1;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: #ffffff;
  color: #a1a1aa;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-button.active {
  background: #18181b;
  color: #ffffff;
}

.ticket-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
}

.ticket-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.ticket-card:hover {
  background: #ffffff;
}

.ticket-card.active {
  background: #ffffff;
  box-shadow: 0 0 0 2px #18181b;
}

.ticket-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.ticket-number {
  font-size: 14px;
  font-weight: 600;
  color: #18181b;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-dot.pending {
  background: #f59e0b;
}

.status-dot.in_progress {
  background: #10b981;
}

.status-dot.completed {
  background: #71717a;
}

.ticket-preview {
  font-size: 13px;
  color: #a1a1aa;
  margin: 0 0 8px 0;
}

.ticket-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.wait-time {
  font-size: 11px;
  color: #a1a1aa;
  font-family: monospace;
}

/* 中间对话区 */
.center-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.chat-header {
  height: 68px;
  background: #ffffff;
  border-bottom: 1px solid #e4e4e7;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  gap: 14px;
  align-items: center;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f4f4f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-user,
.icon-bot,
.icon-headset,
.icon-inbox,
.icon-sparkles {
  font-size: 18px;
  color: #18181b;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #18181b;
  margin: 0;
}

.ticket-status-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.ticket-id {
  font-size: 12px;
  color: #a1a1aa;
  font-family: monospace;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-family: monospace;
}

.status-badge.pending {
  background: #fef3c7;
  color: #b45309;
}

.status-badge.in_progress {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.completed {
  background: #f4f4f5;
  color: #52525b;
}

.chat-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message.user {
  justify-content: flex-end;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f4f4f5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-content {
  max-width: 60%;
}

.message-bubble {
  padding: 14px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message.user .message-bubble {
  background: #18181b;
  color: #ffffff;
}

.message.assistant .message-bubble,
.message.agent .message-bubble {
  background: #ffffff;
  border: 1px solid #e4e4e7;
  color: #18181b;
}

.message-bubble p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.message-time {
  font-size: 10px;
  font-family: monospace;
  opacity: 0.6;
}

.message.user .message-time {
  text-align: right;
}

.chat-input-bar {
  background: #ffffff;
  border-top: 1px solid #e4e4e7;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

.message-input {
  flex: 1;
  height: 44px;
  padding: 0 16px;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  font-size: 14px;
  background: #fafafa;
}

.message-input:focus {
  outline: none;
  border-color: #18181b;
}

.message-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button {
  height: 44px;
  padding: 0 24px;
  border: none;
  border-radius: 8px;
  background: #18181b;
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.send-button:hover:not(:disabled) {
  opacity: 0.8;
}

.send-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.complete-button,
.suggest-button {
  height: 36px;
  padding: 0 16px;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  background: #ffffff;
  color: #18181b;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.complete-button:hover,
.suggest-button:hover:not(:disabled) {
  background: #f4f4f5;
}

.suggest-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #a1a1aa;
}

.empty-state .icon-inbox {
  font-size: 48px;
}

/* 右侧 AI 辅助面板 */
.right-panel {
  width: 320px;
  background: #ffffff;
  border-left: 1px solid #e4e4e7;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e4e7;
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: #18181b;
  margin: 0;
}

.icon-sparkles-header::before {
  content: '✨';
  font-size: 20px;
}

.assist-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #18181b;
  margin: 0;
}

.intent-card,
.profile-card,
.suggestion-card {
  padding: 14px;
  border-radius: 8px;
  border: 1px solid #e4e4e7;
  background: #fafafa;
}

.intent-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.intent-item:last-child {
  margin-bottom: 0;
}

.label {
  font-size: 13px;
  color: #71717a;
}

.value {
  font-size: 13px;
  color: #18181b;
  font-weight: 500;
}

.intent-warning {
  margin-top: 8px;
  padding: 8px;
  border-radius: 4px;
  background: #fef3c7;
  color: #b45309;
  font-size: 12px;
}

.profile-item {
  margin-bottom: 8px;
}

.domain-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.domain-tag {
  padding: 4px 10px;
  border-radius: 12px;
  background: #f4f4f5;
  color: #18181b;
  font-size: 12px;
}

.suggestion-text {
  font-size: 13px;
  color: #52525b;
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.suggestion-actions {
  display: flex;
  gap: 8px;
}

.adopt-button {
  flex: 1;
  height: 36px;
  border: none;
  border-radius: 6px;
  background: #dbeafe;
  color: #18181b;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.adopt-button:hover {
  opacity: 0.8;
}

.regenerate-button {
  flex: 1;
  height: 36px;
  border: 1px solid #e4e4e7;
  border-radius: 6px;
  background: #fafafa;
  color: #71717a;
  font-size: 12px;
  font-weight: normal;
  cursor: pointer;
  transition: background 0.2s;
}

.regenerate-button:hover {
  background: #f4f4f5;
}

.resolved-button {
  height: 40px;
  padding: 0 18px;
  border: none;
  border-radius: 8px;
  background: #d1fae5;
  color: #065f46;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.resolved-button:hover {
  opacity: 0.8;
}

.knowledge-card {
  padding: 14px;
  border-radius: 8px;
  border: 1px solid #e4e4e7;
  background: #fafafa;
}

.knowledge-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 6px;
  background: #f4f4f5;
}

.icon-file::before {
  content: '📄';
  font-size: 14px;
}

.knowledge-name {
  font-size: 12px;
  color: #71717a;
}

.empty-state-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #a1a1aa;
}

.empty-state-panel .icon-sparkles {
  font-size: 48px;
}

/* 图标字体（使用简单的文本替代） */
.icon-user::before {
  content: '👤';
}

.icon-bot::before {
  content: '🤖';
}

.icon-headset::before {
  content: '🎧';
}

.icon-inbox::before {
  content: '📥';
}

.icon-sparkles::before {
  content: '✨';
}
</style>
