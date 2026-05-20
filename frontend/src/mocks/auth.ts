import type { ApiResponse, LoginResponse } from '@/types/auth'

// Mock 测试账号
export const mockAccounts = [
  {
    username: 'employee1',
    password: '123456',
    user: {
      id: 1,
      username: 'employee1',
      display_name: '张三',
      role: 'employee',
      created_at: '2026-05-20 10:00:00'
    }
  },
  {
    username: 'agent1',
    password: '123456',
    user: {
      id: 2,
      username: 'agent1',
      display_name: '李四',
      role: 'agent',
      created_at: '2026-05-20 10:00:00'
    }
  },
  {
    username: 'admin',
    password: '123456',
    user: {
      id: 3,
      username: 'admin',
      display_name: '王五',
      role: 'admin',
      created_at: '2026-05-20 10:00:00'
    }
  }
]

export const loginSuccessResponse = (username: string): ApiResponse<LoginResponse> => {
  const account = mockAccounts.find((acc) => acc.username === username)
  if (!account) {
    return loginFailResponse() as ApiResponse<LoginResponse>
  }

  return {
    code: 200,
    message: 'success',
    data: {
      access_token: `mock-token-${username}-${Date.now()}`,
      token_type: 'Bearer',
      user: account.user
    }
  }
}

export const loginFailResponse = (): ApiResponse<LoginResponse> => {
  return {
    code: 1001,
    message: '用户名或密码错误',
    data: null
  }
}

// Mock 登录函数
export const mockLogin = (username: string, password: string): Promise<ApiResponse<LoginResponse>> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const account = mockAccounts.find((acc) => acc.username === username && acc.password === password)
      if (account) {
        resolve(loginSuccessResponse(username))
      } else {
        resolve(loginFailResponse())
      }
    }, 500)
  })
}
