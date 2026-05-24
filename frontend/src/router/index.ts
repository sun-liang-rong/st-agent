import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/Login.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/pages/Register.vue'),
    },
    {
      path: '/app',
      name: 'chat',
      component: () => import('@/pages/Home.vue'),
    },
    {
      path: '/image',
      name: 'image',
      component: () => import('@/pages/ImageGen.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/pages/Settings.vue'),
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: () => import('@/pages/Favorites.vue'),
    },
    {
      path: '/share/:token',
      name: 'share',
      component: () => import('@/pages/ShareView.vue'),
      meta: { noAuth: true },
    },
    {
      path: '/',
      redirect: '/app',
    },
  ],
})

// Auth guard
router.beforeEach((to, _from, next) => {
  if (to.meta.noAuth) {
    next()
    return
  }
  const token = localStorage.getItem('token')
  if (!token && to.path !== '/login' && to.path !== '/register') {
    next('/login')
  } else {
    next()
  }
})

export default router