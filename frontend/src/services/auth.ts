import api from './api'
import { mockLogin } from '@/mocks/auth'
import type { ApiResponse, LoginRequest, LoginResponse } from '@/types/auth'

const useMock = import.meta.env.VITE_USE_MOCK === 'true'

export const login = async (data: LoginRequest): Promise<ApiResponse<LoginResponse>> => {
  if (useMock) {
    return mockLogin(data.username, data.password)
  }

  const response = await api.post<ApiResponse<LoginResponse>>('/auth/login', data)
  return response.data
}
