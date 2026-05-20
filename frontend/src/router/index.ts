import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/pages/LoginPage.vue'
import EmployeePage from '@/pages/EmployeePage.vue'
import AgentPage from '@/pages/AgentPage.vue'
import KnowledgePage from '@/pages/KnowledgePage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { requiresAuth: false }
    },
    {
      path: '/employee',
      name: 'employee',
      component: EmployeePage,
      meta: { requiresAuth: true }
    },
    {
      path: '/agent',
      name: 'agent',
      component: AgentPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: KnowledgePage,
      meta: { requiresAuth: true }
    }
  ]
})

// 导航守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/employee')
  } else {
    next()
  }
})

export default router
