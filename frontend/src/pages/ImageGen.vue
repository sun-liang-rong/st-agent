<template>
  <div class="flex flex-col h-full bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-stone-900 dark:via-stone-800 dark:to-stone-900">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-amber-200 dark:border-stone-700">
      <h1 class="text-xl font-bold text-amber-800 dark:text-amber-200">🎨 AI 图片生成</h1>
      <p class="text-sm text-amber-600 dark:text-amber-400 mt-1">输入提示词，让 AI 为你创作</p>
    </div>

    <!-- Content -->
    <div ref="scrollArea" class="flex-1 overflow-y-auto p-6 space-y-4">
      <!-- Empty State -->
      <div v-if="messages.length === 0 && !loading" class="flex flex-col items-center justify-center py-16 text-center">
        <div class="text-5xl mb-4">🎨</div>
        <div class="text-lg font-semibold text-amber-800 dark:text-amber-200 mb-2">输入提示词，生成图片</div>
        <div class="text-sm text-amber-600 dark:text-amber-400">试试描述一个场景，我来帮你画出来</div>
      </div>

      <!-- Message List -->
      <div v-for="m in messages" :key="m.id">
        <!-- User Message Bubble -->
        <div v-if="m.role === 'user'" class="flex gap-3 items-start justify-end">
          <div class="text-right">
            <div class="bg-gradient-to-r from-amber-500 to-red-500 text-white rounded-tr-sm rounded-tl-xl rounded-bl-xl rounded-br-xl px-4 py-3 shadow-md max-w-[75%] inline-block">
              <p class="whitespace-pre-wrap text-sm">{{ m.content }}</p>
            </div>
          </div>
          <div class="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-lg shadow-md flex-shrink-0">😊</div>
        </div>

        <!-- AI Image Response -->
        <div v-else class="flex gap-3 items-start">
          <div class="w-9 h-9 rounded-full bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center text-lg shadow-md flex-shrink-0">🤖</div>
          <div>
            <!-- Skeleton (loading) -->
            <div v-if="m.loading" class="skeleton-image-card bg-white dark:bg-stone-800 border-2 border-dashed border-amber-300 dark:border-stone-600 rounded-2xl overflow-hidden max-w-[280px]" :style="{ aspectRatio: skeletonAspect }">
              <div class="skeleton-shimmer-layer"></div>
              <div class="skeleton-particles">
                <span v-for="i in 6" :key="i" class="particle" :style="particleStyle(i)"></span>
              </div>
              <div class="skeleton-center">
                <div class="brush-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18.37 2.63a2.12 2.12 0 0 1 3 3L14 13l-4 1 1-4Z"/><path d="M9 15c-3 1-5.5 3-5.5 3s2-2.5 3-5.5"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="M2 12h2"/><path d="M20 12h2"/></svg>
                </div>
                <p class="progress-text">{{ progressMessage }}</p>
                <div class="progress-dots"><span></span><span></span><span></span></div>
              </div>
            </div>
            <!-- Image Card (completed) -->
            <div v-else-if="m.imageUrl" class="max-w-[280px] rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-200 group cursor-pointer" @click="previewImage(m.imageUrl)">
              <div class="relative">
                <img :src="m.imageUrl" class="w-full object-cover rounded-2xl" :style="{ aspectRatio: skeletonAspect }" alt="generated" />
                <!-- Overlay Actions -->
                <div class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all duration-200 rounded-2xl"></div>
                <div class="absolute top-3 right-3 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-all duration-200">
                  <button @click.stop="downloadImage(m.imageUrl)" class="action-btn" title="下载">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  </button>
                  <button @click.stop="regenerate(m.prompt)" class="action-btn" title="重新生成">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
                  </button>
                </div>
                <!-- Click hint -->
                <div class="absolute bottom-3 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200">
                  <span class="bg-black/50 text-white text-xs px-2 py-1 rounded-full">点击查看大图</span>
                </div>
              </div>
            </div>
            <!-- Error -->
            <div v-else-if="m.content" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-4 py-3 text-sm text-red-600 dark:text-red-400 max-w-[280px]">
              {{ m.content }}
            </div>
          </div>
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

    <!-- Input Area -->
    <div class="p-4 border-t border-amber-200 dark:border-stone-700">
      <!-- Prompt Inspiration -->
      <div v-if="messages.length === 0 && !loading" class="flex gap-2 flex-wrap mb-3 max-w-3xl mx-auto">
        <span class="text-xs text-amber-600 dark:text-amber-400 self-center">💡 试试：</span>
        <button @click="fillPrompt('日落下的古镇，水墨画风格')" class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-3 py-1.5 text-xs text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">🌅 日落古镇</button>
        <button @click="fillPrompt('雪山湖泊倒影，写实摄影')" class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-3 py-1.5 text-xs text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">🏔️ 雪山湖泊</button>
        <button @click="fillPrompt('樱花小径，日系插画')" class="bg-white dark:bg-stone-800 border-2 border-amber-300 dark:border-stone-600 rounded-full px-3 py-1.5 text-xs text-amber-800 dark:text-amber-200 hover:-translate-y-0.5 hover:shadow-md transition-all">🌸 樱花小径</button>
      </div>
      <div class="max-w-3xl mx-auto">
        <div class="relative border-2 border-amber-300 dark:border-stone-600 bg-white dark:bg-stone-800 rounded-2xl focus-within:ring-2 focus-within:ring-amber-400 focus-within:border-transparent">
          <!-- Textarea -->
          <textarea
            v-model="input"
            @keydown.enter.ctrl="generate"
            :disabled="loading"
            placeholder="描述你想要的图片..."
            rows="2"
            class="w-full bg-transparent px-4 py-3 pb-8 text-sm text-amber-900 dark:text-amber-100 placeholder-amber-400 dark:placeholder-stone-500 focus:outline-none resize-none disabled:opacity-50"
          ></textarea>
          <!-- Bottom Bar: Style + Ratio + Send -->
          <div class="flex items-center justify-between px-3 pb-2.5">
            <div class="flex items-center gap-2">
              <!-- Style Selector -->
              <div class="relative">
                <button
                  ref="styleBtnRef"
                  @click="showStyleDropdown ? (showStyleDropdown = false) : openStyleDropdown()"
                  :disabled="loading"
                  class="style-trigger flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-amber-50 dark:bg-stone-700 text-amber-800 dark:text-amber-200 hover:bg-amber-100 dark:hover:bg-stone-600 transition-colors border border-amber-200 dark:border-stone-600"
                >
                  {{ currentStyleLabel }}
                  <svg class="w-3 h-3 text-amber-400 dark:text-stone-400 transition-transform duration-200" :class="showStyleDropdown ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                </button>
                <Teleport to="body">
                  <transition
                    enter-active-class="transition duration-200 ease-out"
                    enter-from-class="opacity-0 -translate-y-1"
                    enter-to-class="opacity-100 translate-y-0"
                    leave-active-class="transition duration-150 ease-in"
                    leave-from-class="opacity-100 translate-y-0"
                    leave-to-class="opacity-0 -translate-y-1"
                  >
                    <div v-if="showStyleDropdown" :style="styleDropdownPos" class="fixed bg-white dark:bg-stone-800 rounded-lg shadow-lg border border-amber-100 dark:border-stone-600 w-[200px] py-1 origin-top-left" style="z-index: 9999">
                      <div class="h-[80px] overflow-y-auto">
                        <button
                          v-for="s in styleOptions"
                          :key="s.value"
                          @mousedown.prevent="style = s.value; showStyleDropdown = false"
                          class="w-full text-left px-3 py-1.5 text-xs transition-colors cursor-pointer"
                          :class="style === s.value ? 'bg-amber-50 dark:bg-stone-600 text-amber-900 dark:text-amber-100 font-medium' : 'text-amber-700 dark:text-amber-300 hover:bg-amber-50/60 dark:hover:bg-stone-700'"
                        >{{ s.label }}</button>
                      </div>
                    </div>
                  </transition>
                </Teleport>
              </div>
              <!-- Ratio Selector -->
              <div class="relative">
                <button
                  ref="ratioBtnRef"
                  @click="showRatioDropdown ? (showRatioDropdown = false) : openRatioDropdown()"
                  :disabled="loading"
                  class="ratio-trigger flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-amber-50 dark:bg-stone-700 text-amber-800 dark:text-amber-200 hover:bg-amber-100 dark:hover:bg-stone-600 transition-colors border border-amber-200 dark:border-stone-600"
                >
                  {{ ratio }}
                  <svg class="w-3 h-3 text-amber-400 dark:text-stone-400 transition-transform duration-200" :class="showRatioDropdown ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
                </button>
                <Teleport to="body">
                  <transition
                    enter-active-class="transition duration-200 ease-out"
                    enter-from-class="opacity-0 -translate-y-1"
                    enter-to-class="opacity-100 translate-y-0"
                    leave-active-class="transition duration-150 ease-in"
                    leave-from-class="opacity-100 translate-y-0"
                    leave-to-class="opacity-0 -translate-y-1"
                  >
                    <div v-if="showRatioDropdown" :style="ratioDropdownPos" class="fixed bg-white dark:bg-stone-800 rounded-lg shadow-lg border border-amber-100 dark:border-stone-600 w-[200px] py-1 origin-top-left" style="z-index: 9999">
                      <div class="h-[80px] overflow-y-auto">
                        <button
                          v-for="r in ratioOptions"
                          :key="r.value"
                          @mousedown.prevent="ratio = r.value; showRatioDropdown = false"
                          class="w-full text-left px-3 py-1.5 text-xs transition-colors cursor-pointer"
                          :class="ratio === r.value ? 'bg-amber-50 dark:bg-stone-600 text-amber-900 dark:text-amber-100 font-medium' : 'text-amber-700 dark:text-amber-300 hover:bg-amber-50/60 dark:hover:bg-stone-700'"
                        >{{ r.label }}</button>
                      </div>
                    </div>
                  </transition>
                </Teleport>
              </div>
            </div>
            <!-- Send Button (icon, only visible when input has content) -->
            <button
              v-show="input.trim()"
              @click="generate"
              :disabled="loading"
              class="w-8 h-8 rounded-lg bg-gradient-to-r from-amber-500 to-red-500 hover:from-amber-600 hover:to-red-600 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center justify-center"
            >
              <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { apiService } from '../services/api'

const input = ref('')
const loading = ref(false)
const progressStep = ref(0)
const progressMessage = ref('准备中...')
const ratio = ref('1:1')
const style = ref('旅行海报')

const styleOptions = [
  { value: '旅行海报', label: '旅行海报' },
  { value: '水墨画', label: '水墨画' },
  { value: '油画', label: '油画' },
  { value: '水彩画', label: '水彩画' },
  { value: '像素画', label: '像素画' },
  { value: '赛博朋克', label: '赛博朋克' },
  { value: '日系插画', label: '日系插画' },
  { value: '写实摄影', label: '写实摄影' },
]

const ratioOptions = [
  { value: '1:1', label: '1:1' },
  { value: '2:3', label: '2:3' },
  { value: '3:2', label: '3:2' },
  { value: '3:4', label: '3:4' },
  { value: '4:3', label: '4:3' },
  { value: '4:5', label: '4:5' },
  { value: '5:4', label: '5:4' },
  { value: '9:16', label: '9:16' },
  { value: '16:9', label: '16:9' },
  { value: '9:21', label: '9:21' },
  { value: '21:9', label: '21:9' },
]

const currentStyleLabel = computed(() => {
  const found = styleOptions.find(s => s.value === style.value)
  return found ? found.label : '风格'
})

const ratioMap: Record<string, string> = {
  '1:1': '1/1', '2:3': '2/3', '3:2': '3/2', '3:4': '3/4', '4:3': '4/3',
  '4:5': '4/5', '5:4': '5/4', '9:16': '9/16', '16:9': '16/9', '9:21': '9/21', '21:9': '21/9',
}
const skeletonAspect = computed(() => ratioMap[ratio.value] || '1/1')

// Dropdown state
const showStyleDropdown = ref(false)
const showRatioDropdown = ref(false)
const styleBtnRef = ref<HTMLElement | null>(null)
const ratioBtnRef = ref<HTMLElement | null>(null)

const styleDropdownPos = computed(() => {
  if (!styleBtnRef.value) return { bottom: '0px', left: '0px' }
  const rect = styleBtnRef.value.getBoundingClientRect()
  return { bottom: `${window.innerHeight - rect.top + 4}px`, left: `${rect.left}px` }
})

const ratioDropdownPos = computed(() => {
  if (!ratioBtnRef.value) return { bottom: '0px', left: '0px' }
  const rect = ratioBtnRef.value.getBoundingClientRect()
  return { bottom: `${window.innerHeight - rect.top + 4}px`, left: `${rect.left}px` }
})

function openStyleDropdown() {
  showStyleDropdown.value = true
  showRatioDropdown.value = false
}

function openRatioDropdown() {
  showRatioDropdown.value = true
  showStyleDropdown.value = false
}

function closeDropdowns(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.style-trigger') && !target.closest('.ratio-trigger')) {
    showStyleDropdown.value = false
    showRatioDropdown.value = false
  }
}

document.addEventListener('mousedown', closeDropdowns)
onBeforeUnmount(() => document.removeEventListener('mousedown', closeDropdowns))

function particleStyle(i: number) {
  const angles = [0, 60, 120, 180, 240, 300]
  const angle = angles[(i - 1) % 6]
  const delay = (i - 1) * 0.4
  const size = 4 + (i % 3) * 2
  return { '--angle': `${angle}deg`, '--delay': `${delay}s`, width: `${size}px`, height: `${size}px` }
}

interface ImageMessage {
  id: string | number
  role: 'user' | 'assistant'
  content: string
  imageUrl?: string
  prompt?: string
  loading?: boolean
}

const messages = ref<ImageMessage[]>([])
const scrollArea = ref<HTMLElement | null>(null)
const previewVisible = ref(false)
const previewUrl = ref('')
const route = useRoute()
const sessionId = ref('')

function extractImageUrl(content: string): string | null {
  const match = content.match(/^\[图片\]\s*(.+)$/s)
  if (!match) return null
  const path = match[1].trim()
  if (path.startsWith('http')) return path
  return '/' + path.replace(/\\/g, '/')
}

async function loadSession(id: string) {
  const res: any = await apiService.getSessionMessages(id)
  const rows = Array.isArray(res) ? res : (res.data || [])
  messages.value = rows.flatMap((row: any) => {
    const result: ImageMessage[] = []
    const userText = row.userMessage || ''
    result.push({ id: `${row.id}-u`, role: 'user', content: userText })
    const imgUrl = extractImageUrl(row.aiReply || '')
    if (imgUrl) {
      result.push({ id: `${row.id}-a`, role: 'assistant', content: '', imageUrl: imgUrl, prompt: userText })
    } else {
      result.push({ id: `${row.id}-a`, role: 'assistant', content: row.aiReply || '' })
    }
    return result
  })
  sessionId.value = id
  scrollToBottom()
}

watch(
  () => route.query.sessionId,
  async (val) => {
    const id = typeof val === 'string' ? val : ''
    if (!id) {
      messages.value = []
      sessionId.value = ''
      return
    }
    await loadSession(id)
  },
  { immediate: true },
)

function previewImage(url: string) {
  previewUrl.value = url
  previewVisible.value = true
}

function scrollToBottom() {
  setTimeout(() => {
    if (scrollArea.value) scrollArea.value.scrollTop = scrollArea.value.scrollHeight
  }, 50)
}

function generate() {
  const prompt = input.value.trim()
  if (!prompt || loading.value) return

  loading.value = true
  progressStep.value = 0
  progressMessage.value = '准备中...'

  messages.value.push({ id: `${Date.now()}-u`, role: 'user', content: prompt })
  const aiId = `${Date.now()}-a`
  messages.value.push({ id: aiId, role: 'assistant', content: '', loading: true, prompt })
  input.value = ''
  scrollToBottom()

  apiService.generateImageStream(
    prompt,
    style.value,
    ratio.value,
    sessionId.value || undefined,
    (step, message) => {
      progressStep.value = step
      progressMessage.value = message
    },
    (imageUrl, contextId) => {
      const aiMsg = messages.value.find(m => m.id === aiId)
      if (aiMsg) {
        aiMsg.loading = false
        aiMsg.imageUrl = imageUrl
        aiMsg.id = contextId || aiId
      }
      if (contextId) sessionId.value = contextId
      scrollToBottom()
    },
    () => {
      loading.value = false
      progressStep.value = 0
      progressMessage.value = ''
    },
    (error) => {
      const aiMsg = messages.value.find(m => m.id === aiId)
      if (aiMsg) {
        aiMsg.loading = false
        aiMsg.content = `生成失败：${error}`
      }
      loading.value = false
      progressStep.value = 0
      progressMessage.value = ''
      console.error('Image generation failed:', error)
    },
  )
}

function downloadImage(url: string) {
  const a = document.createElement('a')
  a.href = url
  a.download = 'ai-generated.png'
  a.click()
}

function regenerate(prompt: string) {
  input.value = prompt
  generate()
}
function fillPrompt(text: string) {
  input.value = text
}
</script>

<style scoped>
/* Skeleton card */
.skeleton-image-card {
  position: relative;
  overflow: hidden;
}

.skeleton-shimmer-layer {
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 30%, rgba(251,191,36,0.12) 50%, transparent 70%);
  background-size: 200% 100%;
  animation: shimmer-slide 1.8s ease-in-out infinite;
}

@keyframes shimmer-slide {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-shimmer {
  animation: shimmer-slide 1.8s ease-in-out infinite;
  background: linear-gradient(110deg, rgba(251,191,36,0.15) 30%, rgba(251,191,36,0.3) 50%, rgba(251,191,36,0.15) 70%);
  background-size: 200% 100%;
}

/* Floating particles */
.skeleton-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  top: 50%;
  left: 50%;
  border-radius: 50%;
  background: rgba(251,191,36,0.5);
  animation: float-particle 3s ease-in-out var(--delay, 0s) infinite;
}

@keyframes float-particle {
  0% {
    transform: translate(-50%, -50%) rotate(var(--angle, 0deg)) translateY(0) scale(1);
    opacity: 0;
  }
  20% { opacity: 0.8; }
  50% {
    transform: translate(-50%, -50%) rotate(var(--angle, 0deg)) translateY(-30px) scale(1.2);
    opacity: 0.6;
  }
  80% { opacity: 0.3; }
  100% {
    transform: translate(-50%, -50%) rotate(var(--angle, 0deg)) translateY(-50px) scale(0.8);
    opacity: 0;
  }
}

/* Center content */
.skeleton-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.brush-icon {
  color: rgba(217,119,6,0.6);
  animation: brush-wobble 2s ease-in-out infinite;
}

@keyframes brush-wobble {
  0%, 100% { transform: rotate(-8deg) scale(1); }
  25% { transform: rotate(8deg) scale(1.05); }
  50% { transform: rotate(-4deg) scale(1); }
  75% { transform: rotate(6deg) scale(1.02); }
}

.progress-text {
  font-size: 12px;
  color: rgba(180,83,9,0.7);
  font-weight: 500;
}

.progress-dots {
  display: flex;
  gap: 4px;
}

.progress-dots span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(217,119,6,0.5);
  animation: dot-bounce 1.4s ease-in-out infinite;
}

.progress-dots span:nth-child(2) { animation-delay: 0.2s; }
.progress-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1.2); opacity: 1; }
}

/* Action buttons */
.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(4px);
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  transition: all 0.2s;
  border: none;
  cursor: pointer;
}

.action-btn:hover {
  background: #fff;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

:root.dark .action-btn {
  background: rgba(55,65,81,0.9);
  color: #e5e7eb;
}

:root.dark .action-btn:hover {
  background: #4b5563;
}
</style>
