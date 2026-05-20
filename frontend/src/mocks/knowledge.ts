import type {
  DocumentListApiResponse,
  DocumentDetailApiResponse,
  UploadDocumentApiResponse,
  DocumentListItem,
  DocumentDetail,
  ProcessingProgress
} from '@/types/knowledge'

// Mock 文档列表数据
const mockDocumentList: DocumentListItem[] = [
  {
    id: 101,
    title: 'IT设备故障排查指南.md',
    status: 'completed',
    uploaded_at: '2026-05-20 16:00:00',
    processed_at: '2026-05-20 16:00:25',
    chunk_count: 12,
    qa_count: 8
  },
  {
    id: 102,
    title: '网络配置手册.md',
    status: 'processing',
    uploaded_at: '2026-05-20 16:05:00',
    processed_at: null,
    chunk_count: 0,
    qa_count: 0
  },
  {
    id: 103,
    title: '办公软件使用指南.md',
    status: 'completed',
    uploaded_at: '2026-05-19 10:30:00',
    processed_at: '2026-05-19 10:30:40',
    chunk_count: 15,
    qa_count: 10
  },
  {
    id: 104,
    title: '系统权限管理规范.md',
    status: 'completed',
    uploaded_at: '2026-05-18 14:20:00',
    processed_at: '2026-05-18 14:20:30',
    chunk_count: 8,
    qa_count: 6
  }
]

// Mock 文档详情数据
const mockDocumentDetails: Record<number, DocumentDetail> = {
  101: {
    id: 101,
    title: 'IT设备故障排查指南.md',
    status: 'completed',
    uploaded_at: '2026-05-20 16:00:00',
    processed_at: '2026-05-20 16:00:25',
    chunk_count: 12,
    qa_count: 8,
    file_size_bytes: 15360,
    chunks: [
      {
        id: 1,
        content:
          '## 电脑无法开机故障排查\n\n1. 检查电源连接是否牢固\n2. 确认电源插座是否有电\n3. 观察主机指示灯是否亮起\n4. 尝试按住电源键5秒后重新开机',
        keywords: ['电脑', '开机', '电源', '故障', '排查'],
        qa_pairs: [
          {
            question: '电脑无法开机怎么办？',
            answer: '首先检查电源线是否插紧，确认电源插座是否有电，观察主机是否有任何指示灯亮起。如果问题仍未解决，可能需要进一步检查硬件。'
          }
        ]
      },
      {
        id: 2,
        content: '## 显示器无信号\n\n1. 检查显示器电源线和数据线\n2. 确认显示器输入源选择正确\n3. 尝试更换数据线',
        keywords: ['显示器', '无信号', '数据线', '输入源'],
        qa_pairs: [
          {
            question: '显示器显示无信号怎么办？',
            answer: '请检查显示器电源线和数据线是否插紧，确认显示器输入源选择是否正确（HDMI/VGA/DP等），必要时尝试更换数据线。'
          }
        ]
      }
    ]
  },
  103: {
    id: 103,
    title: '办公软件使用指南.md',
    status: 'completed',
    uploaded_at: '2026-05-19 10:30:00',
    processed_at: '2026-05-19 10:30:40',
    chunk_count: 15,
    qa_count: 10,
    file_size_bytes: 22400,
    chunks: [
      {
        id: 1,
        content: '## Word 常见问题\n\n1. 如何设置页边距\n2. 如何插入页码\n3. 如何生成目录',
        keywords: ['Word', '页边距', '页码', '目录'],
        qa_pairs: [
          {
            question: 'Word如何设置页边距？',
            answer: '在"布局"选项卡中点击"页边距"，选择预设值或自定义边距。'
          }
        ]
      }
    ]
  },
  104: {
    id: 104,
    title: '系统权限管理规范.md',
    status: 'completed',
    uploaded_at: '2026-05-18 14:20:00',
    processed_at: '2026-05-18 14:20:30',
    chunk_count: 8,
    qa_count: 6,
    file_size_bytes: 12800,
    chunks: [
      {
        id: 1,
        content: '## 权限申请流程\n\n1. 提交申请表\n2. 部门主管审批\n3. IT部门授权',
        keywords: ['权限', '申请', '审批', '授权'],
        qa_pairs: [
          {
            question: '如何申请系统权限？',
            answer: '请填写权限申请表，经部门主管审批后提交IT部门授权。'
          }
        ]
      }
    ]
  }
}

// Mock 入库进度数据
let mockProcessingProgress: Record<number, ProcessingProgress> = {}

// Mock 获取文档列表
export const mockGetDocuments = (
  page = 1,
  pageSize = 20,
  status?: string
): DocumentListApiResponse => {
  let filteredList = mockDocumentList

  if (status) {
    filteredList = mockDocumentList.filter((doc) => doc.status === status)
  }

  const start = (page - 1) * pageSize
  const end = start + pageSize
  const items = filteredList.slice(start, end)

  return {
    code: 200,
    message: 'success',
    data: {
      items,
      total: filteredList.length,
      page,
      page_size: pageSize
    }
  }
}

// Mock 获取文档详情
export const mockGetDocumentDetail = (id: number): DocumentDetailApiResponse => {
  const detail = mockDocumentDetails[id]

  if (!detail) {
    return {
      code: 404,
      message: '文档不存在',
      data: null
    }
  }

  return {
    code: 200,
    message: 'success',
    data: detail
  }
}

// Mock 上传文档
export const mockUploadDocument = (file: File): UploadDocumentApiResponse => {
  if (!file.name.endsWith('.md')) {
    return {
      code: 3001,
      message: '文档格式不支持，仅支持 .md 格式',
      data: null
    }
  }

  const newDocId = Math.max(...mockDocumentList.map((d) => d.id), 100) + 1

  const newDoc: DocumentListItem = {
    id: newDocId,
    title: file.name,
    status: 'processing',
    uploaded_at: new Date().toISOString().replace('T', ' ').slice(0, 19),
    processed_at: null,
    chunk_count: 0,
    qa_count: 0
  }

  mockDocumentList.unshift(newDoc)

  // 初始化入库进度
  mockProcessingProgress[newDocId] = {
    document_id: newDocId,
    title: file.name,
    steps: {
      chunk: false,
      vector: false,
      keyword: false,
      qa: false
    },
    current_step: 'chunk'
  }

  // 模拟入库进度（每2秒完成一个步骤）
  setTimeout(() => {
    if (mockProcessingProgress[newDocId]) {
      mockProcessingProgress[newDocId].steps.chunk = true
      mockProcessingProgress[newDocId].current_step = 'vector'
    }
  }, 2000)

  setTimeout(() => {
    if (mockProcessingProgress[newDocId]) {
      mockProcessingProgress[newDocId].steps.vector = true
      mockProcessingProgress[newDocId].current_step = 'keyword'
    }
  }, 4000)

  setTimeout(() => {
    if (mockProcessingProgress[newDocId]) {
      mockProcessingProgress[newDocId].steps.keyword = true
      mockProcessingProgress[newDocId].current_step = 'qa'
    }
  }, 6000)

  setTimeout(() => {
    if (mockProcessingProgress[newDocId]) {
      mockProcessingProgress[newDocId].steps.qa = true
      mockProcessingProgress[newDocId].current_step = null

      // 更新文档状态为已完成
      const doc = mockDocumentList.find((d) => d.id === newDocId)
      if (doc) {
        doc.status = 'completed'
        doc.processed_at = new Date().toISOString().replace('T', ' ').slice(0, 19)
        doc.chunk_count = Math.floor(Math.random() * 10) + 5
        doc.qa_count = Math.floor(Math.random() * 8) + 3
      }
    }
  }, 8000)

  return {
    code: 200,
    message: 'success',
    data: {
      document_id: newDocId,
      title: file.name,
      status: 'processing',
      uploaded_at: newDoc.uploaded_at
    }
  }
}

// Mock 获取入库进度
export const mockGetProcessingProgress = (
  documentId: number
): ProcessingProgress | null => {
  return mockProcessingProgress[documentId] || null
}

// 清理已完成的进度数据
export const clearCompletedProgress = (documentId: number): void => {
  delete mockProcessingProgress[documentId]
}
