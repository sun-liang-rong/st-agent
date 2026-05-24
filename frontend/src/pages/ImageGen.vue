<template>
  <AppPage>
    <div class="max-w-5xl mx-auto p-4 md:p-6">
      <!-- Header -->
      <div class="text-center mb-6">
        <h1 class="text-2xl font-bold text-amber-900 dark:text-amber-100">🎨 AI 图片生成</h1>
        <p class="text-sm text-amber-500 dark:text-amber-400 mt-1">描述你想要的图片，AI 为你创作</p>
      </div>

      <!-- Style & Ratio -->
      <div class="flex flex-wrap gap-2 mb-4 justify-center">
        <div class="flex items-center gap-1.5 text-sm text-amber-700 dark:text-amber-300 font-medium">风格</div>
        <select v-model="style" class="rounded-xl border-2 border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-3 py-1.5 text-sm text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-400">
          <option value="旅行海报">旅行海报</option>
          <option value="水墨画">水墨画</option>
          <option value="油画">油画</option>
          <option value="水彩画">水彩画</option>
          <option value="像素画">像素画</option>
          <option value="赛博朋克">赛博朋克</option>
          <option value="日系插画">日系插画</option>
          <option value="写实摄影">写实摄影</option>
        </select>
        <div class="flex items-center gap-1.5 text-sm text-amber-700 dark:text-amber-300 font-medium">比例</div>
        <select v-model="ratio" class="rounded-xl border-2 border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-3 py-1.5 text-sm text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-400">
          <option value="1:1">1:1</option>
          <option value="3:4">3:4</option>
          <option value="4:3">4:3</option>
          <option value="16:9">16:9</option>
          <option value="9:16">9:16</option>
        </select>
      </div>

      <!-- Progress -->
      <div v-if="loading && progressMessage" class="mb-4 flex items-center justify-center gap-2 text-sm text-amber-600 dark:text-amber-400">
        <AppSpinner size="sm" />
        <span>{{ progressMessage }}</span>
      </div>

      <!-- Results Grid -->
      <div v-if="messages.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div v-for="m in displayedMessages" :key="m.id" class="group relative bg-white dark:bg-stone-800 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all border border-amber-200 dark:border-stone-700">
          <!-- Image or skeleton -->
          <div v-if="m.imageUrl" :class="skeletonAspectClass" class="overflow-hidden cursor-pointer relative" @click="previewImage(m.imageUrl!)">
            <img :src="m.imageUrl" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" alt="AI 生成图片" />
            <!-- Hover actions -->
            <div class="absolute top-3 right-3 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-all duration-200">
              <button @click.stop="downloadImage(m.imageUrl!)" class="action-btn" title="下载">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              </button>
              <button @click.stop="doFavorite(m)" class="action-btn" title="收藏">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
              </button>
              <button @click.stop="regenerate(m.prompt || '')" class="action-btn" title="重新生成">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
              </button>
              <button @click.stop="openShare(m)" class="action-btn" title="分享">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
              </button>
            </div>
          </div>
          <!-- Loading skeleton -->
          <div v-else-if="m.loading" :class="skeletonAspectClass" class="bg-amber-100 dark:bg-stone-700 animate-pulse flex items-center justify-center">
            <AppSpinner size="lg" />
          </div>
          <!-- Prompt -->
          <div class="p-3">
            <p class="text-sm text-amber-800 dark:text-amber-200 truncate">{{ m.prompt || m.content || '...' }}</p>
            <div v-if="m.aspectRatio" class="flex items-center gap-2 mt-1">
              <span class="text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-stone-700 text-amber-600 dark:text-amber-400">{{ style }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-stone-700 text-amber-600 dark:text-amber-400">{{ m.aspectRatio }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <AppEmpty v-if="messages.length === 0 && !loading" emoji="🎨" title="开始创作" description="输入描述，让 AI 为你生成精美图片" />

      <!-- Input -->
      <div class="fixed bottom-0 left-0 md:left-64 right-0 bg-gradient-to-t from-amber-50 via-amber-50 to-transparent dark:from-stone-900 dark:via-stone-900 pt-6 pb-4 px-4">
        <div class="max-w-5xl mx-auto flex items-end gap-2">
          <div class="flex-1">
            <textarea v-model="input" @keydown.enter.exact="generate" rows="1" class="w-full rounded-xl border-2 border-amber-200 dark:border-stone-600 bg-white dark:bg-stone-800 px-4 py-2.5 text-sm text-amber-900 dark:text-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-400 resize-none" placeholder="描述你想生成的图片..." @input="autoResize"></textarea>
          </div>
          <AppBtn text="生成" :disabled="!input.trim() || loading" :full="false" @click="generate" />
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
import { ref, computed, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { imageApi, chatApi } from '@/services/api'
import { useSessionStore } from '@/stores/session'
import { downloadImage } from '@/composables/useImageDownload'
import { useSSE } from '@/composables/useSSE'
import AppPage from '@/components/AppPage.vue'
import AppEmpty from '@/components/AppEmpty.vue'
import AppSpinner from '@/components/AppSpinner.vue'
import AppBtn from '@/components/AppBtn.vue'
import AppLightbox from '@/components/AppLightbox.vue'
import ShareDialog from '@/components/ShareDialog.vue'

interface ImageMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  imageUrl?: string
  prompt?: string
  aspectRatio?: string
  loading?: boolean
}

const route = useRoute()
const sessionStore = useSessionStore()
const { readSSE } = useSSE()

const input = ref('')
const style = ref('旅行海报')
const ratio = ref('1:1')
const loading = ref(false)
const progressMessage = ref('')
const messages = ref<ImageMessage[]>([])
const sessionId = ref('')
const previewVisible = ref(false)
const previewUrl = ref('')

// Share & Favorite
const shareVisible = ref(false)
const shareType = ref<'travel' | 'image'>('image')
const shareContentId = ref('')

const displayedMessages = computed(() => messages.value.filter(m => m.role === 'assistant'))

const skeletonAspect = computed(() => {
  const map: Record<string, string> = { '1:1': 'aspect-square', '3:4': 'aspect-[3/4]', '4:3': 'aspect-[4/3]', '16:9': 'aspect-video', '9:16': 'aspect-[9/16]' }
  return map[ratio.value] || 'aspect-square'
})

const skeletonAspectClass = computed(() => skeletonAspect.value)

function ratioToAspect(r: string) {
  const map: Record<string, string> = { '1:1': '1:1', '3:4': '3:4', '4:3': '4:3', '16:9': '16:9', '9:16': '9:16' }
  return map[r] || r
}

function autoResize(e: Event) {
  const el = e.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 150) + 'px'
}

function previewImage(url: string) {
  previewUrl.value = url
  previewVisible.value = true
}

function extractImageUrl(text: string): string {
  const match = text.match(/!\[.*?\]\((.*?)\)/) || text.match(/\((\/generated\/[^\s)]+)\)/) || text.match(/(https?:\/\/[^\s)]+\.(png|jpg|jpeg|webp))/i)
  return match ? match[1] : ''
}

async function loadSession(id: string) {
  try {
    const detail: any = await chatApi.getSessionDetail(id)
    const rows = Array.isArray(detail) ? detail : (detail?.data || [])
    messages.value = rows.flatMap((row: any) => {
      const result: ImageMessage[] = []
      const userText = row.userMessage || ''
      result.push({ id: `${row.id}-u`, role: 'user', content: userText })
      const imgUrl = extractImageUrl(row.aiReply || '')
      const imgRatio = row.imageRatio || ''
      if (imgUrl) {
        result.push({ id: `${row.id}-a`, role: 'assistant', content: '', imageUrl: imgUrl, prompt: userText, aspectRatio: ratioToAspect(imgRatio) })
      } else {
        result.push({ id: `${row.id}-a`, role: 'assistant', content: row.aiReply || '' })
      }
      return result
    })
    sessionId.value = id
  } catch (e) {
    console.error('加载会话失败:', e)
  }
}

function generate() {
  const prompt = input.value.trim()
  if (!prompt || loading.value) return

  loading.value = true
  progressMessage.value = '准备中...'

  messages.value.push({ id: `${Date.now()}-u`, role: 'user', content: prompt })
  const aiId = `${Date.now()}-a`
  messages.value.push({ id: aiId, role: 'assistant', content: '', loading: true, prompt, aspectRatio: skeletonAspect.value })
  input.value = ''

  imageApi.streamGenerate(prompt, style.value, ratio.value, sessionId.value || undefined)
    .then(async (response) => {
      if (!response.ok) {
        const aiMsg = messages.value.find(m => m.id === aiId)
        if (aiMsg) { aiMsg.loading = false; aiMsg.content = `生成失败：HTTP ${response.status}` }
        loading.value = false
        return
      }

      await readSSE(response, {
        onImageProgress(data) {
          progressMessage.value = data.message || data.status || '生成中...'
        },
        onImageResult(data) {
          const aiMsg = messages.value.find(m => m.id === aiId)
          if (aiMsg) {
            aiMsg.loading = false
            if (data.imageUrl) aiMsg.imageUrl = data.imageUrl
            aiMsg.aspectRatio = ratioToAspect(data.imageRatio || ratio.value)
          }
          if (data.contextId) sessionId.value = data.contextId
          loading.value = false
          sessionStore.loadSessions()
        },
        onDone(data) {
          const aiMsg = messages.value.find(m => m.id === aiId)
          if (aiMsg && !aiMsg.imageUrl) {
            aiMsg.loading = false
            if (data.imageUrl) aiMsg.imageUrl = data.imageUrl
          }
          if (data.contextId) sessionId.value = data.contextId
          loading.value = false
          sessionStore.loadSessions()
        },
        onError(data) {
          const aiMsg = messages.value.find(m => m.id === aiId)
          if (aiMsg) { aiMsg.loading = false; aiMsg.content = `生成失败：${data.message || '未知错误'}` }
          loading.value = false
        },
      })
    })
    .catch((e) => {
      const aiMsg = messages.value.find(m => m.id === aiId)
      if (aiMsg) { aiMsg.loading = false; aiMsg.content = `生成失败：${e.message}` }
      loading.value = false
    })
}

function regenerate(prompt: string) {
  input.value = prompt
  generate()
}

function openShare(m: ImageMessage) {
  shareType.value = 'image'
  shareContentId.value = m.id
  shareVisible.value = true
}

async function doFavorite(m: ImageMessage) {
  if (!m.imageUrl) return
  try {
    await imageApi.addFavorite({
      imageUrl: m.imageUrl,
      prompt: m.prompt || m.content,
      style: style.value,
      ratio: ratio.value,
    })
    alert('已收藏')
  } catch (e: any) {
    alert('收藏失败: ' + (e.response?.data?.detail || e.message))
  }
}

// Load session from route
watch(() => route.query.session as string, (id) => {
  if (id) loadSession(id)
}, { immediate: true })
</script>

<style scoped>
.action-btn {
  @apply w-8 h-8 rounded-full bg-white/90 dark:bg-stone-800/90 text-amber-700 dark:text-amber-300 hover:bg-amber-50 dark:hover:bg-stone-700 flex items-center justify-center shadow-sm transition-colors;
}
</style>