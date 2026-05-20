<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getDocuments, uploadDocument } from '@/services/knowledge'
import { mockGetProcessingProgress, clearCompletedProgress } from '@/mocks/knowledge'
import type { DocumentListItem, ProcessingProgress } from '@/types/knowledge'

// 状态
const documents = ref<DocumentListItem[]>([])
const loading = ref(false)
const uploading = ref(false)
const uploadInputRef = ref<HTMLInputElement | null>(null)
const searchQuery = ref('')

// 入库进度（只在 Mock 模式下使用）
const processingDocuments = ref<ProcessingProgress[]>([])

// 状态文案映射
const statusTextMap = {
  processing: '处理中',
  completed: '已入库',
  failed: '失败'
}

// 状态颜色映射
const statusColorMap = {
  processing: '#B45309',
  completed: '#15803D',
  failed: '#DC2626'
}

// 统计数据
const stats = computed(() => {
  const total = documents.value.length
  const indexed = documents.value.filter((doc) => doc.status === 'completed').length
  const processing = documents.value.filter((doc) => doc.status === 'processing').length
  const totalQA = documents.value.reduce((sum, doc) => sum + (doc.qa_count || 0), 0)

  return {
    total,
    indexed,
    processing,
    totalQA
  }
})

// 加载文档列表
const loadDocuments = async () => {
  try {
    loading.value = true
    const response = await getDocuments()

    if (response.code === 200 && response.data) {
      documents.value = response.data.items
    } else {
      console.error('加载文档列表失败:', response.message)
    }
  } catch (error) {
    console.error('加载文档列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 触发文件选择
const handleUploadClick = () => {
  uploadInputRef.value?.click()
}

// 处理文件上传
const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  // 检查文件格式
  if (!file.name.endsWith('.md')) {
    alert('仅支持上传 .md 格式的文件')
    target.value = ''
    return
  }

  try {
    uploading.value = true
    const response = await uploadDocument(file)

    if (response.code === 200 && response.data) {
      // 上传成功，重新加载列表
      await loadDocuments()

      // 如果是 Mock 模式，启动进度监控
      if (import.meta.env.VITE_USE_MOCK === 'true') {
        startProgressMonitoring(response.data.document_id)
      }
    } else {
      alert(response.message || '上传失败')
    }
  } catch (error) {
    console.error('上传文档失败:', error)
    alert('上传失败，请稍后重试')
  } finally {
    uploading.value = false
    target.value = ''
  }
}

// 启动进度监控（Mock 模式）
const startProgressMonitoring = (documentId: number) => {
  const interval = setInterval(() => {
    const progress = mockGetProcessingProgress(documentId)

    if (!progress) {
      clearInterval(interval)
      return
    }

    // 更新或添加进度
    const existingIndex = processingDocuments.value.findIndex(
      (p) => p.document_id === documentId
    )

    if (existingIndex >= 0) {
      processingDocuments.value[existingIndex] = progress
    } else {
      processingDocuments.value.push(progress)
    }

    // 检查是否已完成
    if (!progress.current_step) {
      clearInterval(interval)
      // 延迟移除进度显示，让用户看到完成状态
      setTimeout(() => {
        processingDocuments.value = processingDocuments.value.filter(
          (p) => p.document_id !== documentId
        )
        clearCompletedProgress(documentId)
        // 刷新文档列表
        loadDocuments()
      }, 2000)
    }
  }, 500)
}

// 格式化时间（显示为 YYYY-MM-DD HH:mm）
const formatDateTime = (dateStr: string) => {
  return dateStr.slice(0, 16).replace(' ', ' ')
}

// 当前进度文案
const currentProgressText = computed(() => {
  if (processingDocuments.value.length === 0) return ''

  const progress = processingDocuments.value[0]
  if (!progress) return ''

  const stepNames = {
    chunk: '文档切片',
    vector: '向量化',
    keyword: '关键词提取',
    qa: 'QA 提取'
  }

  const completedSteps = Object.entries(progress.steps)
    .filter(([, completed]) => completed)
    .map(([step]) => stepNames[step as keyof typeof stepNames])

  if (!progress.current_step) {
    return `文档《${progress.title}》已完成入库`
  }

  const currentStepName = stepNames[progress.current_step]

  if (completedSteps.length === 0) {
    return `当前任务：${currentStepName}中...`
  }

  return `当前任务：${currentStepName}中...（已完成：${completedSteps.join('、')}）`
})

// 页面加载时获取文档列表
onMounted(() => {
  loadDocuments()
})
</script>

<template>
  <div class="knowledge-page">
    <div class="kb-main">
      <!-- 页面头部 -->
      <div class="kb-header">
        <div class="kb-header-text">
          <h1 class="kb-title">知识库管理</h1>
          <p class="kb-subtitle">管理和维护 AI 客服的知识文档</p>
        </div>
        <div class="kb-header-actions">
          <div class="search-box">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8" stroke-width="2" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-4.35-4.35" />
            </svg>
            <input v-model="searchQuery" type="text" placeholder="搜索文档..." />
          </div>
          <button class="btn-upload" :disabled="uploading" @click="handleUploadClick">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"
              />
            </svg>
            {{ uploading ? '上传中...' : '上传文档' }}
          </button>
          <input
            ref="uploadInputRef"
            type="file"
            accept=".md"
            style="display: none"
            @change="handleFileChange"
          />
        </div>
      </div>

      <!-- 统计卡片行 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-label">总文档数</div>
          <div class="stat-value">
            <span class="stat-number">{{ stats.total }}</span>
            <span class="stat-unit">篇</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">已索引</div>
          <div class="stat-value">
            <span class="stat-number stat-green">{{ stats.indexed }}</span>
            <span class="stat-unit">篇</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">处理中</div>
          <div class="stat-value">
            <span class="stat-number stat-orange">{{ stats.processing }}</span>
            <span class="stat-unit">篇</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">QA 条目</div>
          <div class="stat-value">
            <span class="stat-number stat-accent">{{ stats.totalQA }}</span>
            <span class="stat-unit">条</span>
          </div>
        </div>
      </div>

      <!-- 文档列表表格 -->
      <div class="kb-table-container">
        <table class="kb-table">
          <thead>
            <tr>
              <th class="col-name">文档名称</th>
              <th class="col-type">类型</th>
              <th class="col-size">大小</th>
              <th class="col-status">状态</th>
              <th class="col-time">上传时间</th>
              <th class="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="loading-cell">加载中...</td>
            </tr>
            <tr v-if="!loading && documents.length === 0">
              <td colspan="6" class="empty-cell">暂无文档，点击右上角上传按钮添加文档</td>
            </tr>
            <tr v-for="doc in documents" v-else :key="doc.id" class="doc-row">
              <td class="doc-name">
                <div class="doc-name-content">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"
                    />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 2v6h6M16 13H8M16 17H8M10 9H8" />
                  </svg>
                  <span>{{ doc.title }}</span>
                </div>
              </td>
              <td class="doc-type">Markdown</td>
              <td class="doc-size">-</td>
              <td class="doc-status">
                <span
                  class="status-badge"
                  :style="{ backgroundColor: statusColorMap[doc.status] + '20', color: statusColorMap[doc.status] }"
                >
                  {{ statusTextMap[doc.status] }}
                </span>
              </td>
              <td class="doc-time">{{ formatDateTime(doc.uploaded_at) }}</td>
              <td class="doc-actions">
                <button class="btn-action" title="查看">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" stroke-width="2" />
                  </svg>
                </button>
                <button class="btn-action" title="删除">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6"
                    />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 底部入库状态监控条 -->
      <div v-if="currentProgressText" class="kb-progress-bar">
        <div class="progress-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-width="2" />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6v6l4 2"
            />
          </svg>
        </div>
        <span class="progress-text">{{ currentProgressText }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fafafa;
}

.kb-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 28px;
  gap: 20px;
  overflow: hidden;
}

/* 页面头部 */
.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.kb-header-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kb-title {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #18181b;
  margin: 0;
}

.kb-subtitle {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #71717a;
  margin: 0;
}

.kb-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 260px;
  height: 40px;
  padding: 0 14px;
  background: #ffffff;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
}

.search-box svg {
  flex-shrink: 0;
  color: #a1a1aa;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 13px;
  color: #18181b;
  background: transparent;
}

.search-box input::placeholder {
  color: #a1a1aa;
}

.btn-upload {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  height: 40px;
  background: #18181b;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-upload:hover:not(:disabled) {
  background: #27272a;
  transform: translateY(-1px);
}

.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 统计卡片行 */
.stats-row {
  display: flex;
  gap: 16px;
}

.stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.stat-label {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #a1a1aa;
}

.stat-value {
  display: flex;
  align-items: flex-end;
  gap: 6px;
}

.stat-number {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #18181b;
}

.stat-number.stat-green {
  color: #15803d;
}

.stat-number.stat-orange {
  color: #b45309;
}

.stat-number.stat-accent {
  color: #52525b;
}

.stat-unit {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 13px;
  font-weight: 400;
  color: #a1a1aa;
  padding-bottom: 2px;
}

/* 表格容器 */
.kb-table-container {
  flex: 1;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: auto;
}

.kb-table {
  width: 100%;
  border-collapse: collapse;
}

.kb-table thead {
  position: sticky;
  top: 0;
  background: #fafafa;
  z-index: 1;
}

.kb-table th {
  padding: 16px 20px;
  text-align: left;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #71717a;
  border-bottom: 1px solid #e4e4e7;
}

.kb-table td {
  padding: 16px 20px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 14px;
  color: #18181b;
  border-bottom: 1px solid #f4f4f5;
}

.col-name {
  width: auto;
}

.col-type {
  width: 90px;
}

.col-size {
  width: 80px;
}

.col-status {
  width: 100px;
}

.col-time {
  width: 150px;
}

.col-actions {
  width: 120px;
}

.doc-row {
  transition: background-color 0.2s;
}

.doc-row:hover {
  background: #fafafa;
}

.doc-name-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.doc-name-content svg {
  flex-shrink: 0;
  color: #52525b;
}

.doc-name-content span {
  font-weight: 500;
}

.doc-type,
.doc-size,
.doc-time {
  color: #71717a;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.doc-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: #71717a;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action:hover {
  background: #f4f4f5;
  color: #18181b;
}

.loading-cell,
.empty-cell {
  text-align: center;
  padding: 40px 20px;
  color: #a1a1aa;
  font-size: 14px;
}

/* 底部进度条 */
.kb-progress-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.progress-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f4f4f5;
  border-radius: 8px;
  color: #52525b;
}

.progress-icon svg {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.progress-text {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 13px;
  color: #52525b;
}
</style>
