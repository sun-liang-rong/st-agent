<template>
  <AppPage>
    <div class="max-w-4xl mx-auto p-4 md:p-6 space-y-4">
      <!-- Messages -->
      <div ref="scrollContainer" class="space-y-4 pb-32">
        <AppEmpty v-if="messages.length === 0 && !loading" emoji="🗺️" title="开始你的旅行对话" description="输入目的地或旅行问题，AI 为你规划行程" />

        <div v-for="m in messages" :key="m.id" class="flex gap-3" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
          <!-- User message -->
          <div v-if="m.role === 'user'" class="max-w-[80%] bg-gradient-to-r from-amber-500 to-red-500 text-white px-4 py-2.5 rounded-2xl rounded-br-md shadow-sm text-sm whitespace-pre-wrap">{{ m.content }}</div>

          <!-- AI message -->
          <div v-else class="max-w-[85%] group">
            <div class="bg-white dark:bg-stone-800 border border-amber-200 dark:border-stone-700 px-4 py-3 rounded-2xl rounded-bl-md shadow-sm">
              <!-- Image display -->
              <div v-if="m.imageUrl" class="mb-3">
                <img :src="m.imageUrl" class="max-w-full rounded-lg cursor-pointer hover:opacity-90 transition-opacity" alt="生成的图片" @click="previewUrl = m.imageUrl; previewVisible = true" />
              </div>
              <!-- Image progress -->
              <div v-if="m.imageProgress" class="mb-3 flex items-center gap-2 text-sm text-amber-600 dark:text-amber-400">
                <AppSpinner size="sm" />
                <span>{{ m.imageProgress }}</span>
              </div>
              <!-- Text content -->
              <div v-if="m.content" class="text-sm text-amber-900 dark:text-amber-100 prose prose-amber dark:prose-invert max-w-none">
                <MarkdownRenderer :content="m.content" />
              </div>
              <!-- Streaming indicator -->
              <div v-if="m.isStreaming" class="inline-block w-2 h-4 bg-amber-500 animate-pulse ml-1"></div>
              <!-- Loading -->
              <div v-if="!m.content && !m.imageUrl && !m.imageProgress && !m.isStreaming" class="flex items-center gap-2 text-amber-400">
                <AppSpinner size="sm" />
              </div>
            </div>

            <!-- Action buttons -->
            <div class="flex items-center gap-3 mt-1.5 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <span class="text-xs text-amber-600 dark:text-amber-400">{{ formatTime(m.created_at) }}</span>
              <button @click="copyMessage(m.content)" class="text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 transition-colors">📋 复制</button>
              <button v-if="!m.isStreaming && m.messageId" @click="regenerateMessage(m)" class="text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 transition-colors">🔄 重新生成</button>
              <button v-if="!m.isStreaming && isTravelContent(m.content)" @click="exportTravel(m)" class="text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 transition-colors">📥 导出</button>
              <button v-if="!m.isStreaming && m.imageUrl" @click="favoriteImage(m)" class="text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 transition-colors">⭐ 收藏</button>
              <button v-if="!m.isStreaming && sessionId" @click="openShare('travel', sessionId)" class="text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 transition-colors">🔗 分享</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Input area -->
      <div class="fixed bottom-0 left-0 md:left-64 right-0 bg-gradient-to-t from-amber-50 via-amber-50 to-transparent dark:from-stone-900 dark:via-stone-900 pt-6 pb-4 px-4">
        <div class="max-w-4xl mx-auto">
          <!-- Image generation options -->
          <div v-if="showImageGen" class="mb-2 flex items-center gap-2 flex-wrap">
            <select v-model="imageStyle" class="rounded-lg border border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-2 py-1 text-xs text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-1 focus:ring-amber-400">
              <option value="旅行海报">旅行海报</option>
              <option value="水墨画">水墨画</option>
              <option value="油画">油画</option>
              <option value="水彩画">水彩画</option>
              <option value="像素画">像素画</option>
              <option value="赛博朋克">赛博朋克</option>
              <option value="日系插画">日系插画</option>
              <option value="写实摄影">写实摄影</option>
            </select>
            <select v-model="imageRatio" class="rounded-lg border border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-2 py-1 text-xs text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-1 focus:ring-amber-400">
              <option value="1:1">1:1</option>
              <option value="3:4">3:4</option>
              <option value="4:3">4:3</option>
              <option value="16:9">16:9</option>
              <option value="9:16">9:16</option>
            </select>
          </div>
          <div class="flex items-end gap-2">
            <button @click="showImageGen = !showImageGen" class="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-colors" :class="showImageGen ? 'bg-amber-500 text-white' : 'bg-amber-100 dark:bg-stone-700 text-amber-600 dark:text-amber-300'" title="图片生成模式">🎨</button>
            <div class="flex-1 relative">
              <textarea v-model="input" @keydown.enter.exact="send" rows="1" class="w-full rounded-xl border-2 border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-4 py-2.5 text-sm text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-400 resize-none" placeholder="输入旅行问题..." @input="autoResize"></textarea>
            </div>
            <AppBtn text="发送" :disabled="!input.trim() || loading" :full="false" @click="send" />
          </div>
        </div>
      </div>
    </div>

    <!-- Image Preview -->
    <AppLightbox v-model:visible="previewVisible" :src="previewUrl" downloadable />

    <!-- Share Dialog -->
    <ShareDialog v-model:visible="shareVisible" :type="shareType" :contentId="shareContentId" @close="shareVisible = false" />
  </AppPage>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import { chatApi, travelApi, imageApi, downloadBlob } from '@/services/api'
import { useSessionStore } from '@/stores/session'
import { downloadImage } from '@/composables/useImageDownload'
import { useSSE } from '@/composables/useSSE'
import AppPage from '@/components/AppPage.vue'
import AppEmpty from '@/components/AppEmpty.vue'
import AppSpinner from '@/components/AppSpinner.vue'
import AppBtn from '@/components/AppBtn.vue'
import AppLightbox from '@/components/AppLightbox.vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import ShareDialog from '@/components/ShareDialog.vue'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at?: string
  isStreaming?: boolean
  messageId?: number
  imageUrl?: string
  imageProgress?: string
}

const sessionStore = useSessionStore()
const { readSSE } = useSSE()

const messages = ref<Message[]>([])
const input = ref('')
const loading = ref(false)
const sessionId = ref(sessionStore.currentSessionId)
const previewVisible = ref(false)
const previewUrl = ref('')
const showImageGen = ref(false)
const imageStyle = ref('旅行海报')
const imageRatio = ref('1:1')
const scrollContainer = ref<HTMLElement>()

// Share & Favorite
const shareVisible = ref(false)
const shareType = ref<'travel' | 'image'>('travel')
const shareContentId = ref('')

watch(() => sessionStore.currentSessionId, (val) => {
  sessionId.value = val
  if (val) loadSession(val)
})

function formatTime(dateStr?: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function isTravelContent(text: string) {
  if (!text) return false
  const keywords = ['行程', '路线', '攻略', '景点', '推荐', '旅游', '旅行']
  return keywords.some(k => text.includes(k))
}

function autoResize(e: Event) {
  const el = e.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 150) + 'px'
}

function scrollToBottom() {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  })
}

function copyMessage(text: string) {
  navigator.clipboard.writeText(text)
}

async function loadSession(id: string) {
  try {
    const res: any = await chatApi.getSessionDetail(id)
    const rows = Array.isArray(res) ? res : (res?.data || [])
    messages.value = rows.map((row: any) => [
      { id: `${row.id}-u`, role: 'user' as const, content: row.userMessage || '' },
      { id: `${row.id}-a`, role: 'assistant' as const, content: row.aiReply || '', messageId: row.id },
    ]).flat()
    scrollToBottom()
  } catch (e) {
    console.error('加载会话失败:', e)
  }
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  loading.value = true
  messages.value.push({ id: `${Date.now()}-u`, role: 'user', content: text })
  const aiId = `${Date.now()}-a`
  messages.value.push({ id: aiId, role: 'assistant', content: '', isStreaming: true })
  input.value = ''
  scrollToBottom()

  try {
    const res = await chatApi.streamChat(text, {
      contextId: sessionId.value || undefined,
      generateImage: showImageGen.value || undefined,
      imageStyle: showImageGen.value ? imageStyle.value : undefined,
      imageRatio: showImageGen.value ? imageRatio.value : undefined,
    })

    let fullContent = ''
    await readSSE(res, {
      onToken(data) {
        fullContent += data.content || ''
        const aiMsg = messages.value.find(m => m.id === aiId)
        if (aiMsg) {
          aiMsg.content = fullContent
          aiMsg.isStreaming = true
        }
        scrollToBottom()
      },
      onImageIntent(data) {
        const aiMsg = messages.value.find(m => m.id === aiId)
        if (aiMsg) aiMsg.imageProgress = data.message || '正在生成图片...'
        scrollToBottom()
      },
      onImageProgress(data) {
        const aiMsg = messages.value.find(m => m.id === aiId)
        if (aiMsg) aiMsg.imageProgress = data.message || data.status || '生成中...'
      },
      onImageResult(data) {
        const aiMsg = messages.value.find(m => m.id === aiId)
        if (aiMsg) {
          aiMsg.imageUrl = data.imageUrl
          aiMsg.imageProgress = undefined
        }
        scrollToBottom()
      },
      onDone(data) {
        const aiMsg = messages.value.find(m => m.id === aiId)
        if (aiMsg) {
          aiMsg.isStreaming = false
          aiMsg.messageId = data.messageId
        }
        if (data.contextId) {
          sessionId.value = data.contextId
          sessionStore.loadSessions()
        }
        loading.value = false
        scrollToBottom()
      },
      onError(data) {
        const aiMsg = messages.value.find(m => m.id === aiId)
        if (aiMsg) {
          aiMsg.isStreaming = false
          aiMsg.content = `错误: ${data.message || '未知错误'}`
        }
        loading.value = false
      },
    })
  } catch (e: any) {
    const aiMsg = messages.value.find(m => m.id === aiId)
    if (aiMsg) {
      aiMsg.isStreaming = false
      aiMsg.content = `发送失败: ${e.message}`
    }
    loading.value = false
  }
}

async function regenerateMessage(m: Message) {
  if (!m.messageId) return
  loading.value = true
  const aiId = `${Date.now()}-a`
  const idx = messages.value.findIndex(msg => msg.id === m.id)
  if (idx !== -1) {
    messages.value.splice(idx + 1)
    messages.value.push({ id: aiId, role: 'assistant', content: '', isStreaming: true })
  }
  scrollToBottom()

  try {
    const res = await chatApi.streamRegenerate(m.messageId)
    let fullContent = ''
    await readSSE(res, {
      onToken(data) {
        fullContent += data.content || ''
        const aiMsg = messages.value.find(msg => msg.id === aiId)
        if (aiMsg) { aiMsg.content = fullContent; aiMsg.isStreaming = true }
        scrollToBottom()
      },
      onDone(data) {
        const aiMsg = messages.value.find(msg => msg.id === aiId)
        if (aiMsg) { aiMsg.isStreaming = false; aiMsg.messageId = data.messageId }
        loading.value = false
        scrollToBottom()
      },
      onError(data) {
        const aiMsg = messages.value.find(msg => msg.id === aiId)
        if (aiMsg) { aiMsg.isStreaming = false; aiMsg.content = `错误: ${data.message}` }
        loading.value = false
      },
    })
  } catch (e: any) {
    const aiMsg = messages.value.find(msg => msg.id === aiId)
    if (aiMsg) { aiMsg.isStreaming = false; aiMsg.content = `重新生成失败: ${e.message}` }
    loading.value = false
  }
}

async function exportTravel(m: Message) {
  if (!sessionId.value) return
  try {
    const res = await travelApi.exportTravel(sessionId.value, 'pdf')
    const blob = new Blob([res.data as any], { type: 'application/pdf' })
    downloadBlob(blob, `${m.content.slice(0, 20) || 'travel'}.pdf`)
  } catch (e) {
    console.error('导出失败:', e)
  }
}

function openShare(type: 'travel' | 'image', id: string) {
  shareType.value = type
  shareContentId.value = id
  shareVisible.value = true
}

async function favoriteImage(m: Message) {
  if (!m.imageUrl) return
  try {
    await imageApi.addFavorite({
      imageUrl: m.imageUrl,
      prompt: m.content,
    })
    alert('已收藏')
  } catch (e: any) {
    alert('收藏失败: ' + (e.response?.data?.detail || e.message))
  }
}

onMounted(() => {
  if (sessionId.value) loadSession(sessionId.value)
})
</script>