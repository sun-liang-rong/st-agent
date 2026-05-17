import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/Home.vue'),
    meta: {
      title: 'AI 智能报表生成',
      requiresAuth: true
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/Login.vue'),
    meta: {
      title: '登录',
      guest: true
    }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/pages/Register.vue'),
    meta: {
      title: '注册',
      guest: true
    }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/pages/Settings.vue'),
    meta: {
      title: '设置',
      requiresAuth: true
    }
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/pages/History.vue'),
    meta: {
      title: '历史记录',
      requiresAuth: true
    }
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@/pages/Help.vue'),
    meta: {
      title: '帮助'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  document.title = to.meta.title ? `${to.meta.title} - AI 智能报表生成` : 'AI 智能报表生成'
  
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      await authStore.checkAuth()
    }
    
    if (!authStore.isAuthenticated) {
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }
  
  next()
})

export default router
