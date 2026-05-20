import api from './api'
import type {
  DocumentListApiResponse,
  DocumentDetailApiResponse,
  UploadDocumentApiResponse
} from '@/types/knowledge'
import {
  mockGetDocuments,
  mockGetDocumentDetail,
  mockUploadDocument
} from '@/mocks/knowledge'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

/**
 * 获取知识库文档列表
 */
export const getDocuments = async (
  page = 1,
  pageSize = 20,
  status?: string
): Promise<DocumentListApiResponse> => {
  if (USE_MOCK) {
    return Promise.resolve(mockGetDocuments(page, pageSize, status))
  }

  const params: Record<string, string | number> = { page, page_size: pageSize }
  if (status) {
    params.status = status
  }

  const response = await api.get<DocumentListApiResponse>('/knowledge/documents', {
    params
  })
  return response.data
}

/**
 * 获取知识库文档详情
 */
export const getDocumentDetail = async (
  id: number
): Promise<DocumentDetailApiResponse> => {
  if (USE_MOCK) {
    return Promise.resolve(mockGetDocumentDetail(id))
  }

  const response = await api.get<DocumentDetailApiResponse>(
    `/knowledge/documents/${id}`
  )
  return response.data
}

/**
 * 上传知识库文档
 */
export const uploadDocument = async (
  file: File,
  title?: string
): Promise<UploadDocumentApiResponse> => {
  if (USE_MOCK) {
    return Promise.resolve(mockUploadDocument(file))
  }

  const formData = new FormData()
  formData.append('file', file)
  if (title) {
    formData.append('title', title)
  }

  const response = await api.post<UploadDocumentApiResponse>(
    '/knowledge/documents',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  )
  return response.data
}
