<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo">
        <div class="logo-icon">🤖</div>
        <span class="logo-text">智能客服系统</span>
      </div>
    </div>

    <nav class="header-nav">
      <router-link to="/employee" class="nav-item">员工端</router-link>
      <router-link to="/agent" class="nav-item">坐席端</router-link>
      <router-link to="/knowledge" class="nav-item">知识库管理</router-link>
    </nav>

    <div class="header-right">
      <div v-if="authStore.user" class="user-info">
        <span class="user-name">{{ authStore.user.display_name || authStore.user.username }}</span>
        <button class="logout-button" @click="handleLogout">退出</button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  height: 64px;
  background: white;
  border-bottom: 1px solid #e4e4e7;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
  line-height: 1;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #18181b;
  letter-spacing: -0.02em;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

.nav-item {
  padding: 8px 16px;
  color: #71717a;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-item:hover {
  color: #18181b;
  background: #fafafa;
}

.nav-item.router-link-active {
  color: #18181b;
  background: #f4f4f5;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  font-size: 14px;
  color: #18181b;
  font-weight: 500;
}

.logout-button {
  padding: 6px 16px;
  background: transparent;
  border: 1px solid #e4e4e7;
  color: #52525b;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-button:hover {
  background: #fafafa;
  border-color: #d4d4d8;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 16px;
  }

  .logo-text {
    display: none;
  }

  .header-nav {
    gap: 4px;
  }

  .nav-item {
    padding: 6px 12px;
    font-size: 14px;
  }

  .user-name {
    display: none;
  }
}
</style>
