# 接口契约

> 前端 Mock 和后端实现的唯一对齐依据。任何变更必须同步更新本文件。

**版本**：V1.0  
**更新日期**：2026-05-20  
**基础 URL**：`http://localhost:8000`

---

## 通用约定

### 统一响应格式

**成功响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误响应**：
```json
{
  "code": <错误码>,
  "message": "<错误描述>",
  "data": null
}
```

**分页响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 通用错误码

| 错误码 | 描述 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token失效或未登录） |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 请求频率限制 |
| 500 | 服务器内部错误 |
| 1001 | 用户名或密码错误 |
| 2001 | 工单不存在 |
| 2002 | 工单状态不允许该操作 |
| 2003 | 工单已被其他坐席接单 |
| 3001 | 文档格式不支持 |
| 3002 | 文档入库失败 |
| 4001 | AI服务调用失败（百炼平台） |
| 4002 | AI服务降级（使用关键词回退） |

### 认证机制

所有接口（除 `/api/auth/login` 和 `/health`）需在请求头中携带：
```
Authorization: Bearer <access_token>
```

---

## 接口清单

### 1. 登录

**接口**：`POST /api/auth/login`

**请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "user": {
      "user_id": 1,
      "username": "zhangsan",
      "display_name": "张三",
      "role": "employee",
      "created_at": "2026-05-20 10:00:00"
    }
  }
}
```

**字段说明**：
- `display_name`（可选）：用户显示名称/昵称，用于界面展示。如后端未返回此字段，前端应降级显示 `username`

**响应（失败 401）**：
```json
{
  "code": 1001,
  "message": "用户名或密码错误",
  "data": null
}
```

---

### 2. 发起咨询（员工端）

**接口**：`POST /api/tickets`

**请求体**：
```json
{
  "message": "我的电脑无法开机，怎么办？"
}
```

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "ticket_id": 1001,
    "status": "ai_answering",
    "created_at": "2026-05-20 14:30:00",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "我的电脑无法开机，怎么办？",
        "timestamp": "2026-05-20 14:30:00"
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "您好！根据您的描述，建议先检查：1. 电源线是否插紧；2. 电源插座是否有电；3. 主机电源按钮是否按下后有指示灯亮起。请问您的电脑是否有任何指示灯显示？",
        "timestamp": "2026-05-20 14:30:03"
      }
    ]
  }
}
```

**响应（失败 4001）**：
```json
{
  "code": 4001,
  "message": "AI服务调用失败，请稍后重试",
  "data": null
}
```

---

### 3. 获取工单列表（员工端）

**接口**：`GET /api/tickets`

**请求参数**：
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |
| status | string | 否 | 工单状态过滤（ai_answering, pending, in_progress, completed） |

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1001,
        "status": "completed",
        "last_message": "感谢您的帮助，问题已解决！",
        "created_at": "2026-05-20 14:30:00",
        "updated_at": "2026-05-20 14:45:00",
        "message_count": 8
      },
      {
        "id": 1002,
        "status": "in_progress",
        "last_message": "请您稍等，我为您查询一下...",
        "created_at": "2026-05-20 15:00:00",
        "updated_at": "2026-05-20 15:05:00",
        "message_count": 4
      }
    ],
    "total": 25,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 4. 获取工单详情

**接口**：`GET /api/tickets/{id}`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 工单ID |

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1001,
    "status": "completed",
    "created_at": "2026-05-20 14:30:00",
    "updated_at": "2026-05-20 14:45:00",
    "user_id": 5,
    "agent_id": 12,
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "我的电脑无法开机，怎么办？",
        "timestamp": "2026-05-20 14:30:00"
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "您好！根据您的描述，建议先检查...",
        "timestamp": "2026-05-20 14:30:03"
      }
    ]
  }
}
```

**响应（失败 404）**：
```json
{
  "code": 2001,
  "message": "工单不存在",
  "data": null
}
```

---

### 5. 转人工（员工端）

**接口**：`PUT /api/tickets/{id}/transfer`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 工单ID |

**请求体**：
```json
{}
```

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "ticket_id": 1001,
    "status": "pending",
    "updated_at": "2026-05-20 14:35:00"
  }
}
```

**响应（失败 400）**：
```json
{
  "code": 2002,
  "message": "当前工单状态不允许转人工",
  "data": null
}
```

---

### 6. 获取待处理工单列表（坐席端）

**接口**：`GET /api/tickets/pending`

**请求参数**：
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1003,
        "status": "pending",
        "last_message": "AI无法解决，需要人工帮助",
        "created_at": "2026-05-20 15:10:00",
        "wait_time_seconds": 120,
        "user_id": 8,
        "message_count": 5
      }
    ],
    "total": 3,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 7. 坐席接单

**接口**：`PUT /api/tickets/{id}/pick`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 工单ID |

**请求体**：
```json
{}
```

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "ticket_id": 1003,
    "status": "in_progress",
    "agent_id": 12,
    "picked_at": "2026-05-20 15:12:00"
  }
}
```

**响应（失败 400）**：
```json
{
  "code": 2003,
  "message": "工单已被其他坐席接单",
  "data": null
}
```

---

### 8. 结束工单（坐席端）

**接口**：`PUT /api/tickets/{id}/complete`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 工单ID |

**请求体**：
```json
{}
```

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "ticket_id": 1003,
    "status": "completed",
    "completed_at": "2026-05-20 15:20:00"
  }
}
```

---

### 9. 发送消息

**接口**：`POST /api/tickets/{id}/messages`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 工单ID |

**请求体**：
```json
{
  "content": "好的，我已经按照您的建议操作了，现在电脑可以开机了！"
}
```

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message_id": 15,
    "ticket_id": 1003,
    "role": "user",
    "content": "好的，我已经按照您的建议操作了，现在电脑可以开机了！",
    "timestamp": "2026-05-20 15:18:00"
  }
}
```

---

### 10. 获取消息历史

**接口**：`GET /api/tickets/{id}/messages`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 工单ID |

**请求参数**：
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认50 |

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "role": "user",
        "content": "我的电脑无法开机，怎么办？",
        "timestamp": "2026-05-20 14:30:00"
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "您好！根据您的描述，建议先检查...",
        "timestamp": "2026-05-20 14:30:03"
      }
    ],
    "total": 8,
    "page": 1,
    "page_size": 50
  }
}
```

---

### 11. 获取AI辅助信息（坐席端）

**接口**：`GET /api/tickets/{id}/ai-assist`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 工单ID |

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "ticket_id": 1003,
    "intent": {
      "level1": "IT问题",
      "level2": "硬件故障",
      "is_ambiguous": false
    },
    "user_profile": {
      "user_id": 8,
      "query_domains": {
        "IT问题": 3,
        "网络问题": 1
      },
      "last_updated": "2026-05-20 15:12:00"
    },
    "suggested_keywords": ["电脑", "开机", "电源", "故障排查"]
  }
}
```

---

### 12. 生成建议回复（坐席端）

**接口**：`POST /api/tickets/{id}/suggest-reply`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 工单ID |

**请求体**：
```json
{}
```

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "suggested_reply": "根据您的描述，建议您尝试以下步骤：1. 检查电源线是否插紧；2. 尝试更换电源插座；3. 观察主机是否有任何指示灯亮起。如果问题仍未解决，可能需要进一步检查硬件。"
  }
}
```

**响应（失败 4001）**：
```json
{
  "code": 4001,
  "message": "AI服务调用失败，请稍后重试",
  "data": null
}
```

---

### 13. 上传知识库文档

**接口**：`POST /api/knowledge/documents`

**请求体**（multipart/form-data）：
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| file | file | 是 | .md 文件 |
| title | string | 否 | 文档标题（不提供则使用文件名） |

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "document_id": 101,
    "title": "IT设备故障排查指南.md",
    "status": "processing",
    "uploaded_at": "2026-05-20 16:00:00"
  }
}
```

**响应（失败 400）**：
```json
{
  "code": 3001,
  "message": "文档格式不支持，仅支持 .md 格式",
  "data": null
}
```

---

### 14. 获取知识库文档列表

**接口**：`GET /api/knowledge/documents`

**请求参数**：
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |
| status | string | 否 | 状态过滤（processing, completed, failed） |

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 101,
        "title": "IT设备故障排查指南.md",
        "status": "completed",
        "uploaded_at": "2026-05-20 16:00:00",
        "processed_at": "2026-05-20 16:00:25",
        "chunk_count": 12,
        "qa_count": 8
      },
      {
        "id": 102,
        "title": "网络配置手册.md",
        "status": "processing",
        "uploaded_at": "2026-05-20 16:05:00",
        "processed_at": null,
        "chunk_count": 0,
        "qa_count": 0
      }
    ],
    "total": 15,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 15. 获取知识库文档详情

**接口**：`GET /api/knowledge/documents/{id}`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 文档ID |

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 101,
    "title": "IT设备故障排查指南.md",
    "status": "completed",
    "uploaded_at": "2026-05-20 16:00:00",
    "processed_at": "2026-05-20 16:00:25",
    "chunk_count": 12,
    "qa_count": 8,
    "file_size_bytes": 15360,
    "chunks": [
      {
        "id": 1,
        "content": "## 电脑无法开机故障排查\n\n1. 检查电源连接...",
        "keywords": ["电脑", "开机", "电源", "故障", "排查"],
        "qa_pairs": [
          {
            "question": "电脑无法开机怎么办？",
            "answer": "首先检查电源线是否插紧..."
          }
        ]
      }
    ]
  }
}
```

---

### 16. 健康检查

**接口**：`GET /health`

**响应（成功 200）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "healthy",
    "timestamp": "2026-05-20 16:10:00",
    "version": "1.0.0"
  }
}
```

---

## WebSocket 接口

### 连接工单实时消息

**接口**：`WS /ws/tickets/{ticket_id}`

**路径参数**：
| 参数 | 类型 | 描述 |
|------|------|------|
| ticket_id | int | 工单ID |

**连接参数**（Query String）：
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| token | string | 是 | access_token（不带"Bearer "前缀） |

**连接示例**：
```
ws://localhost:8000/ws/tickets/1003?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**服务端推送消息格式**：

**1. 新消息**：
```json
{
  "type": "new_message",
  "data": {
    "message_id": 15,
    "ticket_id": 1003,
    "role": "agent",
    "content": "您好，我是坐席小李，我来帮您处理这个问题。",
    "timestamp": "2026-05-20 15:13:00"
  }
}
```

**2. 工单状态变更**：
```json
{
  "type": "status_change",
  "data": {
    "ticket_id": 1003,
    "old_status": "pending",
    "new_status": "in_progress",
    "agent_id": 12,
    "timestamp": "2026-05-20 15:12:00"
  }
}
```

**3. 连接确认**：
```json
{
  "type": "connected",
  "data": {
    "ticket_id": 1003,
    "message": "WebSocket连接成功",
    "timestamp": "2026-05-20 15:11:00"
  }
}
```

**4. 错误消息**：
```json
{
  "type": "error",
  "data": {
    "code": 401,
    "message": "Token失效，请重新登录"
  }
}
```

**客户端发送消息格式**（心跳包）：
```json
{
  "type": "ping",
  "timestamp": "2026-05-20 15:15:00"
}
```

**服务端心跳响应**：
```json
{
  "type": "pong",
  "timestamp": "2026-05-20 15:15:00"
}
```

---

## 前端 Mock 数据规范

前端 Mock 数据必须严格遵循本文件定义的响应格式，存放在：
```
frontend/src/mocks/
├── auth.ts        # 登录相关 Mock
├── tickets.ts     # 工单相关 Mock
├── messages.ts    # 消息相关 Mock
└── knowledge.ts   # 知识库相关 Mock
```

**Mock 数据切换**：
- 开发环境：`VITE_USE_MOCK=true`（使用 Mock 数据）
- 联调环境：`VITE_USE_MOCK=false`（使用真实后端）

**Mock 数据要求**：
1. 响应格式必须与本文件完全一致
2. 错误码必须与本文件定义一致
3. 字段名、类型、嵌套结构必须严格对齐
4. Mock 数据应覆盖正常流程和至少一种异常流程

---

**文档版本**：V1.0  
**维护规则**：任何接口变更必须先更新本文件，再同步更新前端 Mock 和后端实现
