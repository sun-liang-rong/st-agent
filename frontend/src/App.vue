<template>
  <div v-if="isAuthPage" class="h-screen">
    <router-view />
  </div>
  <div v-else class="h-screen flex bg-gray-100">
    <aside class="w-72 bg-white border-r flex flex-col">
      <div class="p-4 border-b">
        <h1 class="font-bold text-lg">AI 助手</h1>
      </div>

      <div class="p-3 space-y-2">
        <button class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100" @click="goNewChat">新对话</button>
        <button class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100" @click="goImage">AI生成图片</button>
      </div>

      <div class="px-3 pt-2 pb-1 text-xs text-gray-500">历史记录</div>
      <div class="flex-1 overflow-y-auto px-3 pb-3 space-y-1">
        <button
          v-for="s in sessions"
          :key="s.sessionId"
          class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100"
          @click="openSession(s)"
        >
          <div class="text-sm font-medium truncate">{{ s.title || '未命名会话' }}</div>
          <div class="text-xs text-gray-500 truncate">{{ s.sessionType === 'image' ? '图片' : '对话' }}</div>
        </button>
      </div>
    </aside>

    <main class="flex-1 min-w-0">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import type { SessionItem } from '@/services/api'

const router = useRouter()
const route = useRoute()
const sessionStore = useSessionStore()
const sessions = computed(() => sessionStore.sessions)
const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')

function goNewChat() {
  router.push('/app')
}

function goImage() {
  router.push('/image')
}

function openSession(s: SessionItem) {
  if (s.sessionType === 'image') {
    router.push({ path: '/image', query: { sessionId: s.sessionId } })
    return
  }
  router.push({ path: '/app', query: { sessionId: s.sessionId } })
}

onMounted(async () => {
  await sessionStore.loadSessions()
})
</script>
