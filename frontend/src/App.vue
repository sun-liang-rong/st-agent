<template>
  <!-- 主题切换过渡遮罩 -->
  <div v-if="themeTransitioning" ref="themeOverlay"
    class="theme-overlay fixed inset-0 z-[99999] pointer-events-none"
    :style="{ background: themeOverlayColor }">
  </div>

  <div id="app" :class="appClasses">
    <!-- ── 仪表盘布局：侧边栏 + 顶栏 + 页面内容 ── -->
    <template v-if="!isLandingPage">
      <div class="flex h-screen bg-gray-50 dark:bg-slate-900">
        <!-- 移动端侧边栏遮罩 -->
        <div
          v-if="sideBarOpen && isAuthenticated"
          class="fixed inset-0 bg-black/30 dark:bg-black/50 z-20 md:hidden backdrop-blur-sm transition-all duration-300"
          @click="toggleSideBar"
        ></div>

        <!-- 侧边栏 -->
        <aside 
          v-if="sideBarOpen && isAuthenticated"
          class="w-64 bg-white dark:bg-slate-800 border-r border-gray-200 dark:border-slate-700 flex flex-col shrink-0 md:relative fixed left-0 top-0 h-full z-30 transition-all duration-300 shadow-xl md:shadow-none"
      >
        <!-- Logo 区 -->
        <div class="p-5 border-b border-gray-100 dark:border-slate-700/50">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-xl shadow-sm shadow-emerald-200 dark:shadow-emerald-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              </svg>
            </div>
            <div>
              <h1 class="text-base font-bold text-gray-900 dark:text-white leading-tight">{{ t('app.title', appStore.locale) }}</h1>
              <p class="text-[11px] text-gray-400 dark:text-gray-500">{{ t('app.subtitle', appStore.locale) }}</p>
            </div>
          </div>
        </div>
        
        <!-- 导航菜单 -->
        <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <router-link 
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200"
            :class="route.path === item.path
              ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
              : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-700/50 hover:text-gray-700 dark:hover:text-gray-200'"
          >
            <!-- 激活指示器 -->
            <span class="w-1 h-1 rounded-full transition-all duration-200" :class="route.path === item.path ? 'bg-primary-500 w-1.5 h-1.5' : ''"></span>
            <component :is="item.icon" class="w-5 h-5 shrink-0" />
            <span>{{ item.name }}</span>
          </router-link>
        </nav>
        
        <!-- 底部：用户 + 主题 -->
        <div class="border-t border-gray-100 dark:border-slate-700/50">
          <!-- 用户信息 -->
          <div v-if="isAuthenticated" class="px-4 py-3">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center shadow-sm shrink-0">
                <span class="text-white text-sm font-semibold">{{ userInitial }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-gray-800 dark:text-white truncate">{{ currentUser?.username || 'User' }}</p>
                <p class="text-xs text-gray-400 dark:text-gray-500 truncate">{{ currentUser?.email || '' }}</p>
              </div>
              <button @click="handleLogout" class="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all" title="退出登录">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 主题切换 -->
          <div class="px-4 pb-3">
            <button @click="toggleTheme"
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
                text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-700/50 hover:text-gray-700 dark:hover:text-gray-200">
              <span class="text-base leading-none">{{ isDark ? '🌙' : '☀️' }}</span>
              <span>{{ t('sidebar.theme', appStore.locale) }}</span>
              <span class="ml-auto text-[11px] text-gray-400 dark:text-gray-500">{{ isDark ? t('sidebar.dark', appStore.locale) : t('sidebar.light', appStore.locale) }}</span>
            </button>
          </div>
        </div>
      </aside>
      
      <!-- 主内容区 -->
      <main class="flex-1 flex flex-col overflow-hidden">
        <!-- 移动端顶部栏 -->
        <div class="md:hidden flex items-center justify-between p-4 border-b border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800">
          <div class="flex items-center gap-4">
            <button v-if="isAuthenticated" @click="toggleSideBar" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
              </svg>
            </button>
            <h1 class="text-lg font-bold text-emerald-600">{{ t('app.title', appStore.locale) }}</h1>
          </div>
          <button
            v-if="!isAuthenticated && route.path !== '/login' && route.path !== '/register'"
            @click="router.push('/login')"
            class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg text-sm font-medium transition-colors"
          >
            {{ t('login.submit', appStore.locale) }}
          </button>
        </div>
        
        <!-- 页面内容 -->
        <div class="flex-1 overflow-auto">
          <router-view v-slot="{ Component }">
            <transition name="page-fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
  </template>
  
  <!-- ── 官网首页：独立布局，不继承仪表盘的 flex h-screen ── -->
  <template v-else>
    <router-view />
  </template>
  </div>
  <!-- 全局 Toast 通知 -->
  <Toast />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { t } from '@/i18n'
import Toast from '@/components/Toast.vue'
import { h } from 'vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const authStore = useAuthStore()

const isDark = computed(() => appStore.isDark)
const sideBarOpen = computed(() => appStore.sideBarOpen)
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isLandingPage = computed(() => route.name === 'landing')

const fontSizeClass = computed(() => {
  const map = { small: 'text-sm', medium: 'text-base', large: 'text-lg' }
  return map[appStore.settings.fontSize] || 'text-base'
})

const codeFontClass = computed(() => {
  return appStore.settings.codeFont === 'system' ? 'code-font-system' : ''
})

const densityClass = computed(() => {
  return appStore.settings.messageDensity === 'compact' ? 'density-compact' : ''
})

const appClasses = computed(() => ({
  dark: isDark.value,
  [fontSizeClass.value]: true,
  [codeFontClass.value]: codeFontClass.value !== '',
  [densityClass.value]: densityClass.value !== '',
}))
const currentUser = computed(() => authStore.currentUser)
const userInitial = computed(() => {
  if (currentUser.value?.username) return currentUser.value.username.charAt(0).toUpperCase()
  return 'U'
})

// ── 主题切换动画（左下角扩散） ──
const themeTransitioning = ref(false)
const themeOverlayColor = ref('')
const themeOverlay = ref<HTMLElement | null>(null)
const TRANSITION_DURATION = 600 // ms

function toggleTheme() {
  const targetIsDark = !appStore.isDark
  themeOverlayColor.value = targetIsDark ? '#0f172a' : '#f8fafc'
  themeTransitioning.value = true

  // 下一帧触发 clip-path 动画
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      if (themeOverlay.value) {
        themeOverlay.value.classList.add('active')
      }
    })
  })

  // 动画过半时切换主题
  setTimeout(() => {
    appStore.toggleTheme()
  }, TRANSITION_DURATION * 0.45)

  // 动画结束后移除遮罩
  setTimeout(() => {
    if (themeOverlay.value) {
      themeOverlay.value.classList.remove('active')
    }
    themeTransitioning.value = false
  }, TRANSITION_DURATION)
}

function toggleSideBar() {
  appStore.toggleSideBar()
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

// 导航项（响应式翻译）
const navItems = computed(() => [
  {
    path: '/app',
    name: t('nav.home', appStore.locale),
    icon: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-5 h-5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '1.5', d: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z' }),
      h('circle', { cx: '12', cy: '10', r: '3', fill: 'currentColor' })
    ])
  },
  {
    path: '/history',
    name: t('nav.history', appStore.locale),
    icon: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-5 h-5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0z' })
    ])
  },
  {
    path: '/settings',
    name: t('nav.settings', appStore.locale),
    icon: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-5 h-5' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 0 0-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 0 0-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 0 0-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 0 0-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 0 0 1.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' }),
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z' })
    ])
  }
])

onMounted(async () => {
  appStore.loadSettings()
  await authStore.checkAuth()
})
</script>

<style>
/* ── 页面切换淡入淡出 ── */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

/* ── 主题切换：从左下角扩散 ── */
.theme-overlay {
  clip-path: circle(0% at 0 100%);
  transition: clip-path 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.theme-overlay.active {
  clip-path: circle(150% at 0 100%);
}
</style>
