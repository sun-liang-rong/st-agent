<template>
  <div class="flex flex-col h-full bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-stone-900 dark:via-stone-800 dark:to-stone-900">
    <!-- Messages Area -->
    <div class="flex-1 overflow-y-auto p-6 space-y-5">
      <!-- Empty State -->
      <div v-if="messages.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
        <div class="text-5xl mb-4">🗺️</div>
        <div class="text-xl font-semibold text-amber-800 dark:text-amber-200 mb-2">你好呀！想探索哪里？</div>
        <div class="text-sm text-amber-600 dark:text-amber-400 mb-6">告诉我你的目的地，我来帮你规划完美旅程</div>
        <div class="flex gap-3 flex-wrap justify-center">
          <button @click="quickSend('帮我规划一个杭州三日游')"
            class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-4 py-2 text-sm text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">
            🏞️ 杭州三日游
          </button>
          <button @click="quickSend('帮我规划成都美食之旅')"
            class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-4 py-2 text-sm text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">
            🌸 成都美食之旅
          </button>
          <button @click="quickSend('帮我规划云南自驾游')"
            class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-4 py-2 text-sm text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">
            🏔️ 云南自驾游
          </button>
        </div>
      </div>

      <!-- Message List -->
      <div v-for="m in messages" :key="m.id" class="message-enter">
        <!-- AI Message -->
        <div v-if="m.role === 'assistant'" class="flex gap-3 items-start group">
          <div class="w-9 h-9 rounded-full bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-lg shadow-md flex-shrink-0">🤖</div>
          <div>
            <div class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-tl-sm rounded-tr-xl rounded-bl-xl rounded-br-xl px-4 py-3 shadow-sm max-w-[75%]">
              <div v-if="m.isStreaming" class="text-sm text-amber-900 dark:text-amber-100 whitespace-pre-wrap">
                {{ m.content }}<span class="cursor-blink">▊</span>
              </div>
              <!-- Image message -->
              <div v-else-if="extractImageUrl(m.content)" class="rounded-xl overflow-hidden max-w-[280px] cursor-pointer hover:opacity-90 transition-opacity" @click="previewImage(extractImageUrl(m.content)!)">
                <img :src="extractImageUrl(m.content)" class="w-full object-cover rounded-xl" alt="AI生成的图片" />
                <div class="text-center text-xs text-amber-500 dark:text-amber-400 mt-1">点击查看大图</div>
              </div>
              <!-- Text message -->
              <div v-else class="text-sm text-amber-900 dark:text-amber-100">
                <MarkdownRenderer :content="m.content" />
              </div>
            </div>
            <div class="flex items-center gap-3 mt-1.5 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <span class="text-xs text-amber-600 dark:text-amber-400">{{ formatTime(m.created_at) }}</span>
              <button @click="copyMessage(m.content)" class="text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 transition-colors">📋 复制</button>
            </div>
          </div>
        </div>

        <!-- User Message -->
        <div v-else class="flex gap-3 items-start justify-end group">
          <div class="text-right">
            <div class="bg-gradient-to-r from-amber-500 to-red-500 text-white rounded-tr-sm rounded-tl-xl rounded-bl-xl rounded-br-xl px-4 py-3 shadow-md max-w-[75%] inline-block">
              <p class="whitespace-pre-wrap text-sm">{{ m.content }}</p>
            </div>
            <div class="flex items-center gap-3 mt-1.5 mr-2 justify-end opacity-0 group-hover:opacity-100 transition-opacity">
              <span class="text-xs text-amber-600 dark:text-amber-400">{{ formatTime(m.created_at) }}</span>
              <button @click="copyMessage(m.content)" class="text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 transition-colors">📋 复制</button>
            </div>
          </div>
          <div class="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-lg shadow-md flex-shrink-0">😊</div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="p-4 border-t border-amber-200 dark:border-stone-700">
      <div class="max-w-3xl mx-auto relative">
        <textarea
          v-model="input"
          @keydown.enter.exact.prevent="send"
          :disabled="loading"
          placeholder="输入内容，和大模型交流"
          rows="2"
          class="w-full border-2 border-amber-300 dark:border-stone-600 bg-white dark:bg-stone-800 rounded-2xl px-4 py-3 pr-12 text-sm text-amber-900 dark:text-amber-100 placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent resize-none disabled:opacity-50"
        ></textarea>
        <button
          v-show="input.trim()"
          @click="send"
          :disabled="loading"
          class="absolute right-3 bottom-3 w-8 h-8 rounded-lg bg-gradient-to-r from-amber-500 to-red-500 hover:from-amber-600 hover:to-red-600 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center justify-center"
        >
          <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"/></svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Image Preview Lightbox -->
  <Teleport to="body">
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="previewVisible" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center" style="z-index: 99999" @click="previewVisible = false">
        <img :src="previewUrl" class="max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl" @click.stop />
        <button @click="previewVisible = false" class="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors flex items-center justify-center">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
        <div class="absolute bottom-6 flex gap-3">
          <button @click.stop="downloadImage(previewUrl)" class="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors flex items-center justify-center" title="下载">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          </button>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { Teleport } from 'vue'
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { apiService } from '@/services/api'
import { useSessionStore } from '@/stores/session'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  isStreaming?: boolean
}

const route = useRoute()
const sessionStore = useSessionStore()
const loading = ref(false)

// Image preview
const previewVisible = ref(false)
const previewUrl = ref('')

function extractImageUrl(content: string): string | null {
  const match = content.match(/^\[图片\]\s*(.+)$/s)
  if (!match) return null
  const path = match[1].trim()
  if (path.startsWith('http')) return path
  return '/' + path.replace(/\\/g, '/')
}

function previewImage(url: string) {
  previewUrl.value = url
  previewVisible.value = true
}

function downloadImage(url: string) {
  const filename = url.split('/').pop()?.split('?')[0] || 'image.png'
  fetch(url, { mode: 'cors' })
    .then(res => res.blob())
    .then(blob => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = filename
      a.click()
      URL.revokeObjectURL(a.href)
    })
    .catch(() => {
      window.open(url, '_blank')
    })
}
const input = ref('')
const messages = ref<Message[]>([])
const sessionId = ref<string>('')

function formatTime(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function copyMessage(text: string) {
  navigator.clipboard.writeText(text)
}

function quickSend(text: string) {
  input.value = text
  send()
}

async function loadSession(id: string) {
  const res: any = await apiService.getSessionMessages(id)
  const rows = Array.isArray(res) ? res : (res.data || [])
  messages.value = rows.flatMap((row: any, idx: number) => [
    { id: `${row.id}-u-${idx}`, role: 'user' as const, content: row.userMessage, created_at: row.createdAt || '' },
    { id: `${row.id}-a-${idx}`, role: 'assistant' as const, content: row.aiReply, created_at: row.createdAt || '' },
  ])
  sessionId.value = id
}

function newSession() {
  messages.value = []
  sessionId.value = ''
}

async function send() {
  const content = input.value.trim()
  if (!content || loading.value) return

  messages.value.push({ id: `${Date.now()}-u`, role: 'user', content, created_at: new Date().toISOString() })
  input.value = ''
  loading.value = true

  const aiMsgId = `${Date.now()}-a`
  messages.value.push({ id: aiMsgId, role: 'assistant', content: '', created_at: new Date().toISOString(), isStreaming: true })
  const aiMsg = messages.value[messages.value.length - 1]

  apiService.chatStream(
    content,
    sessionId.value || undefined,
    (token) => {
      aiMsg.content += token
    },
    (contextId) => {
      sessionId.value = contextId
      aiMsg.isStreaming = false
      loading.value = false
      sessionStore.loadSessions()
    },
    async (error) => {
      // Fallback to non-streaming on error
      try {
        const res = await apiService.chat(content, sessionId.value || undefined)
        sessionId.value = res.contextId
        aiMsg.content = res.reply
        aiMsg.isStreaming = false
        loading.value = false
        await sessionStore.loadSessions()
      } catch {
        aiMsg.content = `出错了：${error}`
        aiMsg.isStreaming = false
        loading.value = false
      }
    },
  )
}

watch(
  () => route.query.sessionId,
  async (val) => {
    const id = typeof val === 'string' ? val : ''
    if (!id) {
      newSession()
      return
    }
    await loadSession(id)
  },
  { immediate: true }
)

onMounted(async () => {
  if (!route.query.sessionId) {
    newSession()
  }
})
</script>
