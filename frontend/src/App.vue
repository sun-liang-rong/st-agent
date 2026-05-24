<template>
  <div v-if="isAuthPage" class="h-screen">
    <router-view />
  </div>
  <div v-else class="h-screen flex bg-gray-100 dark:bg-slate-900">
    <!-- Mobile overlay -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="mobileSidebarOpen" class="fixed inset-0 bg-black/50 z-40 md:hidden" @click="mobileSidebarOpen = false"></div>
    </transition>

    <!-- Sidebar -->
    <aside
      class="w-72 bg-gradient-to-b from-amber-50 to-orange-50 dark:from-stone-900 dark:to-stone-800 border-r border-amber-200 dark:border-stone-700 flex flex-col fixed md:relative z-50 transition-transform duration-300"
      :class="mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    >
      <!-- Logo / Title -->
      <div class="p-5 border-b border-amber-200 dark:border-stone-700">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-lg shadow-md">🤖</div>
          <div>
            <h1 class="font-bold text-amber-900 dark:text-amber-100">AI 助手</h1>
            <p class="text-xs text-amber-500 dark:text-amber-400">智能对话 · 创意无限</p>
          </div>
          <!-- Mobile close button -->
          <button class="md:hidden ml-auto text-amber-400 hover:text-amber-600" @click="mobileSidebarOpen = false">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
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
        <span class="text-xs text-amber-400 dark:text-stone-500">{{ displaySessions.length }}/{{ sessionStore.sessions.length }}</span>
      </div>
      <div class="px-3 pb-2 space-y-2">
        <div class="relative">
          <input
            v-model="sessionSearch"
            @input="onSearchInput"
            type="search"
            placeholder="搜索历史"
            class="w-full rounded-xl border border-amber-200 dark:border-stone-600 bg-white/80 dark:bg-stone-800 px-3 py-2 pl-8 text-sm text-amber-900 dark:text-amber-100 placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-400"
          />
          <svg class="absolute left-2.5 top-2.5 h-4 w-4 text-amber-400 dark:text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-4.35-4.35M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Z"/>
          </svg>
          <button v-if="sessionSearch" @click="clearSearch" class="absolute right-2.5 top-2.5 h-4 w-4 text-amber-400 hover:text-amber-600">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="grid grid-cols-3 gap-1 rounded-xl bg-amber-100/70 dark:bg-stone-800 p-1">
          <button
            v-for="option in sessionTypeOptions"
            :key="option.value"
            class="rounded-lg px-2 py-1.5 text-xs font-medium transition-colors"
            :class="sessionTypeFilter === option.value ? 'bg-white text-amber-900 shadow-sm dark:bg-stone-700 dark:text-amber-100' : 'text-amber-600 hover:text-amber-900 dark:text-amber-400 dark:hover:text-amber-100'"
            @click="sessionTypeFilter = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
      <div class="flex-1 overflow-y-auto px-3 pb-3 space-y-1">
        <!-- Search results or filtered sessions -->
        <div
          v-for="s in displaySessions"
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
            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click.stop="renameSession(s)" class="p-1 rounded-md text-amber-400 dark:text-stone-500 hover:text-amber-700 hover:bg-amber-50 dark:hover:bg-stone-600 transition-all flex-shrink-0" title="重命名">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m16.86 3.49 3.65 3.65M4 20h3.65L19.38 8.27a2.58 2.58 0 0 0-3.65-3.65L4 16.35V20Z"/>
                </svg>
              </button>
              <button @click.stop="deleteSession(s)" class="p-1 rounded-md text-amber-400 dark:text-stone-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all flex-shrink-0" title="删除">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="sessionStore.sessions.length === 0" class="flex flex-col items-center py-8 text-center">
          <div class="text-2xl mb-2 opacity-40">📭</div>
          <p class="text-xs text-amber-400 dark:text-stone-500">暂无历史记录</p>
        </div>
        <div v-else-if="displaySessions.length === 0" class="flex flex-col items-center py-8 text-center">
          <div class="text-2xl mb-2 opacity-40">🔎</div>
          <p class="text-xs text-amber-400 dark:text-stone-500">{{ sessionSearch ? '没有匹配的历史记录' : '没有匹配的历史记录' }}</p>
        </div>
      </div>

      <!-- Bottom Actions -->
      <div class="p-3 border-t border-amber-200 dark:border-stone-700 space-y-1.5">
        <button
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 text-amber-800 dark:text-amber-200 hover:bg-amber-100 dark:hover:bg-stone-700"
          @click="toggleTrash"
        >
          <span class="text-base">🗑️</span>
          回收站 {{ trashCount > 0 ? `(${trashCount})` : '' }}
        </button>
        <button
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 text-amber-800 dark:text-amber-200 hover:bg-amber-100 dark:hover:bg-stone-700"
          @click="goSettings"
        >
          <span class="text-base">⚙️</span>
          个人中心
        </button>
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

    <!-- Main Content -->
    <main class="flex-1 min-w-0 relative">
      <!-- Mobile header -->
      <div class="md:hidden fixed top-0 left-0 right-0 z-30 bg-white dark:bg-stone-800 border-b border-amber-200 dark:border-stone-700 px-4 py-3 flex items-center gap-3">
        <button @click="mobileSidebarOpen = true" class="text-amber-600 hover:text-amber-800">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
        <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-sm">🤖</div>
        <h1 class="font-bold text-amber-900 dark:text-amber-100">AI 助手</h1>
      </div>
      <div class="h-full md:h-full pt-14 md:pt-0">
        <router-view />
      </div>
    </main>

    <ConfirmDialog ref="confirmRef" />

    <!-- Trash Panel -->
    <Teleport to="body">
      <transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="trashPanelOpen" class="fixed inset-0 bg-black/40 z-[60] flex items-center justify-center" @click.self="trashPanelOpen = false">
          <div class="bg-white dark:bg-stone-800 rounded-2xl shadow-xl w-full max-w-md mx-4 max-h-[80vh] overflow-hidden">
            <div class="px-5 py-4 border-b border-amber-200 dark:border-stone-700 flex items-center justify-between">
              <h2 class="text-lg font-bold text-amber-900 dark:text-amber-100">🗑️ 回收站</h2>
              <button @click="trashPanelOpen = false" class="text-amber-400 hover:text-amber-600 dark:text-stone-500 dark:hover:text-stone-300">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
            <div class="p-4 space-y-2 overflow-y-auto max-h-[50vh]">
              <div v-if="sessionStore.trashList.length === 0" class="flex flex-col items-center py-8 text-center">
                <div class="text-2xl mb-2 opacity-40">🗑️</div>
                <p class="text-xs text-amber-400 dark:text-stone-500">回收站是空的</p>
              </div>
              <div v-for="s in sessionStore.trashList" :key="s.contextId" class="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-amber-50 dark:bg-stone-700/50 hover:bg-amber-100 dark:hover:bg-stone-700 transition-all">
                <span class="text-sm">{{ s.sessionType === 'image' ? '🎨' : '💬' }}</span>
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-medium truncate text-amber-800 dark:text-amber-200">{{ s.title || '未命名会话' }}</div>
                  <div class="text-xs text-amber-500 dark:text-stone-500">{{ s.deletedAt ? new Date(s.deletedAt).toLocaleDateString() : '' }}</div>
                </div>
                <div class="flex items-center gap-1">
                  <button @click="restoreFromTrash(s.contextId)" class="px-2 py-1 text-xs rounded-md text-amber-600 hover:text-amber-800 hover:bg-amber-100 dark:text-amber-400 dark:hover:bg-stone-600 transition-all" title="恢复">恢复</button>
                  <button @click="permanentDeleteSession(s)" class="px-2 py-1 text-xs rounded-md text-red-500 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 transition-all" title="永久删除">删除</button>
                </div>
              </div>
            </div>
            <div v-if="sessionStore.trashList.length > 0" class="px-5 py-3 border-t border-amber-200 dark:border-stone-700">
              <button @click="clearTrash" class="w-full py-2 text-sm rounded-xl text-red-600 hover:text-red-800 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 transition-all">清空回收站</button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import type { SessionInfo } from '@/services/api'
import { chatApi } from '@/services/api'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const route = useRoute()
const sessionStore = useSessionStore()
const appStore = useAppStore()
const confirmRef = ref<InstanceType<typeof ConfirmDialog> | null>(null)
const authStore = useAuthStore()

const mobileSidebarOpen = ref(false)
const trashPanelOpen = ref(false)
const sessionSearch = ref('')
const sessionTypeFilter = ref<'all' | 'chat' | 'image'>('all')
const sessionTypeOptions = [
  { value: 'all' as const, label: '全部' },
  { value: 'chat' as const, label: '攻略' },
  { value: 'image' as const, label: '图片' },
]

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function onSearchInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!sessionSearch.value.trim()) {
    sessionStore.clearSearch()
    return
  }
  searchTimeout = setTimeout(() => {
    sessionStore.searchSessions(sessionSearch.value.trim())
  }, 300)
}

function clearSearch() {
  sessionSearch.value = ''
  sessionStore.clearSearch()
}

const displaySessions = computed(() => {
  const list = sessionStore.searchResults ?? sessionStore.sessions
  const keyword = sessionSearch.value.trim().toLowerCase()
  return list.filter((s) => {
    const matchType = sessionTypeFilter.value === 'all' || s.sessionType === sessionTypeFilter.value
    if (!sessionStore.searchResults) {
      const haystack = `${s.title || ''} ${s.summary || ''}`.toLowerCase()
      const matchKeyword = !keyword || haystack.includes(keyword)
      return matchType && matchKeyword
    }
    return matchType
  })
})

const trashCount = computed(() => sessionStore.trashList.length)

const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')
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

function isSessionActive(s: SessionInfo) {
  return route.query.sessionId === s.contextId
}

function goNewChat() {
  mobileSidebarOpen.value = false
  router.push('/app')
}

function goImage() {
  mobileSidebarOpen.value = false
  router.push('/image')
}

function goSettings() {
  mobileSidebarOpen.value = false
  router.push('/settings')
}

async function deleteSession(s: SessionInfo) {
  if (!confirmRef.value) return
  const ok = await confirmRef.value.confirm({
    title: '确认删除',
    message: `删除「${s.title || '未命名会话'}」后将移至回收站`,
    type: 'danger',
  })
  if (!ok) return
  try {
    await chatApi.deleteSession(s.contextId)
    await sessionStore.loadSessions()
    if (isSessionActive(s)) {
      router.push('/app')
    }
  } catch (e) {
    console.error('删除会话失败:', e)
  }
}

async function renameSession(s: SessionInfo) {
  const title = window.prompt('请输入新的会话名称', s.title || '')
  if (title === null) return
  const normalizedTitle = title.trim()
  if (!normalizedTitle || normalizedTitle === s.title) return
  try {
    await chatApi.renameSession(s.contextId, normalizedTitle)
    await sessionStore.loadSessions()
  } catch (e) {
    console.error('重命名会话失败:', e)
  }
}

function openSession(s: SessionInfo) {
  mobileSidebarOpen.value = false
  if (s.sessionType === 'image') {
    router.push({ path: '/image', query: { sessionId: s.contextId } })
    return
  }
  router.push({ path: '/app', query: { sessionId: s.contextId } })
}

function toggleTheme() {
  appStore.toggleTheme()
}

function toggleTrash() {
  trashPanelOpen.value = !trashPanelOpen.value
  if (trashPanelOpen.value) {
    sessionStore.loadTrash()
  }
}

async function restoreFromTrash(contextId: string) {
  try {
    await sessionStore.restoreFromTrash(contextId)
  } catch (e) {
    console.error('恢复会话失败:', e)
  }
}

async function permanentDeleteSession(s: SessionInfo) {
  if (!confirmRef.value) return
  const ok = await confirmRef.value.confirm({
    title: '永久删除',
    message: `永久删除「${s.title || '未命名会话'}」后将无法恢复`,
    type: 'danger',
  })
  if (!ok) return
  try {
    await sessionStore.permanentDelete(s.contextId)
  } catch (e) {
    console.error('永久删除失败:', e)
  }
}

async function clearTrash() {
  if (!confirmRef.value) return
  const ok = await confirmRef.value.confirm({
    title: '清空回收站',
    message: '清空回收站后所有已删除会话将永久删除，无法恢复',
    type: 'danger',
  })
  if (!ok) return
  try {
    await sessionStore.clearAllTrash()
  } catch (e) {
    console.error('清空回收站失败:', e)
  }
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