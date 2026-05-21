<template>
  <div class="flex flex-col h-full bg-gradient-to-b from-gray-50 to-white dark:from-slate-900 dark:to-slate-800">
    <!-- 消息列表 -->
    <div ref="messageContainer" class="flex-1 overflow-y-auto px-4 py-6 space-y-4">
      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center px-6">
        <div class="relative mb-6">
          <div class="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-emerald-100 to-emerald-200 dark:from-emerald-900/40 dark:to-emerald-800/30 rounded-2xl shadow-inner">
            <svg class="w-10 h-10 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
            </svg>
          </div>
        </div>
        <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-2">AI 旅游攻略</h2>
        <p class="text-gray-500 dark:text-gray-400 max-w-md mb-8">输入目的地，获取详细的旅行攻略和精美海报</p>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-lg">
          <button @click="quickSelect('杭州', 3, '经典游，美食')" class="p-4 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:shadow-md hover:border-emerald-300 dark:hover:border-emerald-700 transition-all text-left group">
            <span class="text-2xl mb-1 block">🏯</span>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-emerald-600">杭州3日游</span>
          </button>
          <button @click="quickSelect('成都', 4, '美食，休闲')" class="p-4 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:shadow-md hover:border-emerald-300 dark:hover:border-emerald-700 transition-all text-left group">
            <span class="text-2xl mb-1 block">🐼</span>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-emerald-600">成都4日游</span>
          </button>
          <button @click="quickSelect('大理', 5, '情侣游，自然风光')" class="p-4 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:shadow-md hover:border-emerald-300 dark:hover:border-emerald-700 transition-all text-left group">
            <span class="text-2xl mb-1 block">🌊</span>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-emerald-600">大理5日游</span>
          </button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-for="msg in messages" :key="msg.id" class="flex gap-3 animate-slide-in" :class="{ 'flex-row-reverse': msg.role === 'user' }">
        <!-- 头像 -->
        <div class="flex items-center justify-center flex-shrink-0 w-9 h-9 rounded-full shadow-sm mt-1"
          :class="msg.role === 'user' ? 'bg-emerald-500' : 'bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600'">
          <svg v-if="msg.role === 'user'" class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM12 14a7 7 0 0 0-7 7h14a7 7 0 0 0-7-7z"/>
          </svg>
          <svg v-else class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
          </svg>
        </div>

        <!-- 消息内容 -->
        <div class="max-w-[80%] min-w-0">
          <div class="px-4 py-3 rounded-2xl shadow-sm"
            :class="msg.role === 'user'
              ? 'bg-emerald-500 text-white rounded-tr-sm'
              : 'bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-200 border border-gray-100 dark:border-slate-700/70 rounded-tl-sm'">
            <!-- 用户消息纯文本 -->
            <p v-if="msg.role === 'user'" class="whitespace-pre-wrap text-sm">{{ msg.content }}</p>
            <!-- AI 消息：错误卡片 -->
            <div v-else-if="msg.error" class="flex items-start gap-3">
              <div class="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-red-700 dark:text-red-400">生成失败</p>
                <p class="text-xs text-red-500/70 dark:text-red-400/60 mt-1 leading-relaxed">{{ msg.content }}</p>
              </div>
            </div>
            <!-- AI 消息 Markdown（正常内容） -->
            <div v-else class="prose prose-sm dark:prose-invert max-w-none prose-headings:text-gray-800 dark:prose-headings:text-gray-100 prose-a:text-emerald-600">
              <MarkdownRenderer :content="msg.content" />
            </div>
          </div>

          <!-- 🎯 旅行加载动画（趣味等待） -->
          <div v-if="msg.loading" class="mt-3 px-1 animate-slide-in">
            <div class="relative overflow-hidden rounded-xl bg-gradient-to-br from-emerald-50 via-white to-emerald-50/30 dark:from-emerald-900/15 dark:via-slate-800 dark:to-emerald-900/5 border border-emerald-200/60 dark:border-emerald-700/30 shadow-sm">
              <!-- 流光背景 -->
              <div class="absolute inset-0 bg-gradient-animate opacity-40 dark:opacity-20"></div>
              <div class="relative p-3 flex items-center gap-3">
                <!-- 左侧动画图标组 -->
                <div class="relative w-11 h-11 flex items-center justify-center shrink-0">
                  <!-- 地图定位针 -->
                  <svg class="absolute w-6 h-6 text-emerald-400 animate-map-pin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                    <circle cx="12" cy="10" r="3" fill="currentColor" class="opacity-60"/>
                  </svg>
                  <!-- 旋转罗盘 -->
                  <svg class="absolute w-9 h-9 text-emerald-400/60 animate-spin-slow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="12" cy="12" r="10" stroke-dasharray="31.4 31.4" class="opacity-20" />
                    <path d="M12 2 L12 6 M12 18 L12 22 M2 12 L6 12 M18 12 L22 12" stroke-width="2" class="opacity-30" />
                    <polygon points="12,4 14,12 12,14 10,12" fill="currentColor" class="origin-center animate-compass" />
                  </svg>
                  <!-- 纸飞机 -->
                  <svg class="absolute w-4 h-4 text-emerald-500 -top-0.5 -right-0.5 animate-plane" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21 3L3 10.5L11 13L13.5 21L21 3Z" />
                  </svg>
                </div>
                <!-- 右侧动态文字 -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-1.5">
                    <span class="text-sm font-semibold text-emerald-600 dark:text-emerald-400">AI 旅行规划师</span>
                    <span class="flex gap-1">
                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style="animation-delay:0s" />
                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style="animation-delay:0.15s" />
                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style="animation-delay:0.3s" />
                    </span>
                  </div>
                  <p class="text-xs text-emerald-500/70 dark:text-emerald-400/60 mt-0.5 animate-thinking-text">{{ loadingText }}</p>
                  <!-- 微型进度条 -->
                  <div class="mt-1.5 h-0.5 bg-emerald-200/40 dark:bg-emerald-700/30 rounded-full overflow-hidden">
                    <div class="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full animate-loading-bar"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 图片加载占位（趣味动画） -->
          <div v-if="msg.imageLoading" class="mt-3 animate-slide-in">
            <div class="w-full rounded-xl overflow-hidden border border-gray-200 dark:border-slate-700 shadow-sm">
              <div class="aspect-video relative bg-gradient-to-br from-emerald-100 via-emerald-50 to-teal-100 dark:from-emerald-900/30 dark:via-slate-800 dark:to-teal-900/20 flex flex-col items-center justify-center gap-3 overflow-hidden">
                <!-- 脉冲环 -->
                <div class="absolute inset-0">
                  <div class="absolute inset-0 animate-ping-slow rounded-full bg-emerald-400/5 dark:bg-emerald-500/5" style="top:30%; left:30%; width:40%; height:40%"></div>
                  <div class="absolute inset-0 animate-ping-slower rounded-full bg-emerald-400/5 dark:bg-emerald-500/5" style="top:20%; left:20%; width:60%; height:60%"></div>
                </div>
                <!-- 图标组 -->
                <div class="relative flex items-center gap-4">
                  <svg class="w-7 h-7 text-emerald-400/70 animate-float" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.41a2.25 2.25 0 013.182 0l2.909 2.91m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"/>
                  </svg>
                  <svg class="w-7 h-7 text-emerald-400/50 animate-float-delayed" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"/>
                  </svg>
                  <svg class="w-7 h-7 text-emerald-400/60 animate-float" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 20.25h12m-7.5-3v3m3-3v3m-10.125-3h17.25c.621 0 1.125-.504 1.125-1.125V4.875c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125z"/>
                  </svg>
                </div>
                <!-- 文字 -->
                <div class="relative text-center">
                  <div class="flex items-center justify-center gap-2">
                    <svg class="w-4 h-4 text-emerald-500 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                    </svg>
                    <span class="text-sm font-medium text-emerald-600/70 dark:text-emerald-400/70">正在绘制精美海报...</span>
                  </div>
                </div>
                <!-- 底部的渐变流光条 -->
                <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-emerald-400/60 to-transparent animate-shimmer-line"></div>
              </div>
            </div>
          </div>

          <!-- 生成的图片（缩略图） -->
          <div v-if="msg.imageUrl" class="mt-3">
            <div class="relative group inline-block cursor-pointer max-w-[220px]" @click="openPreview(msg.imageUrl!)">
              <img :src="msg.imageUrl" alt="目的地海报" class="w-full rounded-lg shadow-md border border-gray-200 dark:border-slate-700 hover:opacity-90 transition-opacity" />
              <!-- 悬停遮罩 -->
              <div class="absolute inset-0 rounded-lg bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                <svg class="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- 图片生成失败提示 -->
          <div v-if="msg.imageError" class="mt-3 animate-slide-in">
            <div class="rounded-xl border border-amber-200/70 dark:border-amber-700/30 bg-amber-50/60 dark:bg-amber-900/10 p-3 flex items-center gap-2.5">
              <div class="flex-shrink-0 w-7 h-7 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <p class="text-xs text-amber-600/80 dark:text-amber-400/70">海报生成失败，攻略文本已可用</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── 大图预览模态框 ── -->
    <div v-if="previewImageUrl" class="fixed inset-0 z-[9999] bg-black/70 dark:bg-black/80 flex items-center justify-center p-4 md:p-8 backdrop-blur-sm" @click="closePreview">
      <div class="relative max-w-5xl max-h-[90vh] w-full flex flex-col items-center" @click.stop>
        <!-- 关闭按钮 -->
        <button @click="closePreview" class="absolute -top-10 right-0 text-white/80 hover:text-white transition-colors p-1">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
        <!-- 大图 -->
        <img :src="previewImageUrl" alt="目的地海报大图" class="max-w-full max-h-[80vh] rounded-xl shadow-2xl" />
        <!-- 操作栏 -->
        <div class="flex items-center gap-3 mt-4">
          <button @click="downloadImage(previewImageUrl)" class="inline-flex items-center gap-2 px-5 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium transition-all backdrop-blur-sm border border-white/20 hover:border-white/40">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            下载海报
          </button>
        </div>
      </div>
    </div>

    <!-- 底部输入区 -->
    <div class="border-t border-gray-100 dark:border-slate-700/50 bg-white dark:bg-slate-800/80 backdrop-blur-sm">
      <div class="max-w-3xl mx-auto px-4 py-3">
        <div class="flex gap-2 items-end">
          <div class="flex-1 relative">
            <textarea
              v-model="inputText"
              @keydown.enter.exact="handleSend"
              placeholder="输入目的地，如「杭州3日游攻略」"
              rows="2"
              class="w-full px-4 py-3 text-sm text-gray-800 dark:text-gray-200 placeholder-gray-400 bg-gray-50 dark:bg-slate-700/60 border border-gray-200 dark:border-slate-600 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-400 dark:focus:border-emerald-500 transition-all"
              :disabled="isLoading"
            />
          </div>
          <button
            @click="handleSend"
            :disabled="!inputText.trim() || isLoading"
            class="px-5 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 disabled:from-gray-300 disabled:to-gray-300 dark:disabled:from-slate-600 dark:disabled:to-slate-600 disabled:cursor-not-allowed text-white rounded-2xl font-medium transition-all duration-200 hover:shadow-lg hover:shadow-emerald-200/50 dark:hover:shadow-emerald-900/30 flex items-center gap-2 active:scale-95"
          >
            <svg v-if="isLoading" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
            </svg>
          </button>
        </div>
        <p class="text-[11px] text-gray-400 dark:text-slate-500 mt-1.5 text-center">
          AI 生成仅供参考 · 出行前请核实最新信息
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import { apiService } from '@/services/api'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  imageUrl?: string
  loading?: boolean
  imageLoading?: boolean
  error?: boolean
  imageError?: boolean
}

const messages = ref<ChatMessage[]>([])
const inputText = ref('')
const isLoading = ref(false)
const messageContainer = ref<HTMLElement | null>(null)

// ── 大图预览 ──
const previewImageUrl = ref<string | null>(null)

function openPreview(url: string) {
  previewImageUrl.value = url
  document.body.style.overflow = 'hidden'
}

function closePreview() {
  previewImageUrl.value = null
  document.body.style.overflow = ''
}

function downloadImage(url: string) {
  const link = document.createElement('a')
  link.href = url
  link.download = `旅行海报-${Date.now()}.png`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// ── 加载时循环显示的趣味文案 ──
const loadingTexts = [
  '🧭 在地图上寻找方向...',
  '🍜 搜索当地美食中...',
  '✈️ 规划最优路线中...',
  '🏨 筛选特色住宿...',
  '🎯 挖掘隐藏宝藏景点...',
  '🌤️ 查询天气预报...',
  '📸 寻找最佳拍照点...',
  '🎒 打包行李建议中...',
  '🚗 研究交通方式...',
  '💡 获取本地人推荐...',
]
const loadingText = ref('🧭 在地图上寻找方向...')
let loadingTextTimer: ReturnType<typeof setInterval> | null = null

function startLoadingText() {
  let i = 0
  loadingText.value = loadingTexts[0]
  loadingTextTimer = setInterval(() => {
    i = (i + 1) % loadingTexts.length
    loadingText.value = loadingTexts[i]
  }, 2500)
}

function stopLoadingText() {
  if (loadingTextTimer) {
    clearInterval(loadingTextTimer)
    loadingTextTimer = null
  }
}

function addMessage(msg: ChatMessage) {
  messages.value.push(msg)
}

function scrollToBottom() {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}

watch(() => messages.value.length, scrollToBottom)
watch(messages, scrollToBottom, { deep: true })

// ── 从历史记录恢复对话 ──
const route = useRoute()

onMounted(async () => {
  const itemsParam = route.query.historyItems as string
  if (!itemsParam) return

  try {
    const items: { type: string; rawId: string }[] = JSON.parse(decodeURIComponent(itemsParam))
    const restored: ChatMessage[] = []
    let msgId = 0

    for (const item of items) {
      if (item.type === 'chat') {
        try {
          const detail: any = await apiService.getChatHistoryDetail(item.rawId)
          // 用户消息
          restored.push({
            id: `hist-user-${msgId++}`,
            role: 'user',
            content: detail.userMessage || '',
            timestamp: new Date(detail.createdAt).getTime(),
          })
          // AI 回复 — 解析攻略内容和图片URL
          const aiReply = detail.aiReply || ''
          const imgMatch = aiReply.match(/!\[.*?\]\((.*?)\)/)
          const imageUrl = imgMatch ? imgMatch[1] : undefined
          const content = imgMatch ? aiReply.replace(/\n\n!\[.*?\]\(.*?\)$/, '') : aiReply
          restored.push({
            id: `hist-ai-${msgId++}`,
            role: 'assistant',
            content,
            timestamp: new Date(detail.createdAt).getTime(),
            imageUrl: imageUrl || undefined,
          })
        } catch (e) {
          console.warn('恢复历史记录失败:', item.rawId, e)
        }
      }
    }

    if (restored.length > 0) {
      messages.value = restored
    }
  } catch (e) {
    console.warn('解析 historyItems 失败:', e)
  }

  // 清除 URL 中的查询参数，避免刷新后重复恢复
  window.history.replaceState({}, '', '/app')
})

function parseInput(text: string): { destination: string; days: number; preferences: string } {
  // 尝试从用户输入中提取天数和目的地
  const dayMatch = text.match(/(\d+)\s*天/)
  const days = dayMatch ? parseInt(dayMatch[1]) : 3
  
  // 移除天数字样，剩下的作为目的地+偏好
  let rest = text.replace(/\d+\s*天/, '').trim()
  // 如果包含常见关键词，提取偏好
  const prefKeywords = ['情侣', '亲子', '穷游', '美食', '自驾', '休闲', '自然', '文化', '历史', '购物', '蜜月', '独旅']
  const foundPrefs = prefKeywords.filter(k => rest.includes(k))
  
  // 去除偏好关键词后的剩余作为目的地
  let destination = rest
  for (const k of foundPrefs) {
    destination = destination.replace(k, '')
  }
  destination = destination.replace(/旅游|攻略|去|到|玩|求/g, '').trim()
  
  return {
    destination: destination || text,
    days,
    preferences: foundPrefs.join('，'),
  }
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return
  inputText.value = ''
  
  const { destination, days, preferences } = parseInput(text)
  
  // 添加用户消息
  const userMsg: ChatMessage = {
    id: `user-${Date.now()}`,
    role: 'user',
    content: text,
    timestamp: Date.now(),
  }
  addMessage(userMsg)
  
  // 添加 AI 占位消息 — 显示趣味加载动画
  const aiMsg: ChatMessage = {
    id: `ai-${Date.now()}`,
    role: 'assistant',
    content: '',
    timestamp: Date.now(),
    loading: true,     // 🎯 设为 true 触发加载动画
  }
  addMessage(aiMsg)
  isLoading.value = true
  startLoadingText()
  let hasStartedStreaming = false  // 标记是否已经开始流式传输

  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch('/api/travel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ destination, days, preferences }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''  // 保留未完成的行

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const event = JSON.parse(line.slice(6))
          
          switch (event.type) {
            case 'token':
              // 🎯 第一个 token 到达 → 关闭加载动画，显示流式内容
              if (!hasStartedStreaming) {
                hasStartedStreaming = true
                aiMsg.loading = false
                stopLoadingText()
              }
              aiMsg.content += event.data.content
              messages.value = [...messages.value]
              scrollToBottom()
              break

            case 'text_done':
              // 文本已全部接收
              aiMsg.loading = false
              messages.value = [...messages.value]
              break

            case 'image_loading':
              // 图片正在生成，显示 loading 占位
              aiMsg.imageLoading = true
              messages.value = [...messages.value]
              scrollToBottom()
              break

            case 'image':
              aiMsg.imageLoading = false
              if (event.data.url) {
                aiMsg.imageUrl = event.data.url
              } else {
                aiMsg.imageError = true
              }
              messages.value = [...messages.value]
              break

            case 'done':
              isLoading.value = false
              scrollToBottom()
              break

            case 'error':
              aiMsg.loading = false
              aiMsg.error = true
              aiMsg.content = event.data.message || '生成失败，请稍后重试'
              messages.value = [...messages.value]
              stopLoadingText()
              break
          }
        } catch (e) {
          // 忽略解析错误
          continue
        }
      }
    }
  } catch (e: any) {
    aiMsg.loading = false
    aiMsg.error = true
    aiMsg.content = e.message || '生成失败，请稍后重试'
    messages.value = [...messages.value]
    stopLoadingText()
  } finally {
    isLoading.value = false
    stopLoadingText()
  }
}

function quickSelect(destination: string, days: number, preferences: string) {
  inputText.value = `${destination}${days}日游${preferences ? '，' + preferences : ''}`
  handleSend()
}
</script>
