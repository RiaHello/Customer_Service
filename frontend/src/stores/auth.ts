import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/auth'
import * as authService from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  const init = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        localStorage.removeItem('user')
      }
    }
  }

  const login = async (username: string, password: string, rememberMe: boolean) => {
    try {
      const response = await authService.login({ username, password })

      if (response.code === 200 && response.data) {
        token.value = response.data.token
        user.value = response.data.user

        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))

        if (rememberMe) {
          localStorage.setItem('remember_username', username)
        } else {
          localStorage.removeItem('remember_username')
        }

        return { success: true, message: response.message }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error: any) {
      // 优先使用后端返回的错误消息
      const message = error.response?.data?.message || '登录失败，请重试'
      return { success: false, message }
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const getRememberedUsername = () => {
    return localStorage.getItem('remember_username') || ''
  }

  init()

  return {
    token,
    user,
    isLoggedIn,
    login,
    logout,
    getRememberedUsername
  }
})
