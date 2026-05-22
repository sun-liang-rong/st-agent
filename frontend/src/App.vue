<template>
  <div v-if="isAuthPage" class="h-screen">
    <router-view />
  </div>
  <div v-else class="h-screen flex bg-gray-100 dark:bg-slate-900">
    <aside class="w-72 bg-gradient-to-b from-amber-50 to-orange-50 dark:from-stone-900 dark:to-stone-800 border-r border-amber-200 dark:border-stone-700 flex flex-col">
      <!-- Logo / Title -->
      <div class="p-5 border-b border-amber-200 dark:border-stone-700">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-lg shadow-md">🤖</div>
          <div>
            <h1 class="font-bold text-amber-900 dark:text-amber-100">AI 助手</h1>
            <p class="text-xs text-amber-500 dark:text-amber-400">智能对话 · 创意无限</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="p-3 space-y-1.5">
        <button
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200"
          :class="isActive('/app') ? 'bg-gradient-to-r from-amber-500 to-red-500 text-white shadow-md' : 'text-amber-800 dark:text-amber-200 hover:bg-amber-100 dark:hover:bg-stone-700'"
          @click="goNewChat"
        >
          <span class="text-base">💬</span>
          新对话
        </button>
        <button
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200"
          :class="isActive('/image') ? 'bg-gradient-to-r from-amber-500 to-red-500 text-white shadow-md' : 'text-amber-800 dark:text-amber-200 hover:bg-amber-100 dark:hover:bg-stone-700'"
          @click="goImage"
        >
          <span class="text-base">🎨</span>
          AI 生成图片
        </button>
      </div>

      <!-- History Section -->
      <div class="px-4 pt-3 pb-2 flex items-center justify-between">
        <span class="text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">历史记录</span>
        <span class="text-xs text-amber-400 dark:text-stone-500">{{ sessions.length }}</span>
      </div>
      <div class="flex-1 overflow-y-auto px-3 pb-3 space-y-1">
        <div
          v-for="s in sessions"
          :key="s.contextId"
          class="w-full px-3 py-2.5 rounded-xl transition-all duration-200 group"
          :class="isSessionActive(s) ? 'bg-white dark:bg-stone-700 shadow-sm border border-amber-200 dark:border-stone-600' : 'hover:bg-amber-100/60 dark:hover:bg-stone-700/50'"
          @click="openSession(s)"
        >
          <div class="flex items-center gap-2.5">
            <span class="text-sm flex-shrink-0">{{ s.sessionType === 'image' ? '🎨' : '💬' }}</span>
            <div class="min-w-0 flex-1">
              <div class="text-sm font-medium truncate" :class="isSessionActive(s) ? 'text-amber-900 dark:text-amber-100' : 'text-amber-800 dark:text-amber-200'">{{ s.title || '未命名会话' }}</div>
              <div class="text-xs mt-0.5" :class="isSessionActive(s) ? 'text-amber-600 dark:text-amber-400' : 'text-amber-500/70 dark:text-stone-500'">{{ s.sessionType === 'image' ? '图片生成' : '对话' }}</div>
            </div>
            <button @click.stop="deleteSession(s)" class="opacity-0 group-hover:opacity-100 p-1 rounded-md text-amber-400 dark:text-stone-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all flex-shrink-0" title="删除">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="sessions.length === 0" class="flex flex-col items-center py-8 text-center">
          <div class="text-2xl mb-2 opacity-40">📭</div>
          <p class="text-xs text-amber-400 dark:text-stone-500">暂无历史记录</p>
        </div>
      </div>

      <!-- Bottom Actions -->
      <div class="p-3 border-t border-amber-200 dark:border-stone-700 space-y-1.5">
        <button
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 text-amber-800 dark:text-amber-200 hover:bg-amber-100 dark:hover:bg-stone-700"
          @click="toggleTheme"
        >
          <span class="text-base">{{ themeIcon }}</span>
          {{ themeLabel }}
        </button>
        <button
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 text-amber-800 dark:text-amber-200 hover:bg-red-100 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400"
          @click="handleLogout"
        >
          <span class="text-base">🚪</span>
          退出登录
        </button>
      </div>
    </aside>

    <main class="flex-1 min-w-0">
      <router-view />
    </main>

    <ConfirmDialog ref="confirmRef" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import type { SessionItem } from '@/services/api'
import { apiService } from '@/services/api'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const route = useRoute()
const sessionStore = useSessionStore()
const appStore = useAppStore()
const confirmRef = ref<InstanceType<typeof ConfirmDialog> | null>(null)
const authStore = useAuthStore()
const sessions = computed(() => sessionStore.sessions)
const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')
const isDark = computed(() => appStore.isDark)
const themeIcon = computed(() => {
  const t = appStore.theme
  if (t === 'light') return '☀️'
  if (t === 'dark') return '🌙'
  return '💻'
})
const themeLabel = computed(() => {
  const t = appStore.theme
  if (t === 'light') return '浅色模式'
  if (t === 'dark') return '深色模式'
  return '跟随系统'
})

function isActive(path: string) {
  if (path === '/app') return route.path === '/app' && !route.query.sessionId
  return route.path === path
}

function isSessionActive(s: SessionItem) {
  return route.query.sessionId === s.contextId
}

function goNewChat() {
  router.push('/app')
}

function goImage() {
  router.push('/image')
}

async function deleteSession(s: SessionItem) {
  const ok = await confirmRef.value?.confirm({
    title: '确认删除',
    message: `删除「${s.title || '未命名会话'}」后将无法恢复`,
    type: 'danger',
  })
  if (!ok) return
  try {
    await apiService.deleteChatHistory(s.contextId)
    await sessionStore.loadSessions()
    if (isSessionActive(s)) {
      router.push('/app')
    }
  } catch {
    alert('删除失败')
  }
}

function openSession(s: SessionItem) {
  if (s.sessionType === 'image') {
    router.push({ path: '/image', query: { sessionId: s.contextId } })
    return
  }
  router.push({ path: '/app', query: { sessionId: s.contextId } })
}

function toggleTheme() {
  appStore.toggleTheme()
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  appStore.loadSettings()
  await sessionStore.loadSessions()
})
</script>
