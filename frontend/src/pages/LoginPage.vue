<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1 class="system-title">智能客服系统</h1>
        <p class="subtitle">请输入您的账号密码登录系统</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">账号</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="请输入账号"
            autocomplete="username"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            required
          />
        </div>

        <div class="form-options">
          <label class="remember-me">
            <input v-model="formData.rememberMe" type="checkbox" />
            <span>记住我</span>
          </label>
          <a href="#" class="forgot-password" @click.prevent="handleForgotPassword">忘记密码？</a>
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button type="submit" class="login-button" :disabled="isLoading">
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="mock-hint">
        <p><strong>[Mock 测试账号]</strong></p>
        <p>员工账号: employee1 / 123456</p>
        <p>坐席账号: agent1 / 123456</p>
        <p>管理员: admin / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  password: '',
  rememberMe: false
})

const errorMessage = ref('')
const isLoading = ref(false)

onMounted(() => {
  const rememberedUsername = authStore.getRememberedUsername()
  if (rememberedUsername) {
    formData.value.username = rememberedUsername
    formData.value.rememberMe = true
  }
})

const handleLogin = async () => {
  errorMessage.value = ''
  isLoading.value = true

  try {
    const result = await authStore.login(
      formData.value.username,
      formData.value.password,
      formData.value.rememberMe
    )

    if (result.success) {
      router.push('/employee')
    } else {
      errorMessage.value = result.message
    }
  } catch {
    errorMessage.value = '登录失败，请重试'
  } finally {
    isLoading.value = false
  }
}

const handleForgotPassword = () => {
  // TODO: 实现忘记密码功能
  alert('忘记密码功能将在后续版本实现')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
  padding: 24px;
}

.login-box {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 8px;
  padding: 48px 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.system-title {
  font-size: 28px;
  font-weight: 600;
  color: #18181b;
  margin: 0 0 8px 0;
  letter-spacing: -0.04em;
}

.subtitle {
  font-size: 14px;
  color: #71717a;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #18181b;
}

.form-group input[type='text'],
.form-group input[type='password'] {
  height: 44px;
  padding: 0 16px;
  border: 1px solid #e4e4e7;
  border-radius: 8px;
  font-size: 15px;
  color: #18181b;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #52525b;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: -8px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #52525b;
  cursor: pointer;
  user-select: none;
}

.remember-me input[type='checkbox'] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.forgot-password {
  font-size: 14px;
  color: #52525b;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password:hover {
  color: #18181b;
}

.error-message {
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #ef4444;
  font-size: 14px;
  text-align: center;
}

.login-button {
  height: 44px;
  background: #18181b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
}

.login-button:hover:not(:disabled) {
  background: #27272a;
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.mock-hint {
  margin-top: 32px;
  padding: 16px;
  background: #fafaf9;
  border-radius: 8px;
  font-size: 13px;
  color: #52525b;
  line-height: 1.6;
}

.mock-hint p {
  margin: 4px 0;
}

.mock-hint strong {
  color: #18181b;
}

@media (max-width: 640px) {
  .login-box {
    padding: 32px 24px;
  }

  .system-title {
    font-size: 24px;
  }
}
</style>
