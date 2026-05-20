import type { ApiResponse } from './auth'

// 文档状态
export type DocumentStatus = 'processing' | 'completed' | 'failed'

// 文档列表项
export interface DocumentListItem {
  id: number
  title: string
  status: DocumentStatus
  uploaded_at: string
  processed_at: string | null
  chunk_count: number
  qa_count: number
}

// 文档详情中的 chunk
export interface DocumentChunk {
  id: number
  content: string
  keywords: string[]
  qa_pairs: Array<{
    question: string
    answer: string
  }>
}

// 文档详情
export interface DocumentDetail {
  id: number
  title: string
  status: DocumentStatus
  uploaded_at: string
  processed_at: string | null
  chunk_count: number
  qa_count: number
  file_size_bytes: number
  chunks: DocumentChunk[]
}

// 文档列表响应
export interface DocumentListResponse {
  items: DocumentListItem[]
  total: number
  page: number
  page_size: number
}

// 上传文档响应
export interface UploadDocumentResponse {
  document_id: number
  title: string
  status: DocumentStatus
  uploaded_at: string
}

// API 响应类型
export type DocumentListApiResponse = ApiResponse<DocumentListResponse>
export type DocumentDetailApiResponse = ApiResponse<DocumentDetail>
export type UploadDocumentApiResponse = ApiResponse<UploadDocumentResponse>

// 入库进度步骤
export type ProcessingStep = 'chunk' | 'vector' | 'keyword' | 'qa'

// 入库进度状态
export interface ProcessingProgress {
  document_id: number
  title: string
  steps: {
    chunk: boolean
    vector: boolean
    keyword: boolean
    qa: boolean
  }
  current_step: ProcessingStep | null
}
