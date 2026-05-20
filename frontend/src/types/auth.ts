export interface User {
  id: number
  username: string
  display_name?: string
  role: string
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T | null
}
